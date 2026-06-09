#!/usr/bin/env python3
import argparse
import json
from math import gcd
import os
from pathlib import Path
import sys

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pron_model import load_backbone, load_conformer_ctc_checkpoint
from pron_scoring import parse_target_transcription, score_pronunciation_alignment
from сtc_alignment import score_target_pronunciation


DEFAULT_CHECKPOINT = Path(
    "/cuda/pron/conformer_ctc_head/checkpoints/ctc_conformer_2l_dim192_h6_mHuBERT-147_frozen_last.pt"
)
TARGET_SR = 16_000
SUBSTITUTION_TARGET_EVIDENCE_THRESHOLD = 0.10


def parse_args():
    parser = argparse.ArgumentParser(
        description="Production-style pronunciation inference: audio + target transcription -> display events JSON."
    )
    parser.add_argument("audio", type=Path, help="Input wav/mp3/flac audio path.")
    parser.add_argument(
        "transcription",
        help="Target transcription, for example '/ˈfoʊ.t̬oʊ.ɡræf/' or 'f oʊ t̬ oʊ ɡ r æ f'.",
    )
    parser.add_argument("--checkpoint", "--ckpt", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--offset-ms",
        default="0",
        help="Comma-separated start offsets in milliseconds. Best wPER is returned at top level.",
    )
    parser.add_argument(
        "--include-diagnostic-events",
        action="store_true",
        help="Include raw diagnostic_events in addition to display_events.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    return parser.parse_args()


def parse_offsets_ms(text: str) -> list[float]:
    offsets = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        value = float(part)
        if value < 0:
            raise ValueError(f"Offset must be non-negative, got {value:g}ms")
        offsets.append(value)
    return offsets or [0.0]


def ui_display_event(event: dict) -> dict:
    kind_to_status = {
        "heard_target": "matched",
        "heard_substitution": "substitution",
        "missing_target": "deletion",
        "extra_heard": "insertion",
        "accepted_realization": "accepted",
    }
    status = kind_to_status.get(event["kind"], event.get("status", event["kind"]))
    target_phone = event.get("target_phone")
    heard_phone = event.get("heard_phone")
    acoustic_quality = event.get("best_prob") if heard_phone is not None else None
    target_quality = event.get("quality")
    result = {
        "status": status,
        "target_phone": target_phone,
        "heard_phone": heard_phone,
        "acoustic_quality": acoustic_quality,
        "target_quality": target_quality,
    }
    if status == "substitution":
        target_evidence = event.get("target_prob") or 0.0
        target_quality = target_quality or 0.0
        if target_evidence >= SUBSTITUTION_TARGET_EVIDENCE_THRESHOLD:
            target_quality = target_quality + target_evidence * (1.0 - target_quality)
        result["target_quality"] = round(target_quality, 4)
        result["target_evidence"] = round(target_evidence, 4)
    return result


def load_audio(path: Path) -> np.ndarray:
    wav, sr = sf.read(str(path), dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != TARGET_SR:
        divisor = gcd(sr, TARGET_SR)
        wav = resample_poly(wav, TARGET_SR // divisor, sr // divisor)
    return np.asarray(wav, dtype=np.float32)


def extract_backbone_embeddings(backbone, feature_extractor, wav: np.ndarray, backbone_layer, device: str):
    if hasattr(backbone, "extract_frame_embeddings"):
        embeddings = backbone.extract_frame_embeddings(wav, sampling_rate=TARGET_SR, layer=backbone_layer)
        embeddings = embeddings if embeddings.ndim == 3 else embeddings.unsqueeze(0)
        return embeddings.to(device)
    inputs = feature_extractor(wav, sampling_rate=TARGET_SR, return_tensors="pt")
    kwargs = {
        key: value.to(device)
        for key, value in inputs.items()
        if isinstance(value, torch.Tensor)
    }
    out = backbone(**kwargs, output_hidden_states=(backbone_layer is not None))
    return out.hidden_states[backbone_layer] if backbone_layer is not None else out.last_hidden_state


def infer_audio_logits(head, backbone, feature_extractor, wav: np.ndarray, backbone_layer, device: str):
    embeddings = extract_backbone_embeddings(backbone, feature_extractor, wav, backbone_layer, device)
    input_lengths = torch.tensor([embeddings.shape[1]], dtype=torch.long, device=device)
    logits = head(embeddings, input_lengths=input_lengths)
    return logits, int(input_lengths[0].item())


def greedy_decode_phones(logits: torch.Tensor, blank_id: int, id_to_phone: dict[int, str]) -> list[str]:
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


def compact_scoring(scoring: dict, offset_ms: float, include_diagnostic_events: bool) -> dict:
    result = {
        "offset_ms": offset_ms,
        "wper": scoring["wper"],
        "weighted_error_cost": scoring["weighted_error_cost"],
        "total_target_weight": scoring["total_target_weight"],
        "display_events": [ui_display_event(event) for event in scoring["events"]],
    }
    if include_diagnostic_events:
        result["summary"] = scoring["summary"]
        result["diagnostic_events"] = scoring["diagnostic_events"]
        result["scoring_events"] = scoring["events"]
    return result


@torch.no_grad()
def infer_pronunciation(
    *,
    audio_path: Path,
    transcription: str,
    checkpoint_path: Path = DEFAULT_CHECKPOINT,
    device: str = "cpu",
    offsets_ms: list[float] | None = None,
    include_diagnostic_events: bool = False,
) -> dict:
    offsets_ms = offsets_ms or [0.0]
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    head, phone_to_id, ckpt, backbone, feature_extractor = load_conformer_ctc_checkpoint(
        str(checkpoint_path), device, load_backbone_model=True
    )
    if backbone is None or feature_extractor is None:
        backbone, feature_extractor = load_backbone(ckpt["backbone_id"], device)
    head.eval()
    backbone.eval()

    id_to_phone = {pid: phone for phone, pid in phone_to_id.items()}
    target_metadata = parse_target_transcription(transcription, set(phone_to_id))
    target_phones = [metadata.phone for metadata in target_metadata]
    unknown = [phone for phone in target_phones if phone not in phone_to_id]
    if unknown:
        raise ValueError(f"Unknown target phones: {' '.join(unknown)}")
    target_ids = [phone_to_id[phone] for phone in target_phones]

    wav = load_audio(audio_path)
    best_result = None
    for offset_ms in offsets_ms:
        offset_samples = int(round(TARGET_SR * offset_ms / 1000.0))
        if offset_samples >= len(wav):
            continue
        logits, input_length = infer_audio_logits(
            head,
            backbone,
            feature_extractor,
            wav[offset_samples:],
            ckpt.get("backbone_layer", None),
            device,
        )
        input_lengths = torch.tensor([input_length], dtype=torch.long, device=logits.device)
        greedy_phones = greedy_decode_phones(logits[0, :input_length], head.blank_id, id_to_phone)
        alignment = score_target_pronunciation(
            logits[0, :input_length],
            target_ids,
            head.blank_id,
            id_to_phone,
        )
        scoring = score_pronunciation_alignment(alignment, target_metadata=target_metadata)
        result = compact_scoring(scoring, offset_ms, include_diagnostic_events)
        result["greedy_phones"] = greedy_phones
        if best_result is None or result["wper"] < best_result["wper"]:
            best_result = result

    if best_result is None:
        raise ValueError("All offsets are beyond audio length.")

    return {
        "audio": str(audio_path),
        "transcription": transcription,
        "target_phones": target_phones,
        "checkpoint": str(checkpoint_path),
        "best_offset_ms": best_result["offset_ms"],
        "wper": best_result["wper"],
        "greedy_phones": best_result["greedy_phones"],
        "display_events": best_result["display_events"],
    } | (
        {
            "summary": best_result["summary"],
            "diagnostic_events": best_result["diagnostic_events"],
            "scoring_events": best_result["scoring_events"],
        }
        if include_diagnostic_events
        else {}
    )


def main():
    args = parse_args()
    result = infer_pronunciation(
        audio_path=args.audio,
        transcription=args.transcription,
        checkpoint_path=args.checkpoint,
        device=args.device,
        offsets_ms=parse_offsets_ms(args.offset_ms),
        include_diagnostic_events=args.include_diagnostic_events,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
