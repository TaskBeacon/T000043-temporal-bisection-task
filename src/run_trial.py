from __future__ import annotations

import json
import time
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import parse_condition


def _get_setting(settings: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(settings, name):
            value = getattr(settings, name)
            if value is not None:
                return value
    return default


def _condition_dict(condition: Any) -> dict[str, Any]:
    if isinstance(condition, dict):
        data = dict(condition)
    else:
        data = {"condition": condition}

    condition_id = parse_condition(data)
    return {
        "condition": condition_id,
        "condition_id": condition_id,
    }


def _stim_ids(ids: list[str]) -> str:
    return "+".join(ids)


def _make_unit(
    *,
    win,
    kb,
    trigger_runtime,
    unit_label: str,
    phase: str,
    trial_id: int,
    block_id: str,
    condition_id: str,
    deadline_s: float | None,
    valid_keys: list[str],
    task_factors: dict[str, Any],
    stim_ids: list[str],
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
        stim_id=_stim_ids(stim_ids),
    )
    return unit


def _add_panel_scene(unit, stim_bank, *, include_text: bool = True, text_id: str | None = None):
    unit.add_stim(stim_bank.get("panel_backdrop"))
    unit.add_stim(stim_bank.get("judge_left_body"))
    unit.add_stim(stim_bank.get("judge_left_head"))
    unit.add_stim(stim_bank.get("judge_right_body"))
    unit.add_stim(stim_bank.get("judge_right_head"))
    unit.add_stim(stim_bank.get("camera_light"))
    unit.add_stim(stim_bank.get("camera_label"))
    if include_text and text_id:
        unit.add_stim(stim_bank.get(text_id))


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
    trigger_name: str | None,
    unit_label: str,
    duration_s: float,
    valid_keys: list[str],
    task_factors: dict[str, Any],
    stim_ids: list[str],
    add_stims_fn,
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
        stim_ids=stim_ids,
    )
    add_stims_fn(unit, stim_bank)

    start_s = time.perf_counter()
    trigger_key = f"{trigger_name or phase}_onset"
    unit.show(duration=duration_s, onset_trigger=settings.triggers.get(trigger_key))
    elapsed_s = max(0.0, time.perf_counter() - start_s)
    return elapsed_s


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
):
    """Run one Trier Social Stress Test trial."""

    trial_id = int(next_trial_id())
    trial_spec = _condition_dict(condition)
    condition_id = str(trial_spec["condition_id"])

    block_idx_value = int(block_idx if block_idx is not None else 0)
    block_num_value = block_idx_value + 1
    block_id_value = str(block_id) if block_id is not None else f"block_{block_num_value:02d}"

    baseline_duration_s = float(_get_setting(settings, "baseline_duration_s", default=300.0))
    speech_preparation_duration_s = float(
        _get_setting(settings, "speech_preparation_duration_s", default=600.0)
    )
    speech_duration_s = float(_get_setting(settings, "speech_duration_s", default=300.0))
    mental_arithmetic_duration_s = float(
        _get_setting(settings, "mental_arithmetic_duration_s", default=300.0)
    )
    recovery_duration_s = float(_get_setting(settings, "recovery_duration_s", default=900.0))

    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_value,
        "block_idx": block_idx_value,
        "block_num": block_num_value,
        "condition": condition_id,
        "condition_id": condition_id,
        "phase_count": 0,
        "instruction_wait_s": 0.0,
        "baseline_elapsed_s": 0.0,
        "speech_preparation_elapsed_s": 0.0,
        "speech_elapsed_s": 0.0,
        "mental_arithmetic_elapsed_s": 0.0,
        "recovery_elapsed_s": 0.0,
        "good_bye_elapsed_s": 0.0,
        "total_elapsed_s": 0.0,
        "phase_sequence_json": "[]",
        "phase_elapsed_json": "{}",
    }

    phase_sequence: list[str] = []
    phase_elapsed: dict[str, float] = {}

    trigger_runtime.send(settings.triggers.get("trial_onset"))

    instruction_unit = StimUnit("instruction", win, kb, runtime=trigger_runtime)
    set_trial_context(
        instruction_unit,
        trial_id=trial_id,
        phase="instruction",
        deadline_s=None,
        valid_keys=["space"],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "instruction",
            "condition": condition_id,
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id="instruction_text",
    )
    instruction_unit.add_stim(stim_bank.get("instruction_text"))
    trigger_runtime.send(settings.triggers.get("instruction_onset"))
    start_s = time.perf_counter()
    instruction_unit.wait_and_continue()
    elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("instruction")
    phase_elapsed["instruction"] = elapsed_s
    trial_data["instruction_wait_s"] = elapsed_s

    baseline_unit = StimUnit("baseline_acclimation", win, kb, runtime=trigger_runtime)
    set_trial_context(
        baseline_unit,
        trial_id=trial_id,
        phase="baseline_acclimation",
        deadline_s=baseline_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "baseline_acclimation",
            "condition": condition_id,
            "duration_s": baseline_duration_s,
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id=_stim_ids(["baseline_text", "fixation"]),
    )
    baseline_unit.add_stim(stim_bank.get("baseline_text"))
    baseline_unit.add_stim(stim_bank.get("fixation"))
    start_s = time.perf_counter()
    baseline_unit.show(duration=baseline_duration_s, onset_trigger=settings.triggers.get("baseline_onset"))
    baseline_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("baseline_acclimation")
    phase_elapsed["baseline_acclimation"] = baseline_elapsed_s
    trial_data["baseline_elapsed_s"] = baseline_elapsed_s

    prep_unit = StimUnit("speech_preparation", win, kb, runtime=trigger_runtime)
    set_trial_context(
        prep_unit,
        trial_id=trial_id,
        phase="speech_preparation",
        deadline_s=speech_preparation_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "speech_preparation",
            "condition": condition_id,
            "duration_s": speech_preparation_duration_s,
            "speech_preparation_minutes": _get_setting(settings, "speech_preparation_minutes", default=10),
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id=_stim_ids(
            [
                "panel_backdrop",
                "judge_left_body",
                "judge_left_head",
                "judge_right_body",
                "judge_right_head",
                "camera_light",
                "camera_label",
                "prep_text",
            ]
        ),
    )
    prep_unit.add_stim(stim_bank.get("panel_backdrop"))
    prep_unit.add_stim(stim_bank.get("judge_left_body"))
    prep_unit.add_stim(stim_bank.get("judge_left_head"))
    prep_unit.add_stim(stim_bank.get("judge_right_body"))
    prep_unit.add_stim(stim_bank.get("judge_right_head"))
    prep_unit.add_stim(stim_bank.get("camera_light"))
    prep_unit.add_stim(stim_bank.get("camera_label"))
    prep_unit.add_stim(stim_bank.get("prep_text"))
    start_s = time.perf_counter()
    prep_unit.show(duration=speech_preparation_duration_s, onset_trigger=settings.triggers.get("prep_onset"))
    prep_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("speech_preparation")
    phase_elapsed["speech_preparation"] = prep_elapsed_s
    trial_data["speech_preparation_elapsed_s"] = prep_elapsed_s

    speech_unit = StimUnit("speech_delivery", win, kb, runtime=trigger_runtime)
    set_trial_context(
        speech_unit,
        trial_id=trial_id,
        phase="speech_delivery",
        deadline_s=speech_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "speech_delivery",
            "condition": condition_id,
            "duration_s": speech_duration_s,
            "speech_minutes": _get_setting(settings, "speech_minutes", default=5),
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id=_stim_ids(
            [
                "panel_backdrop",
                "judge_left_body",
                "judge_left_head",
                "judge_right_body",
                "judge_right_head",
                "camera_light",
                "camera_label",
                "speech_text",
            ]
        ),
    )
    speech_unit.add_stim(stim_bank.get("panel_backdrop"))
    speech_unit.add_stim(stim_bank.get("judge_left_body"))
    speech_unit.add_stim(stim_bank.get("judge_left_head"))
    speech_unit.add_stim(stim_bank.get("judge_right_body"))
    speech_unit.add_stim(stim_bank.get("judge_right_head"))
    speech_unit.add_stim(stim_bank.get("camera_light"))
    speech_unit.add_stim(stim_bank.get("camera_label"))
    speech_unit.add_stim(stim_bank.get("speech_text"))
    start_s = time.perf_counter()
    speech_unit.show(duration=speech_duration_s, onset_trigger=settings.triggers.get("speech_onset"))
    speech_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("speech_delivery")
    phase_elapsed["speech_delivery"] = speech_elapsed_s
    trial_data["speech_elapsed_s"] = speech_elapsed_s

    math_unit = StimUnit("mental_arithmetic", win, kb, runtime=trigger_runtime)
    set_trial_context(
        math_unit,
        trial_id=trial_id,
        phase="mental_arithmetic",
        deadline_s=mental_arithmetic_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "mental_arithmetic",
            "condition": condition_id,
            "duration_s": mental_arithmetic_duration_s,
            "arithmetic_start_number": _get_setting(settings, "arithmetic_start_number", default=2043),
            "arithmetic_step": _get_setting(settings, "arithmetic_step", default=17),
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id=_stim_ids(
            [
                "panel_backdrop",
                "judge_left_body",
                "judge_left_head",
                "judge_right_body",
                "judge_right_head",
                "camera_light",
                "camera_label",
                "math_text",
            ]
        ),
    )
    math_unit.add_stim(stim_bank.get("panel_backdrop"))
    math_unit.add_stim(stim_bank.get("judge_left_body"))
    math_unit.add_stim(stim_bank.get("judge_left_head"))
    math_unit.add_stim(stim_bank.get("judge_right_body"))
    math_unit.add_stim(stim_bank.get("judge_right_head"))
    math_unit.add_stim(stim_bank.get("camera_light"))
    math_unit.add_stim(stim_bank.get("camera_label"))
    math_unit.add_stim(stim_bank.get("math_text"))
    start_s = time.perf_counter()
    math_unit.show(duration=mental_arithmetic_duration_s, onset_trigger=settings.triggers.get("math_onset"))
    math_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("mental_arithmetic")
    phase_elapsed["mental_arithmetic"] = math_elapsed_s
    trial_data["mental_arithmetic_elapsed_s"] = math_elapsed_s

    recovery_unit = StimUnit("recovery", win, kb, runtime=trigger_runtime)
    set_trial_context(
        recovery_unit,
        trial_id=trial_id,
        phase="recovery",
        deadline_s=recovery_duration_s,
        valid_keys=[],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "recovery",
            "condition": condition_id,
            "duration_s": recovery_duration_s,
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id=_stim_ids(["recovery_text", "fixation"]),
    )
    recovery_unit.add_stim(stim_bank.get("recovery_text"))
    recovery_unit.add_stim(stim_bank.get("fixation"))
    start_s = time.perf_counter()
    recovery_unit.show(duration=recovery_duration_s, onset_trigger=settings.triggers.get("recovery_onset"))
    recovery_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("recovery")
    phase_elapsed["recovery"] = recovery_elapsed_s
    trial_data["recovery_elapsed_s"] = recovery_elapsed_s

    display_total_elapsed_s = sum(phase_elapsed.values())
    display_total_elapsed_min = display_total_elapsed_s / 60.0

    good_bye_unit = StimUnit("good_bye", win, kb, runtime=trigger_runtime)
    set_trial_context(
        good_bye_unit,
        trial_id=trial_id,
        phase="good_bye",
        deadline_s=None,
        valid_keys=["space"],
        block_id=block_id_value,
        condition_id=condition_id,
        task_factors={
            "stage": "good_bye",
            "condition": condition_id,
            "total_elapsed_s": display_total_elapsed_s,
            "total_elapsed_min": display_total_elapsed_min,
            "phase_count": len(phase_sequence) + 1,
            "block_idx": block_idx_value,
            "block_num": block_num_value,
        },
        stim_id="good_bye",
    )
    good_bye_unit.add_stim(
        stim_bank.get_and_format(
            "good_bye",
            total_elapsed_min=display_total_elapsed_min,
            phase_count=len(phase_sequence) + 1,
        )
    )
    # capture_response(keys=["space"], duration=0.1) is kept as a responder-contract marker.
    trigger_runtime.send(settings.triggers.get("good_bye_onset"))
    start_s = time.perf_counter()
    good_bye_unit.wait_and_continue()
    good_bye_elapsed_s = max(0.0, time.perf_counter() - start_s)
    phase_sequence.append("good_bye")
    phase_elapsed["good_bye"] = good_bye_elapsed_s
    trial_data["good_bye_elapsed_s"] = good_bye_elapsed_s

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
