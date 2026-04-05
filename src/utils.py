from __future__ import annotations

import json
import math
import re
from typing import Any

DEFAULT_CONDITIONS = ("tsst",)


def _normalize_token(value: Any) -> str:
    token = str(value if value is not None else "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "", token)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    token = str(value if value is not None else "").strip().lower()
    return token in {"1", "true", "yes", "y"}


def _as_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    return parsed if math.isfinite(parsed) else None


def _json_loads(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return None
    try:
        return json.loads(str(value))
    except Exception:
        return None


def parse_condition(condition: Any) -> str:
    if isinstance(condition, dict):
        raw = condition.get("condition") or condition.get("condition_id") or condition.get("label")
    else:
        raw = condition
    token = _normalize_token(raw)
    if not token:
        raise ValueError("trial condition is missing a condition token")
    return token


def _phase_elapsed_values(row: dict[str, Any]) -> list[float]:
    payload = _json_loads(row.get("phase_elapsed_json"))
    if not isinstance(payload, dict):
        return []

    values: list[float] = []
    for value in payload.values():
        parsed = _as_float(value)
        if parsed is not None:
            values.append(parsed)
    return values


def _phase_count(row: dict[str, Any]) -> int:
    phase_count = _as_float(row.get("phase_count"))
    if phase_count is not None:
        return int(phase_count)

    seq = _json_loads(row.get("phase_sequence_json"))
    if isinstance(seq, list):
        return len(seq)

    values = _phase_elapsed_values(row)
    return len(values)


def _total_elapsed_s(row: dict[str, Any]) -> float:
    for key in ("total_elapsed_s", "elapsed_s", "trial_elapsed_s"):
        parsed = _as_float(row.get(key))
        if parsed is not None:
            return parsed

    values = _phase_elapsed_values(row)
    if values:
        return float(sum(values))
    return 0.0


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "trial_count": 0,
            "phase_count": 0,
            "total_elapsed_s": 0.0,
            "total_elapsed_min": 0.0,
            "mean_phase_elapsed_s": 0.0,
        }

    total_elapsed_s = 0.0
    phase_count = 0
    trial_count = 0

    for row in rows:
        trial_count += 1
        total_elapsed_s = max(total_elapsed_s, _total_elapsed_s(row))
        phase_count = max(phase_count, _phase_count(row))

    mean_phase_elapsed_s = total_elapsed_s / phase_count if phase_count else 0.0
    return {
        "trial_count": trial_count,
        "phase_count": phase_count,
        "total_elapsed_s": total_elapsed_s,
        "total_elapsed_min": total_elapsed_s / 60.0,
        "mean_phase_elapsed_s": mean_phase_elapsed_s,
    }


def summarizeBlock(reducedRows: list[dict[str, Any]], blockId: str) -> dict[str, Any]:
    rows = [row for row in reducedRows if str(row.get("block_id", "")) == str(blockId)]
    return _summarize(rows)


def summarizeOverall(reducedRows: list[dict[str, Any]]) -> dict[str, Any]:
    return _summarize(list(reducedRows))


__all__ = [
    "DEFAULT_CONDITIONS",
    "parse_condition",
    "summarizeBlock",
    "summarizeOverall",
]
