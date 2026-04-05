# CHANGELOG

All notable development changes for `T000042-trier-social-stress-test` are documented here.

## [Unreleased] - 2026-04-05

### Added
- Added a Chinese-localized Trier Social Stress Test with instruction, baseline acclimation, speech preparation, speech delivery, serial subtraction, recovery, and goodbye screens.
- Added reference-backed literature files for TSST protocol timing, social-evaluative threat, and recovery framing.
- Added built-in PsychoPy primitives for the neutral judge panel and recording indicator so the task remains asset-light.

### Changed
- Replaced the copied fixed-ratio satiation scaffold with a canonical TSST stress-induction flow.
- Reworked human, QA, scripted-sim, and sampler-sim configurations to use the TSST phase sequence and shortened smoke-test timings.
- Updated the launcher, task metadata, and summary reporting to reflect phase duration rather than response scoring.

### Fixed
- Kept participant-facing text in YAML stimulus definitions for localization portability.
- Added explicit layout anchors for the judge panel, recording cue, and recovery screens.
