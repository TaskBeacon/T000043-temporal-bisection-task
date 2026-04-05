# Trier Social Stress Test

![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Trier Social Stress Test |
| Version | v0.1.0-dev |
| URL / Repository | E:/Taskbeacon/T000042-trier-social-stress-test |
| Short Description | Chinese TSST implementation with neutral judges, a public speech challenge, serial subtraction, and recovery. |
| Created By | TaskBeacon |
| Date Updated | 2026-04-05 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural |

## 1. Task Overview

This task implements the classic Trier Social Stress Test as a Chinese-localized PsyFlow protocol. The participant first reads the instructions, then completes a quiet baseline, a speech-preparation period, a 5-minute public speech challenge, a 5-minute serial subtraction challenge, and a recovery period. The core stressor is social evaluation: two neutral judges remain visible while the participant speaks and counts backward.

The task uses built-in PsychoPy primitives to render the judges, camera indicator, and fixation screens. No external media or response scoring is required, because the target construct is acute psychosocial stress induction rather than accuracy or learning.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Load mode and config | `main.py` loads `human`, `qa`, or `sim` mode and resolves the matching YAML config. |
| 2. Initialize runtime | Subject info, window, triggers, and the stimulus bank are initialized. |
| 3. Show instructions | The participant reads the Chinese TSST instructions and presses space to begin. |
| 4. Run the canonical TSST trial | One block contains one TSST trial with the fixed phase order. |
| 5. Finish | The recovery screen ends, the goodbye screen appears, and the data are saved. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Instruction | Explain the stress-test sequence and start with the space key. |
| Baseline acclimation | A brief quiet fixation period prepares the participant. |
| Speech preparation | The participant prepares a 10-minute speech about why they are fit for the job. |
| Speech delivery | The participant delivers the speech for 5 minutes while two neutral judges and a recording light remain visible. |
| Mental arithmetic | The participant counts backward from 2043 in steps of 17, again under observation. |
| Recovery | The participant rests quietly with a fixation cross. |
| Goodbye | The final screen reports the total elapsed time and exits on space. |

### Controller Logic

| Component | Description |
|---|---|
| Condition generation | `BlockUnit.generate_conditions()` produces a single `tsst` condition. |
| Phase order | `instruction -> baseline_acclimation -> speech_preparation -> speech_delivery -> mental_arithmetic -> recovery -> good_bye`. |
| Response handling | `space` starts the instruction screen and dismisses the goodbye screen; no response is required during the timed stress phases. |
| Timing control | Human mode uses the canonical long TSST durations; QA and sim configs shorten the same sequence for smoke testing. |
| Summary metrics | The trial reports phase count, per-phase elapsed time, and total elapsed time. |
| Triggering | Each phase emits a dedicated onset trigger so the stress sequence is auditable. |

### Other Logic

| Component | Description |
|---|---|
| Social-evaluative panel | The judges and camera indicator are rendered with PsychoPy shapes and text primitives. |
| No reward logic | There are no points, tokens, or rewards; this is a stress induction task. |
| No adaptive staircase | The TSST is a fixed-script protocol, so there is no adaptive controller. |
| QA/sim coverage | QA and both simulation profiles cover the same full phase sequence with short durations. |

## 3. Configuration Summary

All human settings are defined in `config/config.yaml`. QA and smoke-test overrides live in `config/config_qa.yaml`, `config/config_scripted_sim.yaml`, and `config/config_sampler_sim.yaml`.

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | 3-digit participant identifier used to seed the run. |

### b. Window Settings

| Parameter | Value |
|---|---|
| `size` | `[1280, 720]` |
| `units` | `pix` |
| `screen` | `0` |
| `bg_color` | `black` |
| `fullscreen` | `false` |
| `monitor_width_cm` | `35.5` |
| `monitor_distance_cm` | `60` |

### c. Stimuli

| Name | Type | Description |
|---|---|---|
| `instruction_text` | text | Chinese instructions describing the TSST sequence and the space key to start. |
| `baseline_text` | text | Quiet fixation prompt for the acclimation period. |
| `prep_text` | text | Speech preparation prompt. |
| `speech_text` | text | Public speech challenge prompt. |
| `math_text` | text | Serial subtraction prompt starting at 2043 and stepping by 17. |
| `recovery_text` | text | Recovery prompt with a quiet rest instruction. |
| `fixation` | text | Centered plus sign used during baseline and recovery. |
| `panel_backdrop` | rect | Dark panel backdrop behind the judges. |
| `judge_left_head` / `judge_left_body` | circle / rect | Left judge silhouette built from primitives. |
| `judge_right_head` / `judge_right_body` | circle / rect | Right judge silhouette built from primitives. |
| `camera_light` | circle | Red recording light shown during evaluative phases. |
| `camera_label` | text | Small `REC` label above the recording light. |
| `good_bye` | text | End-of-task summary and exit screen. |

### d. Timing

| Phase | Human | QA / Sim |
|---|---|---|
| Instruction pause | `0.1 s` | `0.1 s` |
| Baseline acclimation | `300 s` | `2 s` |
| Speech preparation | `600 s` | `3 s` |
| Speech delivery | `300 s` | `2 s` |
| Mental arithmetic | `300 s` | `2 s` |
| Recovery | `900 s` | `3 s` |
| Goodbye hold | `0.1 s` | `0.1 s` |

### e. Triggers

| Event | Code |
|---|---:|
| Experiment onset | `1` |
| Experiment end | `2` |
| Block onset | `10` |
| Block end | `11` |
| Trial onset | `20` |
| Instruction onset | `21` |
| Baseline onset | `22` |
| Preparation onset | `23` |
| Speech onset | `24` |
| Mental arithmetic onset | `25` |
| Recovery onset | `26` |
| Goodbye onset | `30` |

### f. Adaptive Controller

| Parameter | Value |
|---|---|
| `phase_order` | `instruction -> baseline_acclimation -> speech_preparation -> speech_delivery -> mental_arithmetic -> recovery -> good_bye` |
| `conditions` | `tsst` |
| `condition_weights` | `tsst: 1` |
| `total_blocks` | `1` |
| `trial_per_block` | `1` |
| `total_trials` | `1` |
| `speech_preparation_minutes` | `10` |
| `speech_minutes` | `5` |
| `arithmetic_start_number` | `2043` |
| `arithmetic_step` | `17` |
| `recovery_minutes` | `15` |
| `response_key` | `space` |
| `seed_mode` | `same_across_sub` |
| `overall_seed` | `42042` |
| `block_seed` | `42042` |

## 4. Methods (for academic publication)

The Trier Social Stress Test is a widely used acute psychosocial stress induction paradigm that combines social-evaluative threat, uncontrollability, public speaking, and mental arithmetic. In the canonical protocol, the participant prepares and delivers a speech in front of a neutral panel, then performs serial subtraction under observation, followed by a recovery period.

This implementation preserves that structure in Chinese with PsychoPy primitives. The judges and recording cue remain on-screen during the evaluative phases, the speech prompt requires continuous public speaking, and the arithmetic prompt begins at 2043 and decrements by 17. The task is therefore suited for behavioral or psychophysiological studies that need a reproducible TSST sequence without relying on external media assets.
