from __future__ import annotations

import json
import time
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import (
    build_temporal_bisection_schedule,
    format_duration_ms,
    parse_condition,
    response_label_from_key,
)


def _get_setting(settings: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(settings, name):
            value = getattr(settings, name)
            if value is not None:
                return value
    return default


def _int_setting(settings: Any, *names: str, default: int) -> int:
    try:
        return int(_get_setting(settings, *names, default=default))
    except Exception:
        return int(default)


def _float_setting(settings: Any, *names: str, default: float) -> float:
    try:
        return float(_get_setting(settings, *names, default=default))
    except Exception:
        return float(default)


def _phase_trigger(settings: Any, phase_name: str) -> int | None:
    triggers = getattr(settings, "triggers", {}) or {}
    if isinstance(triggers, dict):
        return triggers.get(phase_name)
    if hasattr(triggers, "get"):
        return triggers.get(phase_name)
    return None


def _stim_ids(*ids: str) -> str:
    return "+".join([str(item) for item in ids if item])


def _make_unit(
    *,
    win,
    kb,
    trigger_runtime,
    unit_label: str,
    phase: str,
    trial_id: int | str,
    block_id: str,
    condition_id: str,
    deadline_s: float | None,
    valid_keys: list[str],
    task_factors: dict[str, Any],
    stim_id: str,
):
    unit = StimUnit(unit_label, win, kb, runtime=trigger_runtime)
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=deadline_s,
        valid_keys=valid_keys,
        block_id=block_id,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id=stim_id,
    )
    return unit


def _show_timed_phase(
    *,
    stim_bank,
    trigger_runtime,
    win,
    kb,
    settings,
    trial_id: int,
    block_id: str,
    condition_id: str,
    phase: str,
    unit_label: str,
    duration_s: float,
    valid_keys: list[str],
    task_factors: dict[str, Any],
    stim_id: str,
):
    unit = _make_unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        unit_label=unit_label,
        phase=phase,
        trial_id=trial_id,
        block_id=block_id,
        condition_id=condition_id,
        deadline_s=duration_s,
        valid_keys=valid_keys,
        task_factors=task_factors,
        stim_id=stim_id,
    )
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=duration_s,
        valid_keys=valid_keys,
        block_id=block_id,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id=stim_id,
    )
    unit.add_stim(stim_bank.get("stimulus_flash"))
    start_s = time.perf_counter()
    unit.show(duration=duration_s, onset_trigger=_phase_trigger(settings, f"{phase}_onset"))
    return max(0.0, time.perf_counter() - start_s)


def _show_response_phase(
    *,
    stim_bank,
    trigger_runtime,
    win,
    kb,
    settings,
    trial_id: int,
    block_id: str,
    condition_id: str,
    phase: str,
    unit_label: str,
    duration_s: float,
    valid_keys: list[str],
    task_factors: dict[str, Any],
    stim_id: str,
    response_trigger: dict[str, int | None] | int | None,
    timeout_trigger: int | None,
):
    unit = _make_unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        unit_label=unit_label,
        phase=phase,
        trial_id=trial_id,
        block_id=block_id,
        condition_id=condition_id,
        deadline_s=duration_s,
        valid_keys=valid_keys,
        task_factors=task_factors,
        stim_id=stim_id,
    )
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=duration_s,
        valid_keys=valid_keys,
        block_id=block_id,
        condition_id=condition_id,
        task_factors=task_factors,
        stim_id=stim_id,
    )
    unit.add_stim(stim_bank.get("response_prompt_text"))
    unit.add_stim(stim_bank.get("choice_short_box"))
    unit.add_stim(stim_bank.get("choice_long_box"))
    unit.add_stim(stim_bank.get("choice_short_label"))
    unit.add_stim(stim_bank.get("choice_long_label"))
    unit.add_stim(stim_bank.get("choice_short_hint"))
    unit.add_stim(stim_bank.get("choice_long_hint"))
    start_s = time.perf_counter()
    unit.capture_response(
        keys=valid_keys,
        duration=duration_s,
        onset_trigger=_phase_trigger(settings, f"{phase}_onset"),
        response_trigger=response_trigger,
        timeout_trigger=timeout_trigger,
        terminate_on_response=True,
        correct_keys=valid_keys,
    )
    elapsed_s = max(0.0, time.perf_counter() - start_s)
    return unit, elapsed_s


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
    block_seed=None,
    block_role=None,
    block_trial_offset=None,
    block_trial_count=None,
):
    """Run one temporal-bisection trial."""

    trial_id = int(next_trial_id())
    condition_id = parse_condition(condition)

    block_idx_value = int(block_idx if block_idx is not None else 0)
    block_num_value = block_idx_value + 1
    block_id_value = str(block_id) if block_id is not None else f"block_{block_num_value:02d}"
    block_role_value = str(block_role or condition_id or "test").strip().lower()

    block_trial_offset_value = int(block_trial_offset or 0)
    block_trial_index = trial_id - block_trial_offset_value - 1
    block_trial_count_value = int(block_trial_count or 0)

    anchor_short_ms = _int_setting(settings, "anchor_short_ms", default=400)
    anchor_long_ms = _int_setting(settings, "anchor_long_ms", default=1600)
    probe_durations_ms = list(_get_setting(settings, "probe_durations_ms", default=[400, 500, 650, 800, 950, 1100, 1300, 1600]) or [])
    response_timeout_s = _float_setting(settings, "response_timeout_s", default=3.0)
    fixation_duration_s = _float_setting(settings, "fixation_duration_s", default=0.5)
    learning_label_duration_s = _float_setting(settings, "learning_label_duration_s", default=0.6)
    iti_duration_s = _float_setting(settings, "iti_duration_s", default=0.4)
    short_key = str(_get_setting(settings, "response_key_short", default="left") or "left").strip().lower()
    long_key = str(_get_setting(settings, "response_key_long", default="right") or "right").strip().lower()

    if block_role_value not in {"learning", "test"}:
        block_role_value = "learning" if block_idx_value <= 0 else "test"

    schedule_seed = int(block_seed if block_seed is not None else _get_setting(settings, "overall_seed", default=42043) or 42043)
    if block_trial_count_value <= 0:
        block_trial_count_value = int(getattr(settings, "practice_trials", 8) if block_role_value == "learning" else getattr(settings, "test_trials", 48))
    block_schedule = build_temporal_bisection_schedule(
        block_role=block_role_value,
        trial_count=block_trial_count_value,
        seed=schedule_seed,
        anchor_short_ms=anchor_short_ms,
        anchor_long_ms=anchor_long_ms,
        probe_durations_ms=probe_durations_ms,
    )

    if block_trial_index < 0 or block_trial_index >= len(block_schedule):
        raise IndexError(
            f"Temporal bisection trial index {block_trial_index} is out of range for "
            f"block role {block_role_value!r} with {len(block_schedule)} scheduled trials."
        )

    trial_spec = dict(block_schedule[block_trial_index])
    stimulus_ms = int(trial_spec.get("stimulus_ms", anchor_short_ms))
    anchor_label = trial_spec.get("anchor_label")
    is_anchor = bool(trial_spec.get("is_anchor", False))
    trial_kind = str(trial_spec.get("trial_kind") or trial_spec.get("stimulus_token") or condition_id)

    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "trial_index": trial_id,
        "block_id": block_id_value,
        "block_idx": block_idx_value,
        "block_num": block_num_value,
        "block_role": block_role_value,
        "condition": condition_id,
        "condition_id": condition_id,
        "block_trial_index": block_trial_index,
        "block_trial_offset": block_trial_offset_value,
        "block_trial_count": block_trial_count_value,
        "trial_kind": trial_kind,
        "trial_role": trial_spec.get("trial_role", block_role_value),
        "stimulus_ms": stimulus_ms,
        "stimulus_ms_text": format_duration_ms(stimulus_ms),
        "anchor_label": anchor_label,
        "is_anchor": is_anchor,
        "response_key": None,
        "response_label": None,
        "response_rt_s": None,
        "response_received": False,
        "response_timeout": False,
        "long_choice": None,
        "target_hit": 0,
        "target_rt": None,
        "phase_count": 0,
        "fixation_elapsed_s": 0.0,
        "stimulus_elapsed_s": 0.0,
        "decision_elapsed_s": 0.0,
        "learning_label_elapsed_s": 0.0,
        "iti_elapsed_s": 0.0,
        "total_elapsed_s": 0.0,
        "phase_sequence_json": "[]",
        "phase_elapsed_json": "{}",
    }

    phase_sequence: list[str] = []
    phase_elapsed: dict[str, float] = {}

    trigger_runtime.send(_phase_trigger(settings, "trial_onset"))

    fixation_phase = f"{block_role_value}_fixation"
    fixation_unit = _make_unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        unit_label=fixation_phase,
        phase=fixation_phase,
        trial_id=trial_id,
        block_id=block_id_value,
        condition_id=condition_id,
        deadline_s=fixation_duration_s,
        valid_keys=[],
        task_factors={
            "block_role": block_role_value,
            "trial_kind": trial_kind,
            "trial_role": trial_spec.get("trial_role", block_role_value),
            "stimulus_ms": stimulus_ms,
            "anchor_label": anchor_label,
            "is_anchor": is_anchor,
            "block_trial_index": block_trial_index,
            "block_trial_count": block_trial_count_value,
        },
        stim_id="fixation",
    )
    set_trial_context(
        fixation_unit,
        trial_id=trial_id,
        phase=fixation_phase,
        deadline_s=fixation_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "block_role": block_role_value,
            "trial_kind": trial_kind,
            "trial_role": trial_spec.get("trial_role", block_role_value),
            "stimulus_ms": stimulus_ms,
            "anchor_label": anchor_label,
            "is_anchor": is_anchor,
            "block_trial_index": block_trial_index,
            "block_trial_count": block_trial_count_value,
        },
        stim_id="fixation",
    )
    fixation_unit.add_stim(stim_bank.get("fixation"))
    start_s = time.perf_counter()
    fixation_unit.show(duration=fixation_duration_s, onset_trigger=_phase_trigger(settings, f"{fixation_phase}_onset"))
    fixation_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append(fixation_phase)
    phase_elapsed[fixation_phase] = fixation_elapsed_s
    trial_data["fixation_elapsed_s"] = fixation_elapsed_s

    stimulus_phase = f"{block_role_value}_stimulus"

    stimulus_duration_s = max(0.001, stimulus_ms / 1000.0)
    stimulus_unit = _make_unit(
        win=win,
        kb=kb,
        trigger_runtime=trigger_runtime,
        unit_label=stimulus_phase,
        phase=stimulus_phase,
        trial_id=trial_id,
        block_id=block_id_value,
        condition_id=condition_id,
        deadline_s=stimulus_duration_s,
        valid_keys=[],
        task_factors={
            "block_role": block_role_value,
            "trial_kind": trial_kind,
            "trial_role": trial_spec.get("trial_role", block_role_value),
            "stimulus_ms": stimulus_ms,
            "anchor_label": anchor_label,
            "is_anchor": is_anchor,
            "block_trial_index": block_trial_index,
            "block_trial_count": block_trial_count_value,
        },
        stim_id="stimulus_flash",
    )
    set_trial_context(
        stimulus_unit,
        trial_id=trial_id,
        phase=stimulus_phase,
        deadline_s=stimulus_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "block_role": block_role_value,
            "trial_kind": trial_kind,
            "trial_role": trial_spec.get("trial_role", block_role_value),
            "stimulus_ms": stimulus_ms,
            "anchor_label": anchor_label,
            "is_anchor": is_anchor,
            "block_trial_index": block_trial_index,
            "block_trial_count": block_trial_count_value,
        },
        stim_id="stimulus_flash",
    )
    stimulus_unit.add_stim(stim_bank.get("stimulus_flash"))
    start_s = time.perf_counter()
    stimulus_unit.show(duration=stimulus_duration_s, onset_trigger=_phase_trigger(settings, f"{stimulus_phase}_onset"))
    stimulus_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append(stimulus_phase)
    phase_elapsed[stimulus_phase] = stimulus_elapsed_s
    trial_data["stimulus_elapsed_s"] = stimulus_elapsed_s

    if block_role_value == "learning":
        learning_label_phase = "learning_label"
        learning_text = "这是短标准" if anchor_label == "short" else "这是长标准"
        learning_label_unit = _make_unit(
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            unit_label=learning_label_phase,
            phase=learning_label_phase,
            trial_id=trial_id,
            block_id=block_id_value,
            condition_id=condition_id,
            deadline_s=learning_label_duration_s,
            valid_keys=[],
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "anchor_text": learning_text,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
            },
            stim_id="learning_label_text",
        )
        set_trial_context(
            learning_label_unit,
            trial_id=trial_id,
            phase=learning_label_phase,
            deadline_s=learning_label_duration_s,
            valid_keys=[],
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "anchor_text": learning_text,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
            },
            stim_id="learning_label_text",
        )
        learning_label_unit.add_stim(
            stim_bank.get_and_format(
                "learning_label_text",
                anchor_label=learning_text,
                anchor_ms=stimulus_ms,
                anchor_ms_text=format_duration_ms(stimulus_ms),
            )
        )
        start_s = time.perf_counter()
        learning_label_unit.show(
            duration=learning_label_duration_s,
            onset_trigger=_phase_trigger(settings, "learning_label_onset"),
        )
        learning_label_elapsed_s = max(0.0, time.perf_counter() - start_s)
        phase_sequence.append(learning_label_phase)
        phase_elapsed[learning_label_phase] = learning_label_elapsed_s
        trial_data["learning_label_elapsed_s"] = learning_label_elapsed_s

        iti_phase = "learning_iti"
        iti_unit = _make_unit(
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            unit_label=iti_phase,
            phase=iti_phase,
            trial_id=trial_id,
            block_id=block_id_value,
            condition_id=condition_id,
            deadline_s=iti_duration_s,
            valid_keys=[],
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
            },
            stim_id="fixation",
        )
        set_trial_context(
            iti_unit,
            trial_id=trial_id,
            phase=iti_phase,
            deadline_s=iti_duration_s,
            valid_keys=[],
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
            },
            stim_id="fixation",
        )
        iti_unit.add_stim(stim_bank.get("fixation"))
        start_s = time.perf_counter()
        iti_unit.show(duration=iti_duration_s, onset_trigger=_phase_trigger(settings, "learning_iti_onset"))
        iti_elapsed_s = max(0.0, time.perf_counter() - start_s)
        phase_sequence.append(iti_phase)
        phase_elapsed[iti_phase] = iti_elapsed_s
        trial_data["iti_elapsed_s"] = iti_elapsed_s
    else:
        response_phase = "test_response"
        response_prompt_ids = _stim_ids(
            "response_prompt_text",
            "choice_short_box",
            "choice_short_label",
            "choice_short_hint",
            "choice_long_box",
            "choice_long_label",
            "choice_long_hint",
        )

        response_unit = _make_unit(
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            unit_label=response_phase,
            phase=response_phase,
            trial_id=trial_id,
            block_id=block_id_value,
            condition_id=condition_id,
            deadline_s=response_timeout_s,
            valid_keys=[short_key, long_key],
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
                "short_key": short_key,
                "long_key": long_key,
            },
            stim_id=response_prompt_ids,
        )
        set_trial_context(
            response_unit,
            trial_id=trial_id,
            phase=response_phase,
            deadline_s=response_timeout_s,
            valid_keys=[short_key, long_key],
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
                "short_key": short_key,
                "long_key": long_key,
            },
            stim_id=response_prompt_ids,
        )
        response_unit.add_stim(stim_bank.get("response_prompt_text"))
        response_unit.add_stim(stim_bank.get("choice_short_box"))
        response_unit.add_stim(stim_bank.get("choice_long_box"))
        response_unit.add_stim(stim_bank.get("choice_short_label"))
        response_unit.add_stim(stim_bank.get("choice_long_label"))
        response_unit.add_stim(stim_bank.get("choice_short_hint"))
        response_unit.add_stim(stim_bank.get("choice_long_hint"))
        start_s = time.perf_counter()
        response_unit.capture_response(
            keys=[short_key, long_key],
            duration=response_timeout_s,
            onset_trigger=_phase_trigger(settings, "test_response_onset"),
            response_trigger={
                short_key: _phase_trigger(settings, "test_response_short"),
                long_key: _phase_trigger(settings, "test_response_long"),
            },
            timeout_trigger=_phase_trigger(settings, "test_response_timeout"),
            terminate_on_response=True,
            correct_keys=[short_key, long_key],
        )
        decision_elapsed_s = max(0.0, time.perf_counter() - start_s)
        phase_sequence.append(response_phase)
        phase_elapsed[response_phase] = decision_elapsed_s
        trial_data["decision_elapsed_s"] = decision_elapsed_s

        response_key = response_unit.get_state("response", None)
        response_rt = response_unit.get_state("response_time", None)
        response_label = response_label_from_key(response_key, short_key=short_key, long_key=long_key)
        response_received = response_key is not None
        trial_data.update(
            {
                "response_key": response_key,
                "response_label": response_label,
                "response_rt_s": response_rt,
                "response_received": response_received,
                "response_timeout": not response_received,
                "long_choice": response_label == "long" if response_label is not None else None,
                "target_hit": 1 if response_received else 0,
                "target_rt": response_rt,
            }
        )

        iti_phase = "test_iti"
        iti_unit = _make_unit(
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            unit_label=iti_phase,
            phase=iti_phase,
            trial_id=trial_id,
            block_id=block_id_value,
            condition_id=condition_id,
            deadline_s=iti_duration_s,
            valid_keys=[],
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
            },
            stim_id="fixation",
        )
        set_trial_context(
            iti_unit,
            trial_id=trial_id,
            phase=iti_phase,
            deadline_s=iti_duration_s,
            valid_keys=[],
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors={
                "block_role": block_role_value,
                "trial_kind": trial_kind,
                "trial_role": trial_spec.get("trial_role", block_role_value),
                "stimulus_ms": stimulus_ms,
                "anchor_label": anchor_label,
                "is_anchor": is_anchor,
                "block_trial_index": block_trial_index,
                "block_trial_count": block_trial_count_value,
            },
            stim_id="fixation",
        )
        iti_unit.add_stim(stim_bank.get("fixation"))
        start_s = time.perf_counter()
        iti_unit.show(duration=iti_duration_s, onset_trigger=_phase_trigger(settings, "test_iti_onset"))
        iti_elapsed_s = max(0.0, time.perf_counter() - start_s)
        phase_sequence.append(iti_phase)
        phase_elapsed[iti_phase] = iti_elapsed_s
        trial_data["iti_elapsed_s"] = iti_elapsed_s

    total_elapsed_s = sum(phase_elapsed.values())
    trial_data.update(
        {
            "phase_count": len(phase_sequence),
            "total_elapsed_s": total_elapsed_s,
            "total_elapsed_min": total_elapsed_s / 60.0,
            "phase_sequence_json": json.dumps(phase_sequence, ensure_ascii=False),
            "phase_elapsed_json": json.dumps(phase_elapsed, ensure_ascii=False),
            "phase_elapsed_mean_s": (total_elapsed_s / len(phase_sequence)) if phase_sequence else 0.0,
        }
    )

    return trial_data


__all__ = ["run_trial"]
