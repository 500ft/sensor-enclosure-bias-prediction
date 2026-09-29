# EN-D03 — bounded preparation evidence

Date: 2026-09-09. Base (both reviewed PR layers merged): `c121f2bb3f247220df39dffd552468678254bbc8`.
Branch: `task/day-three-20260909`. Scope: Prepare a falsifiable day/night pilot and intake rules.

## Delivered change

Ten new synthetic intake tests cover full-day versus partial exposure, duplicate slots, missing paired data, invalid timestamps/weather/uncertainty/provenance and the actual CLI raw-hash boundary. 48 analysis tests pass. A sufficient synthetic CSV exits 3; tampered raw bytes exit 2. No physical pilot or model validation occurred. A further non-object JSON metadata counterexample reproduced a traceback; the CLI now returns diagnostic exit 2 for null/list/string metadata.

See [plan](https://github.com/500ft/sensor-enclosure-thermal-design/blob/ddf0a23098964ecfd036e32105dfa9564adc4ea7/docs/DAY3_PLAN.md) and [primary deliverable](../../docs/COLOCATION_PROTOCOL.md). Status is maintained only in [SPRINT_TASKS.csv](../../docs/SPRINT_TASKS.csv); original research/CAD gates remain unchanged. Delivery is a new PR, not an automatic merge or scientific release.

## Verification and reproducibility

Tool `wall_time_seconds` fields describe individual output/poll waits, not total command runtime; use the test runner's printed duration where available. All new/modified Markdown local links and the 13-column task ledger were checked successfully before commit. No separate independent reviewer participated in this task.

[checks.json](checks.json) records commands, observed exit statuses and selected outputs. Baseline source identity, command and outputs are in [baseline.json](baseline.json). Local Python is 3.11.8; CAD tests use the registered isolated Python 3.11.16/CadQuery toolchain. On another machine use the repository's existing workflow/dependency setup, not this machine's absolute interpreter path. The local pytest readline stub is recorded explicitly.

The listed relevant local checks completed. The P-V publication-mode exit 2, where present, is the expected blocked state, not a test failure.

No separate type/lint task was added: existing configured compile/tests and source-specific checks were used. Tests use synthetic developer cases; they are not independent human review, experimental results, adoption or held-out research evaluation. Source checks distinguish read sections from whole-paper review. Initial missing-module test failures for new tooling reflect tests written before implementation, not a defect in the old product. Prior scientific artifacts were not regenerated as new evidence.

## Remaining project work

Actual site/equipment identification, PI/data permission and measurements cannot be supplied by web research.

The only research findings here come from identified external sources; no downloaded third-party full text or sensitive raw data is committed. AI review and declared metadata do not substitute for authorship, permission, calibrated measurement or independent assessment.
