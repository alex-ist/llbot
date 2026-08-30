import asyncio
import os
from dataclasses import dataclass
from typing import Any

import librosa
import torch
from huggingface_hub import login as hf_login, snapshot_download

from botlog import logger
from config import required_env
from pron_model import load_backbone, load_conformer_ctc_checkpoint
from pron_scoring import parse_target_transcription, score_pronunciation_alignment
from сtc_alignment import score_target_pronunciation


HEAD_REPO = "istomin9192/ipa-private-v1"
MODEL_REVISION = os.environ.get("HF_MODEL_REVISION", "main")
SR = 16_000
MAX_SAMPLES = 15 * SR
SUBSTITUTION_TARGET_EVIDENCE_THRESHOLD = 0.10

_MODEL = None
_MODEL_LOCK = asyncio.Lock()


@dataclass
class PronunciationAligner:
    feature_extractor: object
    backbone: object
    conformer_head: object
    phone_to_id: dict[str, int]
    id_to_phone: dict[int, str]
    blank_id: int
    backbone_layer: int | None
    device: str


def _load_hf_token() -> str:
    return required_env("HF_TOKEN")


def _ui_display_event(event: dict[str, Any]) -> dict[str, Any]:
    kind_to_status = {
        "heard_target": "matched",
        "heard_substitution": "substitution",
        "missing_target": "deletion",
        "extra_heard": "insertion",
        "accepted_realization": "accepted",
    }
    status = kind_to_status.get(event["kind"], event.get("status", event["kind"]))
    heard_phone = event.get("heard_phone")
    result = {
        "status": status,
        "target_phone": event.get("target_phone"),
        "heard_phone": heard_phone,
        "acoustic_quality": event.get("best_prob") if heard_phone is not None else None,
        "target_quality": event.get("quality"),
    }
    if status == "substitution":
        target_evidence = event.get("target_prob") or 0.0
        target_quality = event.get("quality") or 0.0
        if target_evidence >= SUBSTITUTION_TARGET_EVIDENCE_THRESHOLD:
            target_quality = target_quality + target_evidence * (1.0 - target_quality)
        result["target_quality"] = round(target_quality, 4)
        result["target_evidence"] = round(target_evidence, 4)
    return result


def _format_alignment_text(display_events: list[dict[str, Any]]) -> str:
    items = [_format_alignment_token(event) for event in display_events]
    return "[" + " ".join(items) + "]"


def _format_alignment_token(event: dict[str, Any]) -> str:
    status = event.get("status")
    target_phone = event.get("target_phone")
    heard_phone = event.get("heard_phone")
    if status in {"matched", "accepted"}:
        return heard_phone or target_phone or "?"
    if status == "deletion":
        return f"-{target_phone or '?'}"
    if status == "insertion":
        return f"+{heard_phone or '?'}"
    if status == "substitution":
        return f"{heard_phone or '?'}-{target_phone or '?'}"
    return f"{heard_phone or '?'}-{target_phone or '?'}"


def _format_quality_value(value: Any) -> str:
    if value is None:
        value = 0.0
    text = f"{float(value):.2f}".rstrip("0").rstrip(".")
    return text if "." in text else f"{text}.0"


def _format_alignment_quality_text(display_events: list[dict[str, Any]]) -> str:
    items = []
    for event in display_events:
        quality = event.get("target_quality")
        if quality is None and event.get("status") == "insertion":
            quality = event.get("acoustic_quality")
        items.append(f"{_format_alignment_token(event)}:{_format_quality_value(quality)}")
    return " ".join(items)


def _load_audio(file_name: str):
    wav, _sr = librosa.load(file_name, sr=SR, mono=True)
    return wav[:MAX_SAMPLES]


def _greedy_decode_phones(logits: torch.Tensor, blank_id: int, id_to_phone: dict[int, str]) -> list[str]:
    pred_ids = logits.argmax(dim=-1).detach().cpu().tolist()
    phones = []
    prev_id = None
    for pred_id in pred_ids:
        if pred_id == prev_id:
            continue
        prev_id = pred_id
        if pred_id == blank_id:
            continue
        phone = id_to_phone.get(int(pred_id))
        if phone and phone != "sil":
            phones.append(phone)
    return phones


def _load_model_sync() -> PronunciationAligner:
    hf_token = _load_hf_token()
    if hf_token:
        hf_login(token=hf_token, add_to_git_credential=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"pron_alignment: loading private HF model on {device}")

    repo_dir = snapshot_download(
        repo_id=HEAD_REPO,
        revision=MODEL_REVISION,
        token=hf_token,
    )
    checkpoint_path = os.path.join(repo_dir, "best.pt")

    conformer_head, phone_to_id, ckpt, backbone, feature_extractor = load_conformer_ctc_checkpoint(
        checkpoint_path,
        device=device,
        load_backbone_model=True,
    )
    if backbone is None or feature_extractor is None:
        backbone, feature_extractor = load_backbone(ckpt["backbone_id"], device)

    id_to_phone = {pid: phone for phone, pid in phone_to_id.items()}
    logger.info("pron_alignment: private HF model loaded")
    return PronunciationAligner(
        feature_extractor=feature_extractor,
        backbone=backbone,
        conformer_head=conformer_head,
        phone_to_id=phone_to_id,
        id_to_phone=id_to_phone,
        blank_id=conformer_head.blank_id,
        backbone_layer=ckpt.get("backbone_layer", None),
        device=device,
    )


async def _get_model() -> PronunciationAligner:
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    async with _MODEL_LOCK:
        if _MODEL is None:
            _MODEL = await asyncio.to_thread(_load_model_sync)
    return _MODEL


def _extract_backbone_embeddings(model: PronunciationAligner, wav):
    if hasattr(model.backbone, "extract_frame_embeddings"):
        embeddings = model.backbone.extract_frame_embeddings(
            wav,
            sampling_rate=SR,
            layer=model.backbone_layer,
        )
        embeddings = embeddings if embeddings.ndim == 3 else embeddings.unsqueeze(0)
        return embeddings.to(model.device)

    inputs = model.feature_extractor(wav, sampling_rate=SR, return_tensors="pt")
    kwargs = {
        key: value.to(model.device)
        for key, value in inputs.items()
        if isinstance(value, torch.Tensor)
    }
    out = model.backbone(**kwargs, output_hidden_states=(model.backbone_layer is not None))
    return out.hidden_states[model.backbone_layer] if model.backbone_layer is not None else out.last_hidden_state


def _align_sync(model: PronunciationAligner, file_name: str, transcription: str) -> dict[str, Any]:
    target_metadata = parse_target_transcription(transcription, set(model.phone_to_id))
    target_phones = [metadata.phone for metadata in target_metadata]
    unknown = [phone for phone in target_phones if phone not in model.phone_to_id]
    if unknown:
        raise ValueError(f"Unknown target phones: {' '.join(unknown)}")

    wav = _load_audio(file_name)
    if len(wav) == 0:
        raise ValueError("Audio is empty.")

    with torch.no_grad():
        embeddings = _extract_backbone_embeddings(model, wav)
        input_lengths = torch.tensor([embeddings.shape[1]], dtype=torch.long, device=model.device)
        logits = model.conformer_head(embeddings, input_lengths=input_lengths)
        input_length = int(input_lengths[0].item())

    target_ids = [model.phone_to_id[phone] for phone in target_phones]
    alignment = score_target_pronunciation(
        logits[0, :input_length],
        target_ids,
        model.blank_id,
        model.id_to_phone,
    )
    scoring = score_pronunciation_alignment(alignment, target_metadata=target_metadata)
    greedy_phones = _greedy_decode_phones(logits[0, :input_length], model.blank_id, model.id_to_phone)
    display_events = [_ui_display_event(event) for event in scoring["events"]]

    return {
        "transcription": transcription,
        "target_phones": target_phones,
        "best_offset_ms": 0.0,
        "wper": scoring["wper"],
        "greedy_phones": greedy_phones,
        "display_events": display_events,
    }


async def pron_alignment(file_name: str, transcription: str | None, lang: str | None = None) -> dict[str, Any]:
    if lang and lang != "en":
        raise ValueError(f"Unsupported pronunciation alignment language: {lang}")
    if not transcription:
        raise ValueError("Target transcription is required for pronunciation alignment.")

    model = await _get_model()
    result = await asyncio.to_thread(_align_sync, model, file_name, transcription)
    logger.info(
        "pron_alignment: lang=%s transcription=%s wper=%.3f greedy=[%s] alignment=%s",
        lang,
        transcription,
        result["wper"],
        " ".join(result["greedy_phones"]),
        _format_alignment_text(result["display_events"]),
    )
    logger.info(
        "pron_alignment_quality: %s",
        _format_alignment_quality_text(result["display_events"]),
    )
    return result
