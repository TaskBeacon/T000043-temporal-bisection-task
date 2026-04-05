from __future__ import annotations

import math
import random
import re
from statistics import fmean
from typing import Any, Iterable

DEFAULT_CONDITIONS = ("learning", "test")


def _get_setting(settings: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(settings, name):
            value = getattr(settings, name)
            if value is not None:
                return value
    return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _normalize_token(value: Any) -> str:
    token = str(value if value is not None else "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "", token)


def parse_condition(condition: Any) -> str:
    """Normalize a block-role token."""
    if isinstance(condition, dict):
        raw = condition.get("condition") or condition.get("condition_id") or condition.get("label")
    else:
        raw = condition
    token = _normalize_token(raw)
    if not token:
        raise ValueError("trial condition is missing a condition token")
    if token not in {"learning", "test"}:
        return token
    return token


def resolve_block_role(block_idx: int) -> str:
    return "learning" if int(block_idx) <= 0 else "test"


def resolve_block_trial_count(settings: Any, block_role: str) -> int:
    if block_role == "learning":
        return _as_int(_get_setting(settings, "practice_trials", default=8), 8)
    return _as_int(_get_setting(settings, "test_trials", default=48), 48)


def build_block_conditions(n_trials: int, labels: list[Any], *, block_role: str, **_: Any) -> list[str]:
    """Return a deterministic condition token list for a block."""
    return [str(block_role)] * int(n_trials)


def _balanced_sequence(labels: list[Any], n_trials: int, seed: int) -> list[Any]:
    if not labels:
        return []
    rng = random.Random(int(seed))
    seq: list[Any] = []
    base = n_trials // len(labels)
    remainder = n_trials % len(labels)
    for label in labels:
        seq.extend([label] * base)
    if remainder:
        extra = list(labels)
        rng.shuffle(extra)
        seq.extend(extra[:remainder])
    rng.shuffle(seq)
    return seq


def build_temporal_bisection_schedule(
    *,
    block_role: str,
    trial_count: int,
    seed: int,
    anchor_short_ms: int,
    anchor_long_ms: int,
    probe_durations_ms: Iterable[int],
) -> list[dict[str, Any]]:
    """Create a deterministic per-trial schedule for a bisection block."""
    block_role = str(block_role).strip().lower()
    rng = random.Random(int(seed))
    short_ms = _as_int(anchor_short_ms, 400)
    long_ms = _as_int(anchor_long_ms, 1600)
    trial_count = int(trial_count)

    if block_role == "learning":
        labels = ["short", "long"]
        seq = _balanced_sequence(labels, trial_count, seed)
        schedule: list[dict[str, Any]] = []
        for i, label in enumerate(seq):
            ms = short_ms if label == "short" else long_ms
            schedule.append(
                {
                    "block_role": "learning",
                    "trial_role": "learning",
                    "trial_kind": f"learning_{label}",
                    "anchor_label": label,
                    "stimulus_ms": ms,
                    "is_anchor": True,
                    "stimulus_token": f"learning_{label}_{ms}",
                    "trial_index_in_block": i,
                }
            )
        return schedule

    probes = [int(ms) for ms in probe_durations_ms]
    if not probes:
        probes = [short_ms, long_ms]
    seq: list[int] = []
    repeats = math.ceil(trial_count / len(probes))
    for _ in range(repeats):
        seq.extend(probes)
    seq = seq[:trial_count]
    rng.shuffle(seq)

    schedule = []
    for i, ms in enumerate(seq):
        if ms == short_ms:
            anchor_label = "short"
            trial_kind = "test_anchor_short"
        elif ms == long_ms:
            anchor_label = "long"
            trial_kind = "test_anchor_long"
        else:
            anchor_label = None
            trial_kind = f"test_probe_{ms}"
        schedule.append(
            {
                "block_role": "test",
                "trial_role": "test",
                "trial_kind": trial_kind,
                "anchor_label": anchor_label,
                "stimulus_ms": ms,
                "is_anchor": anchor_label is not None,
                "stimulus_token": trial_kind,
                "trial_index_in_block": i,
            }
        )
    return schedule


def response_label_from_key(key: str | None, *, short_key: str, long_key: str) -> str | None:
    if key is None:
        return None
    token = str(key).strip().lower()
    if token == str(short_key).strip().lower():
        return "short"
    if token == str(long_key).strip().lower():
        return "long"
    return None


def format_duration_ms(ms: Any) -> str:
    try:
        return f"{int(round(float(ms)))} 毫秒"
    except Exception:
        return "未知时长"


def _phase_elapsed_values(row: dict[str, Any]) -> list[float]:
    payload = row.get("phase_elapsed_json")
    if not isinstance(payload, str):
        return []
    try:
        import json

        parsed = json.loads(payload)
    except Exception:
        return []
    if not isinstance(parsed, dict):
        return []
    values: list[float] = []
    for value in parsed.values():
        try:
            values.append(float(value))
        except Exception:
            continue
    return values


def _total_elapsed_s(row: dict[str, Any]) -> float:
    for key in ("total_elapsed_s", "trial_elapsed_s", "elapsed_s"):
        value = row.get(key)
        try:
            return float(value)
        except Exception:
            continue
    values = _phase_elapsed_values(row)
    return float(sum(values)) if values else 0.0


def _response_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if str(row.get("block_role", "")).lower() == "test"]


def summarizeBlock(reducedRows: list[dict[str, Any]], blockId: str) -> dict[str, Any]:
    rows = [row for row in reducedRows if str(row.get("block_id", "")) == str(blockId)]
    return _summarize(rows)


def summarizeOverall(reducedRows: list[dict[str, Any]]) -> dict[str, Any]:
    return _summarize(list(reducedRows))


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "trial_count": 0,
            "learning_trials": 0,
            "test_trials": 0,
            "response_count": 0,
            "miss_count": 0,
            "mean_rt_s": 0.0,
            "long_choice_rate": 0.0,
            "miss_rate": 0.0,
            "total_elapsed_s": 0.0,
            "total_elapsed_min": 0.0,
        }

    total_elapsed_s = max((_total_elapsed_s(row) for row in rows), default=0.0)
    learning_trials = sum(1 for row in rows if str(row.get("block_role", "")).lower() == "learning")
    test_rows = _response_rows(rows)
    test_trials = len(test_rows)
    response_rows = [row for row in test_rows if str(row.get("response_label") or "").lower() in {"short", "long"}]
    response_count = len(response_rows)
    miss_count = test_trials - response_count
    long_count = sum(1 for row in response_rows if str(row.get("response_label")).lower() == "long")
    mean_rt_s = fmean([float(row["response_rt_s"]) for row in response_rows if row.get("response_rt_s") is not None]) if response_rows else 0.0
    long_choice_rate = (long_count / response_count) if response_count else 0.0
    miss_rate = (miss_count / test_trials) if test_trials else 0.0
    return {
        "trial_count": len(rows),
        "learning_trials": learning_trials,
        "test_trials": test_trials,
        "response_count": response_count,
        "miss_count": miss_count,
        "mean_rt_s": float(mean_rt_s),
        "long_choice_rate": float(long_choice_rate),
        "miss_rate": float(miss_rate),
        "total_elapsed_s": float(total_elapsed_s),
        "total_elapsed_min": float(total_elapsed_s) / 60.0,
    }


__all__ = [
    "DEFAULT_CONDITIONS",
    "build_block_conditions",
    "build_temporal_bisection_schedule",
    "format_duration_ms",
    "parse_condition",
    "resolve_block_role",
    "resolve_block_trial_count",
    "response_label_from_key",
    "summarizeBlock",
    "summarizeOverall",
]
