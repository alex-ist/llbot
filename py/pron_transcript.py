import asyncio
import json
import os
import re
from dataclasses import dataclass

import librosa
import torch
from huggingface_hub import login as hf_login, snapshot_download
from transformers import AutoConfig, AutoFeatureExtractor, AutoModel

from botlog import logger


BACKBONE_ID = "utter-project/mHuBERT-147"
HEAD_REPO = "istomin9192/mHuBERT-147-ipa-head"
SR = 16_000
MAX_SAMPLES = 15 * SR

_HF_TOKEN = os.environ.get("HF_TOKEN")
_MODEL = None
_MODEL_LOCK = asyncio.Lock()


@dataclass
class PronunciationModel:
    feature_extractor: object
    backbone: object
    conformer_head: object
    blank_id: int
    id2phone: dict
    device: str


def _normalize_ipa(ipa: str | None) -> str:
    if not ipa:
        return ""
    ipa = ipa.lower().strip()
    ipa = ipa.strip("/[]")
    ipa = re.sub(r"[\s.ˈˌː:]", "", ipa)
    return ipa


def compare_ipa(expected: str | None, actual: str | None) -> bool:
    return bool(expected and actual and _normalize_ipa(expected) == _normalize_ipa(actual))


def _decode_ctc_predictions(probs, blank_id: int, id2phone: dict) -> tuple[list[str], list[float]]:
    pred_ids = probs.argmax(dim=-1).tolist()
    pred_conf = probs.max(dim=-1).values.tolist()

    phones = []
    conf = []
    prev_id = None
    run_conf = []

    def flush_run():
        if prev_id is None or prev_id == blank_id:
            return
        phone = id2phone[str(prev_id)]
        if phone == "sil":
            return
        phones.append(phone)
        conf.append(sum(run_conf) / len(run_conf))

    for pred_id, frame_conf in zip(pred_ids, pred_conf):
        if pred_id != prev_id:
            flush_run()
            prev_id = pred_id
            run_conf = [frame_conf]
        else:
            run_conf.append(frame_conf)

    flush_run()
    return phones, conf


def _load_audio(file_name: str):
    wav, sr = librosa.load(file_name, sr=SR, mono=True)
    return wav[:MAX_SAMPLES]


def _load_model_sync() -> PronunciationModel:
    if _HF_TOKEN:
        hf_login(token=_HF_TOKEN, add_to_git_credential=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"pron_transcript: loading HF model on {device}")

    head_repo_dir = snapshot_download(repo_id=HEAD_REPO, token=_HF_TOKEN)
    conformer_head_dir = os.path.join(head_repo_dir, "conformer_v1")
    ipa_map_path = os.path.join(head_repo_dir, "ipa_map.json")

    conformer_config = AutoConfig.from_pretrained(
        conformer_head_dir,
        trust_remote_code=True,
    )
    backbone_id = getattr(conformer_config, "base_model", BACKBONE_ID)

    feature_extractor = AutoFeatureExtractor.from_pretrained(
        backbone_id,
        token=_HF_TOKEN,
    )
    backbone = AutoModel.from_pretrained(
        backbone_id,
        token=_HF_TOKEN,
    ).to(device).eval()
    conformer_head = AutoModel.from_pretrained(
        conformer_head_dir,
        trust_remote_code=True,
    ).to(device).eval()

    with open(ipa_map_path, encoding="utf-8") as f:
        id2phone = json.load(f)["id2phone"]

    blank_id = conformer_config.architecture["blank_id"]
    logger.info("pron_transcript: HF model loaded")
    return PronunciationModel(
        feature_extractor=feature_extractor,
        backbone=backbone,
        conformer_head=conformer_head,
        blank_id=blank_id,
        id2phone=id2phone,
        device=device,
    )


async def _get_model() -> PronunciationModel:
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    async with _MODEL_LOCK:
        if _MODEL is None:
            _MODEL = await asyncio.to_thread(_load_model_sync)
    return _MODEL


def _transcribe_sync(model: PronunciationModel, file_name: str) -> str:
    wav = _load_audio(file_name)
    if len(wav) == 0:
        return ""

    with torch.no_grad():
        inp = model.feature_extractor(wav, sampling_rate=SR, return_tensors="pt")
        emb = model.backbone(inp.input_values.to(model.device)).last_hidden_state
        outputs = model.conformer_head(emb, input_lengths=[emb.shape[1]])
        probs = torch.softmax(outputs.logits[0], dim=-1)

    phones, conf = _decode_ctc_predictions(probs, model.blank_id, model.id2phone)
    ipa = "".join(phones)
    scores = " ".join(str(int(c * 100)) for c in conf)
    logger.info(f"pron_transcript: conformer_ctc_v1: {' '.join(phones)} / {scores}")
    return ipa


async def pron_transcript(file_name, lang=None, await_word=None):
    if lang and lang != "en":
        logger.info(f"pron_transcript: skip unsupported lang={lang}")
        return ""

    model = await _get_model()
    ipa = await asyncio.to_thread(_transcribe_sync, model, file_name)
    logger.info(f"pron_transcript: lang={lang}, expect={await_word}, ipa={ipa}")
    return ipa
