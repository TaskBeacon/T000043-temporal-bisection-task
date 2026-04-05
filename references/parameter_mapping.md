# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `task_name` | `task.task_name` | `temporal_bisection_task` | `W1968042267` | Canonical temporal-bisection paradigm naming from the task review and direct task paper | direct | Task identity is explicit in the repo metadata |
| `language` | `task.language` | `Chinese` | `W1968042267` | The paradigm itself is language-agnostic; Chinese localization is a repo-level implementation choice | inferred | Participant-facing text is localized in YAML |
| `overall_seed` | `task.overall_seed` | `42043` | `W1968042267` | Deterministic seed used to reproduce learning/test schedules | inferred | Chosen to keep per-subject schedule reproducible |
| `block_seed` | `task.block_seed` | `[42043, 42044]` | `W1968042267` | Deterministic block seeds for learning and test blocks | inferred | One seed per block |
| `conditions` | `task.conditions` | `['learning', 'test']` | `W1968042267` | Two-stage bisection workflow: anchor learning followed by probe classification | adapted | Condition labels reflect the block roles |
| `condition_weights` | `task.condition_weights` | `{'learning': 1, 'test': 1}` | `W1968042267` | Condition balance is not used for schedule generation, but the two block roles are documented in config | inferred | Custom schedule generator handles exact order |
| `total_blocks` | `task.total_blocks` | `2` | `W1968042267` | Learning/test split used to separate anchor exposure from probe classification | direct | One block for anchors, one for probes |
| `practice_trials` | `task.practice_trials` | `8` | `W1968042267` | Anchor learning requires repeated exposure to the short and long standards | inferred | 4 short and 4 long trials |
| `test_trials` | `task.test_trials` | `48` | `W1968042267` | Probe classification is repeated enough times to support a psychometric curve | inferred | 6 repeats of 8 duration levels |
| `anchor_short_ms` | `task.anchor_short_ms` | `400` | `W1968042267` | Common short-standard value inferred from the canonical bisection literature | inferred | Short anchor duration |
| `anchor_long_ms` | `task.anchor_long_ms` | `1600` | `W1968042267` | Common long-standard value inferred from the canonical bisection literature | inferred | Long anchor duration |
| `probe_durations_ms` | `task.probe_durations_ms` | `[400, 500, 650, 800, 950, 1100, 1300, 1600]` | `W1968042267` | Balanced duration ladder centered near the geometric mean of the anchors | inferred | Creates a monotonic psychometric series |
| `fixation_duration_s` | `timing.fixation_duration_s` | `0.5` | `W2164353133` | Brief inter-trial fixation is standard in duration-judgment tasks | inferred | Keeps the temporal cue isolated |
| `learning_label_duration_s` | `timing.learning_label_duration_s` | `0.6` | `W1968042267` | Anchor labeling is a short, explicit learning step | inferred | Only shown in the learning block |
| `response_timeout_s` | `timing.response_timeout_s` | `3.0` | `W1968042267` | Binary choice screen should allow a bounded response window | inferred | Used only during test trials |
| `iti_duration_s` | `timing.iti_duration_s` | `0.4` | `W2164353133` | Short inter-trial gap keeps the trial stream continuous while reducing overlap | inferred | Applied after each trial |
| `response_key_short` | `task.response_key_short` | `left` | `W1968042267` | Left/right binary choice is a standard neutral mapping for two-choice categorization | inferred | Short = left arrow |
| `response_key_long` | `task.response_key_long` | `right` | `W1968042267` | Left/right binary choice is a standard neutral mapping for two-choice categorization | inferred | Long = right arrow |
| `start_key` | `task.start_key` | `space` | `W1968042267` | Standard start/continue key for instruction and exit screens | inferred | Used to begin and finish |
| `flash_size_px` | `stimuli.stimulus_flash.width` / `height` | `120 x 120` | `W2057409808` | Centered isolated duration cue drawn with built-in primitives | inferred | Visual flash stimulus |
| `choice_box_width_px` | `stimuli.choice_short_box.width` / `stimuli.choice_long_box.width` | `220` | `W1968042267` | Two-choice screen requires clear spatial separation between options | inferred | Boxes must not overlap the prompt |
| `choice_box_height_px` | `stimuli.choice_short_box.height` / `stimuli.choice_long_box.height` | `120` | `W1968042267` | Two-choice screen requires clear spatial separation between options | inferred | Boxes must remain readable |
| `body_font` | `task.body_font` | `SimHei` | `W1968042267` | Chinese participant-facing text requires a full-glyph font | inferred | Language-portable font choice |
| `instruction_font` | `task.instruction_font` | `SimHei` | `W1968042267` | Chinese participant-facing text requires a full-glyph font | inferred | Language-portable font choice |
| `prompt_font` | `task.prompt_font` | `SimHei` | `W1968042267` | Chinese participant-facing text requires a full-glyph font | inferred | Language-portable font choice |
