# Assets for Trier Social Stress Test

This task is intentionally asset-light.

- All participant-facing text is defined in `config/*.yaml`.
- The judge panel, camera cue, fixation, and recovery screens use built-in PsychoPy primitives.
- No external image, movie, or audio files are required for the default human, QA, or simulation flows.

If a future protocol revision needs new media, add only reference-aligned assets and update `references/stimulus_mapping.md` accordingly.
