# Task Logic Audit

## 1. Paradigm Intent

- Task: Trier Social Stress Test
- Primary construct: acute psychosocial stress induction under social-evaluative threat
- Manipulated factors:
  - fixed phase order
  - public speaking under observation
  - mental arithmetic under evaluation
  - recovery/rest period after the stressor
- Dependent measures:
  - phase completion
  - elapsed time per phase
  - instruction-start latency
  - adherence to the scripted phase sequence
  - optional self-report or physiological follow-up outside this task repo
- Key citations:
  - `W2059005389` - protocol paper for TSST procedure and timing
  - `W2023477927` - friendly TSST variant showing the standard social-evaluative structure can be softened or removed
  - `W2080858141` - age/gender TSST paper supporting recovery/reactivity framing
  - `W1969430973` - comparison of psychosocial stress paradigms
  - `W2151454086` and `W2181244039` - high-impact acute-stress validation papers supporting the construct validity of psychosocial stress induction

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 1
- Trials per block: 1
- Randomization/counterbalancing:
  - none required for the canonical TSST sequence
  - all participants receive the same phase order
- Condition weight policy:
  - `task.condition_weights` is defined explicitly in `config/config.yaml`
  - runtime resolution is delegated to `TaskSettings.resolve_condition_weights()` via `BlockUnit.generate_conditions()`
  - weights are effectively even because there is only one condition token
- Condition generation method:
  - built-in `BlockUnit.generate_conditions(...)`
  - no custom generator is needed because the TSST is represented as a single scripted condition rather than a precompiled stimulus sequence
  - generated condition shape passed to `run_trial.py`: a single condition label (`tsst_standard`)
- Runtime-generated trial values:
  - phase durations come from config, not from per-trial stochastic sampling
  - the code only resolves the current condition label and reads deterministic duration fields
  - reproducibility is controlled by the normal PsyFlow task seed flow; no extra randomization is introduced

### Trial State Machine

List each state in order with entry/exit conditions:

1. State name: `instruction`
   - Onset trigger: `instruction_onset`
   - Stimuli shown: Chinese instruction text explaining the TSST, neutral judges, speech, arithmetic, and recovery
   - Valid keys: `space`
   - Timeout behavior: waits for operator/participant start; no auto-advance
   - Next state: `baseline_acclimation`

2. State name: `baseline_acclimation`
   - Onset trigger: `baseline_onset`
   - Stimuli shown: fixation plus a brief neutral wait instruction
   - Valid keys: none
   - Timeout behavior: timer-driven; continues automatically when duration ends
   - Next state: `speech_preparation`

3. State name: `speech_preparation`
   - Onset trigger: `prep_onset`
   - Stimuli shown: speech preparation prompt, neutral panel/camera iconography, and a reminder that the upcoming speech is evaluative
   - Valid keys: none
   - Timeout behavior: timer-driven; continues automatically when duration ends
   - Next state: `speech_delivery`

4. State name: `speech_delivery`
   - Onset trigger: `speech_onset`
   - Stimuli shown: spoken speech prompt, neutral judges, recording indicator, and the speech task prompt
   - Valid keys: none
   - Timeout behavior: timer-driven; continues automatically when duration ends
   - Next state: `mental_arithmetic`

5. State name: `mental_arithmetic`
   - Onset trigger: `math_onset`
   - Stimuli shown: serial-subtraction prompt, neutral judges, and recording indicator
   - Valid keys: none
   - Timeout behavior: timer-driven; continues automatically when duration ends
   - Next state: `recovery`

6. State name: `recovery`
   - Onset trigger: `recovery_onset`
   - Stimuli shown: fixation and a neutral recovery prompt
   - Valid keys: none
   - Timeout behavior: timer-driven; continues automatically when duration ends
   - Next state: `good_bye`

7. State name: `good_bye`
   - Onset trigger: `good_bye_onset`
   - Stimuli shown: end-of-task debrief/exit screen
   - Valid keys: `space`
   - Timeout behavior: waits for operator/participant confirmation or terminate flag
   - Next state: experiment end

## 3. Condition Semantics

For each condition token in `task.conditions`:

- Condition ID: `tsst_standard`
- Participant-facing meaning: the canonical Trier Social Stress Test stress induction sequence
- Concrete stimulus realization (visual/audio):
  - Chinese instructions explain the stress-test structure
  - a neutral social-evaluation panel is rendered using built-in PsychoPy primitives
  - a recording light/icon is shown during the speech and arithmetic phases
  - the speech phase asks the participant to deliver a job-related speech aloud
  - the arithmetic phase asks the participant to count backward from `2043` in steps of `17`
  - the recovery phase returns to a neutral fixation screen
- Outcome rules:
  - no reward, penalty, or performance score is computed
  - the session advances on elapsed time, not response correctness
  - the only response requirement is `space` to start/exit instruction/debrief screens

Also document where participant-facing condition text/stimuli are defined:

- Participant-facing text source (config stimuli / code formatting / generated assets):
  - all participant-facing wording lives in `config/*.yaml`
  - `src/run_trial.py` only formats those config strings and does not hardcode participant text
  - the panel/camera visuals are built from PsychoPy primitives defined in config
- Why this source is appropriate for auditability:
  - the literal wording is centralized and can be translated without code changes
  - the same config drives human, QA, and simulation modes
- Localization strategy (how language variants are swapped via config without code edits):
  - participant text is stored in Chinese in the YAML stimulus bank
  - any future language version can replace the YAML strings and fonts while leaving `run_trial.py` unchanged

## 4. Response and Scoring Rules

- Response mapping:
  - `space` starts the task from instructions
  - `space` may also be used to dismiss the goodbye screen
  - no participant response is required during the timed TSST phases
- Response key source (config field vs code constant):
  - config-driven via `task.response_key` / `task.key_list`
- If code-defined, why config-driven mapping is not sufficient:
  - not applicable; the task remains config-driven
- Missing-response policy:
  - missing responses during the timed phases are not treated as errors because those phases are timer-driven stress induction screens
  - if the participant does not press `space` on the instruction screen, the task remains there until the operator starts it
- Correctness logic:
  - no accuracy scoring is computed
- Reward/penalty updates:
  - none
- Running metrics:
  - phase elapsed time
  - total induction duration
  - number of completed phases
  - optional summary duration at goodbye

## 5. Stimulus Layout Plan

For every screen with multiple simultaneous options/stimuli:

- Screen name: `instruction`
  - Stimulus IDs shown together: `instruction_text`
  - Layout anchors (`pos`): centered at `[0, 0]`
  - Size/spacing (`height`, width, wrap): large centered text, wide wrap width for multi-line instructions
  - Readability/overlap checks: one text block only
  - Rationale: keeps the task introduction readable and avoids any conflicting stimulus positions

- Screen name: `baseline_acclimation`
  - Stimulus IDs shown together: `baseline_text`, `fixation`
  - Layout anchors (`pos`): `baseline_text` near top or center, `fixation` centered
  - Size/spacing (`height`, width, wrap): short text plus a large fixation cross
  - Readability/overlap checks: text and fixation are vertically separated
  - Rationale: neutral wait screen with a clear gaze anchor

- Screen name: `speech_preparation`
  - Stimulus IDs shown together: `prep_text`, `judge_left_head`, `judge_left_body`, `judge_right_head`, `judge_right_body`, `camera_light`
  - Layout anchors (`pos`): judge silhouettes in the upper half, camera indicator at top center, preparation text in the lower half
  - Size/spacing (`height`, width, wrap): moderate-sized text below the panel shapes, explicit spacing between left and right judges
  - Readability/overlap checks: judge shapes must not overlap the prompt text
  - Rationale: preserves the social-evaluative panel while leaving the prompt readable

- Screen name: `speech_delivery`
  - Stimulus IDs shown together: `speech_text`, `judge_left_head`, `judge_left_body`, `judge_right_head`, `judge_right_body`, `camera_light`
  - Layout anchors (`pos`): judge silhouettes upper half, speech prompt lower half
  - Size/spacing (`height`, width, wrap): prompt width wide enough for the job-speech instruction
  - Readability/overlap checks: the prompt must remain readable even with the panel visible
  - Rationale: keeps the evaluative audience visually present during the speech

- Screen name: `mental_arithmetic`
  - Stimulus IDs shown together: `math_text`, `judge_left_head`, `judge_left_body`, `judge_right_head`, `judge_right_body`, `camera_light`
  - Layout anchors (`pos`): judges/camera in the upper half, arithmetic prompt in the lower half
  - Size/spacing (`height`, width, wrap): prompt text large enough to read at a glance
  - Readability/overlap checks: the arithmetic rule must not overlap the judge shapes
  - Rationale: preserves evaluation pressure while presenting the serial-subtraction rule

- Screen name: `recovery`
  - Stimulus IDs shown together: `recovery_text`, `fixation`
  - Layout anchors (`pos`): recovery text above fixation, both centered
  - Size/spacing (`height`, width, wrap): short neutral prompt plus a large fixation cross
  - Readability/overlap checks: no overlap between the text and fixation cross
  - Rationale: shifts from social threat to quiet recovery cleanly

## 6. Trigger Plan

Map each phase/state to trigger code and semantics.

- `exp_onset`: experiment start
- `instruction_onset`: instruction screen onset
- `block_onset`: start of the single TSST block
- `trial_onset`: start of the canonical TSST sequence
- `baseline_onset`: onset of acclimation / pre-stress waiting
- `prep_onset`: onset of speech preparation
- `speech_onset`: onset of speech delivery
- `math_onset`: onset of serial subtraction
- `recovery_onset`: onset of recovery
- `good_bye_onset`: onset of debrief/exit screen
- `block_end`: end of the single TSST block
- `exp_end`: experiment end

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style (simple single flow / helper-heavy / why):
  - simple single flow
  - one instruction phase, one block, one trial, then goodbye
  - this keeps the stress-induction sequence auditable and easy to validate
- `utils.py` used? (yes/no)
  - yes
- If yes, exact purpose (adaptive controller / sequence generation / asset pool / other):
  - light summary utilities only, mainly for block/overall timing summaries
  - no adaptive controller or sequence engine is needed
- Custom controller used? (yes/no)
  - no
- If yes, why PsyFlow-native path is insufficient:
  - not applicable
- Legacy/backward-compatibility fallback logic required? (yes/no)
  - no
- If yes, scope and removal plan:
  - not applicable

## 8. Inference Log

List any inferred decisions not directly specified by references:

- Decision: use a 10-minute speech preparation phase
  - Why inference was required: the protocol literature shows minor variation across TSST variants, and the reference implementation needs one concrete duration
  - Citation-supported rationale: protocol papers and variants consistently include a substantial anticipatory preparation window before the speech

- Decision: use a 15-minute recovery phase
  - Why inference was required: the literature often measures recovery and cortisol changes over longer windows, but the exact duration is study-specific
  - Citation-supported rationale: TSST studies and recovery papers report a post-stressor recovery period; longer physiological follow-up windows are common

- Decision: implement the social-evaluative panel with PsychoPy primitives instead of external actor images
  - Why inference was required: the protocol requires two neutral judges and a recording setup, but the task repo is built to avoid placeholder assets when built-in primitives suffice
  - Citation-supported rationale: TSST protocol papers explicitly describe the neutral committee and recording context

- Decision: keep the build to one canonical stress condition instead of adding a friendly control branch
  - Why inference was required: the queue item asks for TSST, not a comparative stress-versus-control study
  - Citation-supported rationale: the standard TSST is itself a self-contained acute psychosocial stress induction paradigm

## Contract Note

- Participant-facing labels/instructions/options should be config-defined whenever possible.
- `src/run_trial.py` should not hardcode participant-facing text that would require code edits for localization.
