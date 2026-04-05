# Task Plot Audit

- generated_at: 2026-04-05T15:06:43
- mode: existing
- task_path: E:\Taskbeacon\T000042-trier-social-stress-test

## 1. Inputs and provenance

- E:\Taskbeacon\T000042-trier-social-stress-test\README.md
- E:\Taskbeacon\T000042-trier-social-stress-test\config\config.yaml
- E:\Taskbeacon\T000042-trier-social-stress-test\src\run_trial.py

## 2. Evidence extracted from README

- | Step | Description |
- |---|---|
- | Instruction | Explain the stress-test sequence and start with the space key. |
- | Baseline acclimation | A brief quiet fixation period prepares the participant. |
- | Speech preparation | The participant prepares a 10-minute speech about why they are fit for the job. |
- | Speech delivery | The participant delivers the speech for 5 minutes while two neutral judges and a recording light remain visible. |
- | Mental arithmetic | The participant counts backward from 2043 in steps of 17, again under observation. |
- | Recovery | The participant rests quietly with a fixation cross. |
- | Goodbye | The final screen reports the total elapsed time and exits on space. |

## 3. Evidence extracted from config/source

- tsst: phase=instruction, deadline_expr=None, response_expr=n/a, stim_expr='instruction_text'
- tsst: phase=baseline acclimation, deadline_expr=baseline_duration_s, response_expr=n/a, stim_expr=_stim_ids(['baseline_text', 'fixation'])
- tsst: phase=speech preparation, deadline_expr=speech_preparation_duration_s, response_expr=n/a, stim_expr=_stim_ids(['panel_backdrop', 'judge_left_body', 'judge_left_head', 'judge_right_body', 'judge_right_head', 'camera_light', 'camera_label', 'prep_text'])
- tsst: phase=speech delivery, deadline_expr=speech_duration_s, response_expr=n/a, stim_expr=_stim_ids(['panel_backdrop', 'judge_left_body', 'judge_left_head', 'judge_right_body', 'judge_right_head', 'camera_light', 'camera_label', 'speech_text'])
- tsst: phase=mental arithmetic, deadline_expr=mental_arithmetic_duration_s, response_expr=n/a, stim_expr=_stim_ids(['panel_backdrop', 'judge_left_body', 'judge_left_head', 'judge_right_body', 'judge_right_head', 'camera_light', 'camera_label', 'math_text'])
- tsst: phase=recovery, deadline_expr=recovery_duration_s, response_expr=n/a, stim_expr=_stim_ids(['recovery_text', 'fixation'])
- tsst: phase=good bye, deadline_expr=None, response_expr=n/a, stim_expr='good_bye'

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
- max_conditions: 4
- screens_per_timeline: 7
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.030, right=0.033, blank=0.116
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.0297, 'right_ratio': 0.0331, 'blank_ratio': 0.1165}
- validator_warnings:
  - timelines[0].phases[0] missing duration_ms; renderer will annotate as n/a.

## 7. Output files and checksums

- E:\Taskbeacon\T000042-trier-social-stress-test\references\task_plot_spec.yaml: sha256=64d592c65badf7b3c33fc6a8791977321ae9b1ce18c7f2060fa68e61dceadead
- E:\Taskbeacon\T000042-trier-social-stress-test\references\task_plot_spec.json: sha256=a01eb76ecf74744869e8cd4df8b606efb8c41cab7a7de43f8e164713b6592ebe
- E:\Taskbeacon\T000042-trier-social-stress-test\references\task_plot_source_excerpt.md: sha256=1d284dd6a211f215e0cb057328d8af925b74cd767b73d32294ea4d9be6506ec5
- E:\Taskbeacon\T000042-trier-social-stress-test\task_flow.png: sha256=d1a2758282df7a089282e21ae08fdf1581599694e1708b77752d374d9c0c97bb

## 8. Inferred/uncertain items

- tsst:instruction:unresolved variable 'None'
- tsst:baseline acclimation:heuristic numeric parse from 'float(_get_setting(settings, 'baseline_duration_s', default=300.0))'
- tsst:speech preparation:heuristic numeric parse from 'float(_get_setting(settings, 'speech_preparation_duration_s', default=600.0))'
- tsst:speech delivery:heuristic numeric parse from 'float(_get_setting(settings, 'speech_duration_s', default=300.0))'
- tsst:mental arithmetic:heuristic numeric parse from 'float(_get_setting(settings, 'mental_arithmetic_duration_s', default=300.0))'
- tsst:recovery:heuristic numeric parse from 'float(_get_setting(settings, 'recovery_duration_s', default=900.0))'
- tsst:good bye:unresolved variable 'None'
- tsst: phases truncated to screens_per_timeline=6
