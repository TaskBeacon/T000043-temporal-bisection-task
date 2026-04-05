# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `tsst` | `instruction` | `instruction_text` | `你将进行一段经典的 Trier Social Stress Test。按空格开始。` | `W2059005389` | Protocol overview and participant instructions introduce the stress-test flow | `psychopy_builtin` | `text` | Chinese instruction screen. |
| `tsst` | `baseline_acclimation` | `baseline_text`, `fixation` | `请安静坐好，注视中央十字。` | `W2059005389` | Pre-stress quiet baseline / arrival waiting period | `psychopy_builtin` | `text` | Neutral fixation screen. |
| `tsst` | `speech_preparation` | `panel_backdrop`, `judge_left_head`, `judge_left_body`, `judge_right_head`, `judge_right_body`, `camera_light`, `camera_label`, `prep_text` | `请准备一段 10 分钟的陈述，说明你为什么适合这份工作。` | `W2059005389` | Speech-preparation period before the public-speaking stressor; neutral committee and recording context | `psychopy_builtin` | `rect`, `circle`, `text` | Judge silhouettes built from primitives. |
| `tsst` | `speech_delivery` | `panel_backdrop`, `judge_left_head`, `judge_left_body`, `judge_right_head`, `judge_right_body`, `camera_light`, `camera_label`, `speech_text` | `请开始陈述。你必须连续发言 5 分钟。` | `W2059005389` | Five-minute speech period delivered in front of a neutral committee | `psychopy_builtin` | `rect`, `circle`, `text` | Recording light stays visible during speech. |
| `tsst` | `mental_arithmetic` | `panel_backdrop`, `judge_left_head`, `judge_left_body`, `judge_right_head`, `judge_right_body`, `camera_light`, `camera_label`, `math_text` | `请从 2043 开始每次减 17。` | `W2059005389` | Five-minute serial subtraction task under observation | `psychopy_builtin` | `rect`, `circle`, `text` | Error instruction is part of the prompt. |
| `tsst` | `recovery` | `recovery_text`, `fixation` | `请保持安静休息，继续注视中央十字。` | `W2080858141` | Post-stressor recovery / reactivity follow-up period | `psychopy_builtin` | `text` | Judge panel is removed from this screen. |
| `tsst` | `good_bye` | `good_bye` | `任务结束。按空格退出。` | `W2059005389` | Final exit screen after the protocol sequence | `psychopy_builtin` | `text` | Shows elapsed time and phase count. |

Allowed implementation modes:

- `psychopy_builtin`
- `generated_reference_asset`
- `licensed_external_asset`
