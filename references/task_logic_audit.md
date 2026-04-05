# Task Logic Audit

## 1. Paradigm Intent

- Task: Temporal Bisection Task
- Primary construct: subjective duration categorization / interval timing
- Manipulated factors:
  - physical stimulus duration
  - anchor exposure versus probe classification
  - block role (`learning` vs `test`)
  - response mapping left/right
- Dependent measures:
  - proportion of "long" responses by duration
  - response time on test trials
  - miss / timeout rate
  - anchor-learning completion
- Key citations:
  - `W1968042267` - direct temporal bisection review and canonical short/long referent structure
  - `W2164353133` - open-access time-perception paper supporting subjective duration distortions across senses
  - `W2057409808` - high-impact interval-timing paper supporting duration calibration logic
  - `W2070140174` - high-impact open-access time-perception paper supporting duration/decision sensitivity

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 2
- Trials per block:
  - learning block: 8
  - test block: 48
- Randomization/counterbalancing:
  - learning anchors are shuffled deterministically within block
  - test durations are shuffled deterministically within block
  - the physical duration list is balanced so each level appears equally often across repeated cycles
- Condition weight policy:
  - `task.condition_weights` is not used for trial balancing because the block requires a custom schedule
  - the block role is fixed by block index rather than by weighted sampling
- Condition generation method:
  - custom generator
  - simple condition labels cannot represent a two-stage schedule where one block is anchor learning and the next block is duration classification with a different duration ladder
  - generated condition data shape passed into `run_trial.py`: per-trial condition label strings (`learning` or `test`) plus deterministic block-level schedule reconstruction from seed and trial index
- Runtime-generated trial values (if any):
  - per-trial duration, anchor label, and learning/test phase role are generated deterministically from block seed plus block-relative trial index
  - the schedule is reconstructed in `run_trial.py` so the same trial order is auditable from the block seed

### Trial State Machine

List each state in order with entry/exit conditions:

1. State name: `instruction`
   - Onset trigger: `instruction_onset`
   - Stimuli shown: Chinese task instructions, short/long anchor values, and left/right response mapping
   - Valid keys: `space`
   - Timeout behavior: waits until space is pressed
   - Next state: first block

2. State name: `learning_fixation`
   - Onset trigger: `learning_fixation_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: `learning_stimulus`

3. State name: `learning_stimulus`
   - Onset trigger: `learning_stimulus_onset`
   - Stimuli shown: centered white flash for either the short or long anchor duration
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: `learning_label`

4. State name: `learning_label`
   - Onset trigger: `learning_label_onset`
   - Stimuli shown: anchor label text indicating whether the just-presented duration was the short or long standard
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: `learning_iti`

5. State name: `learning_iti`
   - Onset trigger: `learning_iti_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: next learning trial or the test block

6. State name: `test_fixation`
   - Onset trigger: `test_fixation_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: `test_stimulus`

7. State name: `test_stimulus`
   - Onset trigger: `test_stimulus_onset`
   - Stimuli shown: centered white flash at one of the probe durations
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: `test_response`

8. State name: `test_response`
   - Onset trigger: `test_response_onset`
   - Stimuli shown: response prompt plus left/right choice boxes and labels
   - Valid keys: `left`, `right`
   - Timeout behavior: response window ends after the configured deadline if no key is pressed
   - Next state: `test_iti`

9. State name: `test_iti`
   - Onset trigger: `test_iti_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: timer-driven
   - Next state: next test trial or goodbye

10. State name: `good_bye`
   - Onset trigger: `good_bye_onset`
   - Stimuli shown: end-of-task summary screen
   - Valid keys: `space`
   - Timeout behavior: waits until space is pressed
   - Next state: experiment end

## 3. Condition Semantics

For each condition token in `task.conditions`:

- Condition ID: `learning`
  - Participant-facing meaning: anchor learning / memorization of the short and long standards
  - Concrete stimulus realization (visual/audio): repeated centered white flashes at the short or long anchor duration, each followed by a Chinese anchor label
  - Outcome rules: no accuracy scoring; the block exists to establish the duration referents

- Condition ID: `test`
  - Participant-facing meaning: duration classification trials used to build the psychometric bisection curve
  - Concrete stimulus realization (visual/audio): centered white flashes at anchor or probe durations, followed by a short-vs-long choice screen
  - Outcome rules: collect choice and response time; no objective correctness score is computed

Also document where participant-facing condition text/stimuli are defined:

- Participant-facing text source (config stimuli / code formatting / generated assets):
  - all participant-facing wording lives in `config/*.yaml`
  - `src/run_trial.py` only formats those config strings and does not hardcode participant text
  - the flash, fixation cross, and choice boxes are built from PsychoPy primitives defined in config
- Why this source is appropriate for auditability:
  - the literal wording is centralized and can be translated without code changes
  - the same config drives human, QA, and simulation modes
- Localization strategy (how language variants are swapped via config without code edits):
  - participant text is stored in Chinese in the YAML stimulus bank
  - any future language version can replace the YAML strings and fonts while leaving `run_trial.py` unchanged

## 4. Response and Scoring Rules

- Response mapping:
  - left arrow = short
  - right arrow = long
- Response key source (config field vs code constant):
  - config-driven via `task.key_list` and explicit short/long key fields in config
- If code-defined, why config-driven mapping is not sufficient:
  - not applicable; the task remains config-driven
- Missing-response policy:
  - if no key is pressed before timeout, the trial is logged as a timeout and the task advances
  - no punitive feedback is shown during test trials
- Correctness logic:
  - there is no objective correctness score for probe trials
  - the runtime records the chosen category and RT
  - practice anchor exposures are learning-only and do not require a judgment
- Reward/penalty updates:
  - none
- Running metrics:
  - long-response proportion by duration
  - mean RT on test trials
  - miss rate
  - trial count by block role

## 5. Stimulus Layout Plan

For every screen with multiple simultaneous options/stimuli:

- Screen name: `instruction`
  - Stimulus IDs shown together: `instruction_text`
  - Layout anchors (`pos`): centered
  - Size/spacing (`height`, width, wrap): multiline centered text with generous wrap width
  - Readability/overlap checks: single text block only
  - Rationale: task instructions should be readable without competing elements

- Screen name: `learning_stimulus`
  - Stimulus IDs shown together: `fixation`, `stimulus_flash`
  - Layout anchors (`pos`): fixation centered, flash centered
  - Size/spacing (`height`, width, wrap): flash sized as a clear square/circle flash, no extra text during the flash
  - Readability/overlap checks: fixation disappears before the flash starts
  - Rationale: anchor learning should isolate the duration signal

- Screen name: `learning_label`
  - Stimulus IDs shown together: `learning_label_text`
  - Layout anchors (`pos`): centered slightly below midline
  - Size/spacing (`height`, width, wrap): short line of Chinese anchor text with wide wrap width
  - Readability/overlap checks: no overlap with the flash because the flash is not displayed on this screen
  - Rationale: gives a clean verbal anchor without extra clutter

- Screen name: `test_response`
  - Stimulus IDs shown together: `response_prompt`, `choice_short_box`, `choice_long_box`, `choice_short_label`, `choice_long_label`, `choice_hint_text`
  - Layout anchors (`pos`): prompt top-center, choice boxes left/right of center, key hints below each box
  - Size/spacing (`height`, width, wrap): boxes wide enough to read on 1280x720, labels centered inside or above boxes, prompt wrapped to two lines max
  - Readability/overlap checks: left/right boxes must remain clearly separated and the prompt must not overlap them
  - Rationale: participants need an unambiguous two-choice layout during the judgment screen

- Screen name: `test_stimulus`
  - Stimulus IDs shown together: `fixation`, `stimulus_flash`
  - Layout anchors (`pos`): fixation centered, flash centered
  - Size/spacing (`height`, width, wrap): same flash geometry as learning
  - Readability/overlap checks: flash should not overlap any prompt text because no prompt is shown on this screen
  - Rationale: keeps the judged duration isolated from decision cues

- Screen name: `good_bye`
  - Stimulus IDs shown together: `good_bye_text`
  - Layout anchors (`pos`): centered
  - Size/spacing (`height`, width, wrap): summary text in a large centered block
  - Readability/overlap checks: single text block only
  - Rationale: simple summary and exit instruction

## 6. Trigger Plan

Map each phase/state to trigger code and semantics.

- `exp_onset`: experiment start
- `exp_end`: experiment end
- `block_onset`: block start
- `block_end`: block end
- `trial_onset`: trial start
- `instruction_onset`: instruction screen onset
- `learning_fixation_onset`: learning fixation onset
- `learning_stimulus_onset`: learning flash onset
- `learning_label_onset`: anchor label onset
- `learning_iti_onset`: learning inter-trial interval onset
- `test_fixation_onset`: test fixation onset
- `test_stimulus_onset`: test flash onset
- `test_response_onset`: response-screen onset
- `test_iti_onset`: test inter-trial interval onset
- `good_bye_onset`: goodbye screen onset

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style (simple single flow / helper-heavy / why):
  - simple single flow with two blocks
  - the block-level schedule is generated deterministically, but runtime control remains linear and auditable
- `utils.py` used? (yes/no)
  - yes
- If yes, exact purpose (adaptive controller / sequence generation / asset pool / other):
  - deterministic schedule generation for learning and test blocks
  - condition parsing
  - summary aggregation for long-response rate and RT
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

- Decision: use 400 ms and 1600 ms as the short and long anchors
  - Why inference was required: the selected high-citation literature establishes the bisection paradigm and short/long referents, but it does not uniquely fix one anchor pair across all implementations
  - Citation-supported rationale: the canonical temporal bisection literature uses a pair of memorized short/long standards, and 4:1 anchor spacing is a common implementation that preserves a clear psychometric midpoint

- Decision: use a visual white flash as the judged stimulus
  - Why inference was required: the selected literature supports the duration-categorization structure, but modality varies across studies
  - Citation-supported rationale: the temporal bisection paradigm is modality-flexible, and a built-in visual flash is the simplest reference-aligned implementation in PsyFlow

- Decision: use an anchor-learning block followed by a separate test block
  - Why inference was required: the exact block split varies across studies, but the paradigm requires the participant to learn the anchors before probe classification
  - Citation-supported rationale: the canonical task begins with memorization of the short and long referents and then proceeds to probe classification

- Decision: choose left/right arrow keys for short/long responses
  - Why inference was required: the selected papers describe a two-choice judgment but not a single universal keyboard mapping
  - Citation-supported rationale: a left/right mapping is a standard, low-confusion two-choice arrangement for binary timing judgments

## Contract Note

- Participant-facing labels/instructions/options should be config-defined whenever possible.
- `src/run_trial.py` should not hardcode participant-facing text that would require code edits for localization.
