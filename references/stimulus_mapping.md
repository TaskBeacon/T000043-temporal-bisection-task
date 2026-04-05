# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `learning` | `instruction` | `instruction_text` | `你将完成一个时间二分任务。请记住短标准 400 毫秒和长标准 1600 毫秒；按空格开始。` | `W1968042267` | Canonical bisection instructions describe learning the short and long referents before classification begins | `psychopy_builtin` | `text` | Chinese instruction screen |
| `learning` | `learning_fixation` | `fixation` | `+` | `W2164353133` | Brief fixation separates successive duration judgments | `psychopy_builtin` | `text` | Centered fixation cross |
| `learning` | `learning_stimulus` | `stimulus_flash` | `白色方块闪现 400 毫秒` or `白色方块闪现 1600 毫秒` | `W1968042267` | Short/long standards are the referent durations for the bisection task | `psychopy_builtin` | `rect` | Duration depends on the learning trial |
| `learning` | `learning_label` | `learning_label_text` | `这是短标准` or `这是长标准` | `W1968042267` | Anchor learning is reinforced by explicit duration labels in the learning block | `psychopy_builtin` | `text` | Label shown after the flash |
| `learning` | `learning_iti` | `fixation` | `+` | `W2164353133` | Short between-trial gap to keep the stream clean | `psychopy_builtin` | `text` | Reuses the fixation stimulus |
| `test` | `test_fixation` | `fixation` | `+` | `W2164353133` | Brief fixation separates test trials | `psychopy_builtin` | `text` | Centered fixation cross |
| `test` | `test_stimulus` | `stimulus_flash` | `白色方块闪现，持续时间来自探测试次（400-1600 毫秒范围）` | `W1968042267` | Probe durations populate the psychometric function between the short and long standards | `psychopy_builtin` | `rect` | Duration varies by test trial |
| `test` | `test_response` | `response_prompt`, `choice_short_box`, `choice_long_box`, `choice_short_label`, `choice_long_label`, `choice_hint_text` | `左箭头 = 短，右箭头 = 长` | `W1968042267` | Two-choice classification is the core response requirement of the bisection task | `psychopy_builtin` | `rect`, `text` | Response layout uses explicit left/right separation |
| `test` | `test_iti` | `fixation` | `+` | `W2164353133` | Brief inter-trial interval between judgments | `psychopy_builtin` | `text` | Reuses the fixation stimulus |
| `learning` / `test` | `good_bye` | `good_bye_text` | `任务结束。按空格退出。` plus summary metrics | `W1968042267` | Exit screen is a task-local implementation detail, not a bisection-specific stimulus | `psychopy_builtin` | `text` | Shows summary and exits |

Allowed implementation modes:

- `psychopy_builtin`
- `generated_reference_asset`
- `licensed_external_asset`
