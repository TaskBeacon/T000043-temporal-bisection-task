# CHANGELOG

All notable development changes for `T000043-temporal-bisection-task` are documented here.

## [Unreleased] - 2026-04-05

### Added
- Added a Chinese-localized temporal bisection task with a learning block, a test block, and a forced-choice short-vs-long decision screen.
- Added reference-backed literature files for anchor learning, probe classification, and interval-timing logic.
- Added built-in PsychoPy primitives for the white-square flash, fixation cross, and left/right response boxes so the task remains asset-light.

### Changed
- Replaced the copied scaffold with a canonical temporal-bisection flow built around short and long anchors.
- Reworked human, QA, scripted-sim, and sampler-sim configurations to use the new two-block schedule and deterministic probe ladder.
- Updated the launcher, task metadata, and summary reporting to reflect long-choice rate, response time, and miss rate rather than correctness scoring.

### Fixed
- Kept participant-facing text in YAML stimulus definitions for localization portability.
- Added explicit layout anchors for the instruction, flash, and response-choice screens.
