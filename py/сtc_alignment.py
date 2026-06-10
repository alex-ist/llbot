from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class PhoneScoreThresholds:
    deletion_prob: float = 0.08
    substitution_prob: float = 0.50
    insertion_prob: float = 0.50


def ctc_forced_align_viterbi(log_probs: torch.Tensor, target_ids: list[int], blank_id: int) -> list[int]:
    """Return best CTC state index for each frame, conditioning on the full target."""
    if log_probs.ndim != 2:
        raise ValueError(f"Expected [time, classes] log_probs, got shape {tuple(log_probs.shape)}")
    if not target_ids:
        return [0] * int(log_probs.shape[0])

    device = log_probs.device
    expanded: list[int] = [blank_id]
    for pid in target_ids:
        expanded.extend((pid, blank_id))

    t_steps = int(log_probs.shape[0])
    s_steps = len(expanded)
    neg_inf = torch.tensor(-1.0e30, dtype=log_probs.dtype, device=device)
    trellis = torch.full((t_steps, s_steps), neg_inf, dtype=log_probs.dtype, device=device)
    backptr = torch.full((t_steps, s_steps), -1, dtype=torch.long, device=device)

    trellis[0, 0] = log_probs[0, blank_id]
    if s_steps > 1:
        trellis[0, 1] = log_probs[0, expanded[1]]
        backptr[0, 1] = 0

    for t in range(1, t_steps):
        for s, label_id in enumerate(expanded):
            candidates = [(trellis[t - 1, s], s)]
            if s > 0:
                candidates.append((trellis[t - 1, s - 1], s - 1))
            if s > 1 and label_id != blank_id and label_id != expanded[s - 2]:
                candidates.append((trellis[t - 1, s - 2], s - 2))
            best_score, best_state = max(candidates, key=lambda item: float(item[0]))
            trellis[t, s] = best_score + log_probs[t, label_id]
            backptr[t, s] = best_state

    final_states = [s_steps - 1]
    if s_steps > 1:
        final_states.append(s_steps - 2)
    final_state = max(final_states, key=lambda s: float(trellis[-1, s]))

    states = [0] * t_steps
    state = final_state
    for t in range(t_steps - 1, -1, -1):
        states[t] = int(state)
        prev = int(backptr[t, state])
        if prev >= 0:
            state = prev
    return states


def _top_phone_for_frames(probs: torch.Tensor, frame_ids: list[int], blank_id: int) -> tuple[int, float]:
    if not frame_ids:
        return blank_id, 0.0
    max_probs = probs[frame_ids].max(dim=0).values
    max_probs[blank_id] = -1.0
    best_id = int(max_probs.argmax().item())
    return best_id, float(max_probs[best_id].item())


def _status(
    target_prob: float,
    best_id: int,
    target_id: int,
    best_prob: float,
    thresholds: PhoneScoreThresholds,
) -> str:
    if target_prob < thresholds.deletion_prob:
        if best_id != target_id and best_prob >= thresholds.substitution_prob:
            return "substitution"
        return "deletion"
    if best_id != target_id:
        return "substitution"
    return "matched"


def _target_prob_for_frames(probs: torch.Tensor, frame_ids: list[int], target_id: int) -> float:
    if not frame_ids:
        return 0.0
    return float(probs[frame_ids, target_id].max().item())


def _repair_zero_frame_deletions(
    probs: torch.Tensor,
    target_ids: list[int],
    frames_by_target: list[list[int]],
    blank_id: int,
    thresholds: PhoneScoreThresholds,
) -> list[list[int]]:
    repaired = [list(frame_ids) for frame_ids in frames_by_target]
    for idx in range(len(target_ids) - 1):
        cur_frames = repaired[idx]
        next_frames = repaired[idx + 1]
        if not cur_frames:
            continue

        cur_target_prob = _target_prob_for_frames(probs, cur_frames, target_ids[idx])
        next_target_prob_on_cur = _target_prob_for_frames(probs, cur_frames, target_ids[idx + 1])
        next_target_prob = _target_prob_for_frames(probs, next_frames, target_ids[idx + 1])
        best_id, best_prob = _top_phone_for_frames(probs, cur_frames, blank_id)

        if (
            cur_target_prob < thresholds.deletion_prob
            and best_id == target_ids[idx + 1]
            and best_prob >= thresholds.substitution_prob
            and next_target_prob < thresholds.deletion_prob
            and next_target_prob_on_cur >= thresholds.substitution_prob
        ):
            repaired[idx] = []
            repaired[idx + 1] = cur_frames
    return repaired


def _is_silence(class_id: int, blank_id: int, id_to_phone: dict[int, str]) -> bool:
    return class_id == blank_id or id_to_phone.get(class_id) == "sil"


def _adjacent_target_ids(expanded: list[int], state_id: int, blank_id: int) -> set[int]:
    adjacent = set()
    for neighbor in (state_id - 1, state_id + 1):
        if 0 <= neighbor < len(expanded) and expanded[neighbor] != blank_id:
            adjacent.add(expanded[neighbor])
    return adjacent


def _detect_insertions(
    probs: torch.Tensor,
    states: list[int],
    expanded: list[int],
    blank_id: int,
    id_to_phone: dict[int, str],
    thresholds: PhoneScoreThresholds,
) -> list[dict[str, Any]]:
    candidates = []
    for frame_id, state_id in enumerate(states):
        if expanded[state_id] != blank_id:
            candidates.append(None)
            continue
        frame_probs = probs[frame_id]
        top_id = int(frame_probs.argmax().item())
        top_prob = float(frame_probs[top_id].item())
        if (
            _is_silence(top_id, blank_id, id_to_phone)
            or top_prob < thresholds.insertion_prob
            or top_id in _adjacent_target_ids(expanded, state_id, blank_id)
        ):
            candidates.append(None)
            continue
        candidates.append((top_id, top_prob))

    insertions: list[dict[str, Any]] = []
    start = None
    phone_id = None
    peak = 0.0
    for frame_id, candidate in enumerate(candidates + [None]):
        next_phone_id = candidate[0] if candidate is not None else None
        if candidate is not None and start is not None and next_phone_id == phone_id:
            peak = max(peak, candidate[1])
            continue
        if start is not None:
            insertions.append(
                {
                    "phone": id_to_phone.get(phone_id, str(phone_id)),
                    "start_frame": start,
                    "end_frame": frame_id,
                    "frames": frame_id - start,
                    "prob": round(peak, 4),
                    "status": "insertion",
                }
            )
        if candidate is None:
            start = None
            phone_id = None
            peak = 0.0
        else:
            start = frame_id
            phone_id = candidate[0]
            peak = candidate[1]
    return insertions


def _suppress_insertions_continuing_substitutions(
    insertions: list[dict[str, Any]],
    phone_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    filtered = []
    substitutions = [
        row
        for row in phone_rows
        if row["status"] == "substitution" and row["best_phone"] != "<blank>"
    ]
    for insertion in insertions:
        continues_substitution = any(
            insertion["phone"] == substitution["best_phone"]
            and (
                insertion["start_frame"] == substitution["end_frame"]
                or insertion["end_frame"] == substitution["start_frame"]
            )
            for substitution in substitutions
        )
        if not continues_substitution:
            filtered.append(insertion)
    return filtered


def score_target_pronunciation(
    logits: torch.Tensor,
    target_ids: list[int],
    blank_id: int,
    id_to_phone: dict[int, str],
    thresholds: PhoneScoreThresholds | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    thresholds = thresholds or PhoneScoreThresholds()
    log_probs = F.log_softmax(logits.detach().cpu(), dim=-1)
    raw_logits = logits.detach().cpu()
    probs = log_probs.exp()
    states = ctc_forced_align_viterbi(log_probs, target_ids, blank_id)
    expanded: list[int] = [blank_id]
    for pid in target_ids:
        expanded.extend((pid, blank_id))

    frames_by_target = [
        [idx for idx, state in enumerate(states) if state == 2 * target_index + 1]
        for target_index in range(len(target_ids))
    ]
    frames_by_target = _repair_zero_frame_deletions(
        probs,
        target_ids,
        frames_by_target,
        blank_id,
        thresholds,
    )

    phone_rows: list[dict[str, Any]] = []
    for target_index, target_id in enumerate(target_ids):
        frame_ids = frames_by_target[target_index]
        if frame_ids:
            start_frame = min(frame_ids)
            end_frame = max(frame_ids) + 1
        else:
            previous_ends = [
                max(prev_frames) + 1
                for prev_frames in frames_by_target[:target_index]
                if prev_frames
            ]
            next_starts = [
                min(next_frames)
                for next_frames in frames_by_target[target_index + 1 :]
                if next_frames
            ]
            anchor = previous_ends[-1] if previous_ends else (next_starts[0] if next_starts else None)
            start_frame = anchor
            end_frame = anchor
        target_probs = probs[frame_ids, target_id] if frame_ids else torch.empty(0)
        target_prob = float(target_probs.max().item()) if frame_ids else 0.0
        target_peak = float(probs[:, target_id].max().item())
        best_id, best_prob = _top_phone_for_frames(probs, frame_ids, blank_id)
        target_logit = float(raw_logits[frame_ids, target_id].max().item()) if frame_ids else 0.0
        best_logit = float(raw_logits[frame_ids, best_id].max().item()) if frame_ids else 0.0
        top = []
        if frame_ids:
            max_probs = probs[frame_ids].max(dim=0).values
            values, indices = torch.topk(max_probs, k=min(top_k, max_probs.shape[0]))
            top = [
                {"phone": "<blank>" if int(pid) == blank_id else id_to_phone.get(int(pid), str(int(pid))), "prob": round(float(prob), 4)}
                for prob, pid in zip(values.tolist(), indices.tolist())
            ]
        phone_rows.append(
            {
                "phone": id_to_phone.get(target_id, str(target_id)),
                "start_frame": start_frame,
                "end_frame": end_frame,
                "frames": len(frame_ids),
                "target_prob": round(target_prob, 4),
                "target_peak": round(target_peak, 4),
                "best_phone": "<blank>" if best_id == blank_id else id_to_phone.get(best_id, str(best_id)),
                "best_prob": round(best_prob, 4),
                "margin": round(target_prob - best_prob, 4),
                "target_logit": round(target_logit, 4),
                "best_logit": round(best_logit, 4),
                "logit_margin": round(target_logit - best_logit, 4),
                "status": _status(target_prob, best_id, target_id, best_prob, thresholds),
                "top": top,
            }
        )

    frame_labels = [expanded[state] for state in states]
    insertions = _detect_insertions(probs, states, expanded, blank_id, id_to_phone, thresholds)
    insertions = _suppress_insertions_continuing_substitutions(insertions, phone_rows)

    return {
        "phones": phone_rows,
        "insertions": insertions,
        "viterbi_states": states,
        "viterbi_labels": [
            "<blank>" if label_id == blank_id else id_to_phone.get(label_id, str(label_id))
            for label_id in frame_labels
        ],
    }
