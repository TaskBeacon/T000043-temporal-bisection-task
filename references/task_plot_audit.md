# Task Plot Audit

- generated_at: 2026-04-05T16:26:28
- mode: existing
- task_path: E:\Taskbeacon\T000043-temporal-bisection-task

## 1. Inputs and provenance

- E:\Taskbeacon\T000043-temporal-bisection-task\README.md
- E:\Taskbeacon\T000043-temporal-bisection-task\config\config.yaml
- E:\Taskbeacon\T000043-temporal-bisection-task\src\run_trial.py

## 2. Evidence extracted from README

- | Step | Description |
- |---|---|
- | Instruction | Explain the short and long anchor durations and start with the space key. |
- | Learning fixation | A centered fixation cross marks the start of a learning trial. |
- | Learning stimulus | A white square flashes for either 400 ms or 1600 ms. |
- | Learning label | The screen states whether the flash was the short or long standard. |
- | Learning ITI | A brief fixation separates learning exposures. |
- | Test fixation | A centered fixation cross marks the start of a test trial. |
- | Test stimulus | A white square flashes for one probe duration from the timing ladder. |
- | Test response | A two-choice screen asks whether the duration was closer to short or long; left arrow = short, right arrow = long. |
- | Test ITI | A brief fixation separates test judgments. |
- | Goodbye | The final screen reports summary metrics and exits on space. |

## 3. Evidence extracted from config/source

- learning: phase=fixation phase, deadline_expr=fixation_duration_s, response_expr=n/a, stim_expr='fixation'
- learning: phase=stimulus phase, deadline_expr=stimulus_duration_s, response_expr=n/a, stim_expr='stimulus_flash'
- learning: phase=learning label phase, deadline_expr=learning_label_duration_s, response_expr=n/a, stim_expr='learning_label_text'
- learning: phase=iti phase, deadline_expr=iti_duration_s, response_expr=n/a, stim_expr='fixation'
- learning: phase=response phase, deadline_expr=response_timeout_s, response_expr=response_timeout_s, stim_expr=response_prompt_ids
- learning: phase=iti phase, deadline_expr=iti_duration_s, response_expr=n/a, stim_expr='fixation'
- test: phase=fixation phase, deadline_expr=fixation_duration_s, response_expr=n/a, stim_expr='fixation'
- test: phase=stimulus phase, deadline_expr=stimulus_duration_s, response_expr=n/a, stim_expr='stimulus_flash'
- test: phase=learning label phase, deadline_expr=learning_label_duration_s, response_expr=n/a, stim_expr='learning_label_text'
- test: phase=iti phase, deadline_expr=iti_duration_s, response_expr=n/a, stim_expr='fixation'
- test: phase=response phase, deadline_expr=response_timeout_s, response_expr=response_timeout_s, stim_expr=response_prompt_ids
- test: phase=iti phase, deadline_expr=iti_duration_s, response_expr=n/a, stim_expr='fixation'

## 4. Mapping to task_plot_spec

- timeline collection: one representative timeline per unique trial logic
- phase flow inferred from run_trial set_trial_context order and branch predicates
- participant-visible show() phases without set_trial_context are inferred where possible and warned
- duration/response inferred from deadline/capture expressions
- stimulus examples inferred from stim_id + config stimuli
- conditions with equivalent phase/timing logic collapsed and annotated as variants
- root_key: task_plot_spec
- spec_version: 0.2

## 5. Style decision and rationale

- Single timeline-collection view selected by policy: one representative condition per unique timeline logic.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 2
- screens_per_timeline: 6
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.030, right=0.033, blank=0.116
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.0297, 'right_ratio': 0.0331, 'blank_ratio': 0.1155}

## 7. Output files and checksums

- E:\Taskbeacon\T000043-temporal-bisection-task\references\task_plot_spec.yaml: sha256=1726c8b35340ce7efde9b63cbd71664359036a2a7144b7b1a0f8faac21470ffe
- E:\Taskbeacon\T000043-temporal-bisection-task\references\task_plot_spec.json: sha256=27e0a57c205a0be0e6a1a6e8bd2b056b1843060a2cd93b8a2da66541f39e12fd
- E:\Taskbeacon\T000043-temporal-bisection-task\references\task_plot_source_excerpt.md: sha256=27aaac4a746c54c2a17ae63e8f1dfaa5e95fd767adb23d498f52c5c18ca09545
- E:\Taskbeacon\T000043-temporal-bisection-task\task_flow.png: sha256=9ab6dd132f42d9604c199ddf15df895f3a97dbdd9054c59ad3c2516a33df130c

## 8. Inferred/uncertain items

- learning:fixation phase:heuristic numeric parse from '_float_setting(settings, 'fixation_duration_s', default=0.5)'
- learning:stimulus phase:heuristic range parse from 'max(0.001, stimulus_ms / 1000.0)'
- learning:learning label phase:heuristic numeric parse from '_float_setting(settings, 'learning_label_duration_s', default=0.6)'
- learning:iti phase:heuristic numeric parse from '_float_setting(settings, 'iti_duration_s', default=0.4)'
- learning:response phase:heuristic numeric parse from '_float_setting(settings, 'response_timeout_s', default=3.0)'
- test:fixation phase:heuristic numeric parse from '_float_setting(settings, 'fixation_duration_s', default=0.5)'
- test:stimulus phase:heuristic range parse from 'max(0.001, stimulus_ms / 1000.0)'
- test:learning label phase:heuristic numeric parse from '_float_setting(settings, 'learning_label_duration_s', default=0.6)'
- test:iti phase:heuristic numeric parse from '_float_setting(settings, 'iti_duration_s', default=0.4)'
- test:response phase:heuristic numeric parse from '_float_setting(settings, 'response_timeout_s', default=3.0)'
- collapsed equivalent condition logic into representative timeline: learning, test
- unparsed if-tests defaulted to condition-agnostic applicability: block_role_value == 'learning'; block_role_value not in {'learning', 'test'}; block_trial_count_value <= 0; block_trial_index < 0; block_trial_index >= len(block_schedule)
