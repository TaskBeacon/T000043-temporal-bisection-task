# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `phase_order` | `task.phase_order` | `["instruction", "baseline_acclimation", "speech_preparation", "speech_delivery", "mental_arithmetic", "recovery", "good_bye"]` | `W2059005389` | TSST protocol sequence: instruction, preparation, speech, arithmetic, recovery | `direct` | Fixed phase order with no branch logic. |
| `baseline_duration_s` | `timing.baseline_duration_s` | `300.0` | `W2059005389` | Pre-stress quiet baseline period used before the stressor | `direct` | Human mode uses the canonical 5-minute baseline. |
| `speech_preparation_duration_s` | `timing.speech_preparation_duration_s` | `600.0` | `W2059005389` | Anticipatory speech-preparation window before public speaking | `direct` | Human mode keeps the 10-minute preparation period from the selected protocol. |
| `speech_duration_s` | `timing.speech_duration_s` | `300.0` | `W2059005389` | 5-minute speech delivery period in front of the judges | `direct` | The core public-speaking stressor. |
| `mental_arithmetic_duration_s` | `timing.mental_arithmetic_duration_s` | `300.0` | `W2059005389` | 5-minute serial subtraction period after the speech | `direct` | Uses the standard TSST arithmetic duration. |
| `recovery_duration_s` | `timing.recovery_duration_s` | `900.0` | `W2080858141` | TSST recovery/reactivity follow-up is study-dependent and often extended beyond the stressor | `adapted` | Set to 15 minutes as a practical recovery window for this behavior task. |
| `arithmetic_start_number` | `task.arithmetic_start_number` | `2043` | `W2059005389` | Serial subtraction starts at 2043 in the selected protocol | `direct` | Shown in the arithmetic prompt. |
| `arithmetic_step` | `task.arithmetic_step` | `17` | `W2059005389` | Backward counting step is 17 in the selected protocol | `direct` | Shown in the arithmetic prompt. |
| `condition_weights` | `task.condition_weights` | `{"tsst": 1}` | `W1969430973` | The task is represented as one canonical stress condition rather than a multi-condition experiment | `inferred` | Even weighting is trivial because there is only one condition. |

Decision type values:

- `direct`
- `adapted`
- `inferred`
