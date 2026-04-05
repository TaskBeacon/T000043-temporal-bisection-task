# Temporal Bisection Task

![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Temporal Bisection Task |
| Version | v0.1.0-dev |
| URL / Repository | E:/Taskbeacon/T000043-temporal-bisection-task |
| Short Description | Chinese temporal bisection task with a learning block, a test block, and forced-choice short-vs-long judgments. |
| Created By | TaskBeacon |
| Date Updated | 2026-04-05 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural |

## 1. Task Overview

This task implements the canonical temporal bisection paradigm as a Chinese-localized PsyFlow protocol. The participant first reads the instructions, then completes a learning block that exposes the short and long anchor durations, and finally completes a test block that classifies probe durations as closer to the short or long standard.

Each trial presents a centered white square flash on a black background. In the learning block, the flash is followed by an explicit anchor label. In the test block, the participant responds with left and right arrows on a two-choice screen. The task records long-choice rate, response time, and miss rate rather than an objective accuracy score.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Load mode and config | `main.py` loads `human`, `qa`, or `sim` mode and resolves the matching YAML config. |
| 2. Initialize runtime | Subject info, window, triggers, and the stimulus bank are initialized. |
| 3. Show instructions | The participant reads the Chinese temporal-bisection instructions and presses space to begin. |
| 4. Run learning block | The first block presents short and long anchor flashes so the participant can learn the referents. |
| 5. Run test block | The second block presents probe durations and collects forced-choice short-vs-long judgments. |
| 6. Finish | The goodbye screen appears with summary metrics, and the data are saved. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Instruction | Explain the short and long anchor durations and start with the space key. |
| Learning fixation | A centered fixation cross marks the start of a learning trial. |
| Learning stimulus | A white square flashes for either 400 ms or 1600 ms. |
| Learning label | The screen states whether the flash was the short or long standard. |
| Learning ITI | A brief fixation separates learning exposures. |
| Test fixation | A centered fixation cross marks the start of a test trial. |
| Test stimulus | A white square flashes for one probe duration from the timing ladder. |
| Test response | A two-choice screen asks whether the duration was closer to short or long; left arrow = short, right arrow = long. |
| Test ITI | A brief fixation separates test judgments. |
| Goodbye | The final screen reports summary metrics and exits on space. |

### Controller Logic

| Component | Description |
|---|---|
| Condition generation | `BlockUnit.generate_conditions()` produces block labels, and `build_temporal_bisection_schedule()` reconstructs the per-trial anchor/probe order from the block seed. |
| Phase order | `instruction -> learning_fixation -> learning_stimulus -> learning_label -> learning_iti -> test_fixation -> test_stimulus -> test_response -> test_iti -> good_bye`. |
| Response handling | `space` starts the instruction screen and dismisses the goodbye screen; learning trials have no choice response, while test trials use left/right arrows. |
| Timing control | Human mode uses the canonical anchor and probe timings; QA and sim configs keep the same logic while enabling short smoke-test runs. |
| Summary metrics | The task reports long-choice rate, mean RT, miss rate, and elapsed time. |
| Triggering | Each participant-visible phase emits a dedicated onset trigger so the trial stream is auditable. |

### Other Logic

| Component | Description |
|---|---|
| White-square flash | The judged stimulus is a centered white rectangle rendered with PsychoPy primitives. |
| No reward logic | There are no points, tokens, rewards, or correctness feedback in the task. |
| No adaptive staircase | The task uses a fixed anchor/probe schedule rather than an adaptive timing controller. |
| QA/sim coverage | QA and both simulation profiles cover the same full phase sequence with short durations. |

## 3. Configuration Summary

All human settings are defined in `config/config.yaml`. QA and smoke-test overrides live in `config/config_qa.yaml`, `config/config_scripted_sim.yaml`, and `config/config_sampler_sim.yaml`.

The QA and simulation configs keep the same block structure but shorten the run to 16 total trials for smoke testing.

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
| `instruction_text` | text | Chinese instructions describing the short and long standards and the space key to start. |
| `learning_label_text` | text | Short Chinese label that explicitly names the short or long standard after each anchor flash. |
| `response_prompt_text` | text | Two-choice prompt asking whether the flash was closer to short or long. |
| `choice_short_box` / `choice_long_box` | rect | Left and right response boxes centered on the screen. |
| `choice_short_label` / `choice_long_label` | text | Large Chinese labels for short and long inside the boxes. |
| `choice_short_hint` / `choice_long_hint` | text | Arrow-key hints placed below each response box. |
| `fixation` | text | Centered plus sign used during fixation and ITI screens. |
| `stimulus_flash` | rect | Centered white square used for the timed flash. |
| `good_bye_text` | text | End-of-task summary and exit screen. |

### d. Timing

| Parameter | Value |
|---|---|
| `anchor_short_ms` | `400` |
| `anchor_long_ms` | `1600` |
| `probe_durations_ms` | `400, 500, 650, 800, 950, 1100, 1300, 1600` |
| `fixation_duration_s` | `0.5` |
| `learning_label_duration_s` | `0.6` |
| `iti_duration_s` | `0.4` |
| `response_timeout_s` | `3.0` |
| `qa.timing_scale` | `0.2` |

The shared timing values are also mirrored in the top-level `timing` section so PsyFlow validation can flatten them into runtime settings.

### e. Triggers

| Event | Code |
|---|---:|
| Experiment onset | `1` |
| Experiment end | `2` |
| Block onset | `10` |
| Block end | `11` |
| Trial onset | `20` |
| Instruction onset | `21` |
| Learning fixation onset | `22` |
| Learning stimulus onset | `23` |
| Learning label onset | `24` |
| Learning ITI onset | `25` |
| Test fixation onset | `26` |
| Test stimulus onset | `27` |
| Test response onset | `28` |
| Test short response | `29` |
| Test long response | `30` |
| Test timeout | `31` |
| Test ITI onset | `32` |
| Goodbye onset | `40` |

### f. Adaptive Controller

| Parameter | Value |
|---|---|
| `phase_order` | `instruction -> learning_fixation -> learning_stimulus -> learning_label -> learning_iti -> test_fixation -> test_stimulus -> test_response -> test_iti -> good_bye` |
| `conditions` | `learning`, `test` |
| `condition_weights` | `learning: 1`, `test: 1` |
| `total_blocks` | `2` |
| `practice_trials` | `8` |
| `test_trials` | `48` |
| `response_key_short` | `left` |
| `response_key_long` | `right` |
| `start_key` | `space` |
| `seed_mode` | `same_across_sub` |
| `overall_seed` | `42043` |
| `block_seed` | `[42043, 42044]` |

## 4. Methods (for academic publication)

The temporal bisection task is a classic interval-timing paradigm in which participants learn a short standard and a long standard, then classify probe durations according to which standard they seem closer to. The resulting response curve estimates subjective duration and the location of the psychometric midpoint.

This implementation preserves that structure in Chinese with PsychoPy primitives. A white square flash is shown centrally on a black background, the learning block reinforces the short and long referents, and the test block collects forced-choice short-versus-long judgments with left/right arrow keys. The task is therefore suited for behavioral or psychophysiological studies that need a reproducible interval-timing sequence without relying on external media assets.
