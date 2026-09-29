# Sprint progress

## 2026-09-11 — evidence-gap correction

The [current correction](specs/evidence-gap-correction/test-report.md) supersedes any interpretation that earlier preparation closed a physical, approval, or source-review gate. Work is on `fix/evidence-gaps-20260911` from current renamed main; historical entries below retain their original dates and PR snapshots. The original day-3 and presentation PRs are now merged, but this correction is a new reviewable change, not an asserted merge or publication.

Each omitted or incomplete recommendation is accounted for separately in the current correction and existing task ledgers. No owner signature, measurement, PI conversation, imagery judgment, disclosure approval or independent review was fabricated. Exact tests, scope and next inputs are linked from the correction record; actual delivery state is established by its PR.

## Evidence-gap correction — 2026-09-11

This current entry supersedes ambiguous preparation/completion language in the
historical entries below. Baseline clean main was
`182cb1f7bfa7905c09dc465cc559267d416f16c5`; correction branch is
`fix/evidence-gaps-20260911`. EN-D03 already had an executable
`analysis/colocation_intake.py` and tests; its deliverable cell omitted them.
The cell is corrected, not used to claim a newly implemented physical validator.
The requested `analysis/intake_gate.py` is now a tested delegating module CLI.

The authoritative [ledger](SPRINT_TASKS.csv) now explicitly separates EN-R01
(draft protocol preparation done), EN-R02 (executable software verification done)
and EN-R03 (actual co-location acquisition/review blocked). [Corrected 2026-09-16:
this sentence previously named "EN-R03S" for the blocked acquisition. EN-R03 is
the blocked Owner acquisition/review task; EN-R03S is the separate synthetic
rehearsal added 2026-09-12 and marked done. The two evidence routes must not be
conflated -- EN-R03S proves the arithmetic chain, not the enclosure.] A malformed timestamp
metadata regression exposed a traceback; the intake now returns diagnostic exit
2. All 52 analysis tests pass, including identical behavior through both module
names. Tests generate synthetic fixtures, including deliberately physical-labeled
routing cases; these are not real measurements or independent validation.

See the [correction evidence](specs/evidence-gap-correction/test-report.md) and
[owner session packet](COLOCATION_OWNER_SESSION.md), prepared but not sent or
scheduled. PI approval, actual equipment/calibration, protocol freeze and lab
acquisition remain blocked. No new model-derived acceptance tolerance, data,
research result, license change, push or merge is part of this correction.

## Day-3 work — 2026-09-09

Delivery update: the preparation was committed as 500ft and pushed; [day-3 PR](https://github.com/500ft/Enclosure-Research/pull/9) is open against main. Initial implementation source: `245f280667c8fc79204915b5b8ea2f47bb446291` (later review/documentation commits are visible in the PR). This supersedes the pre-push stopping state below. Original day-1/day-2 PRs are merged; this new PR is not merged. Resume from the named unresolved project gates in [DAY3_PLAN.md](https://github.com/500ft/sensor-enclosure-thermal-design/blob/ddf0a23098964ecfd036e32105dfa9564adc4ea7/docs/DAY3_PLAN.md), not from the already completed push step.

Both reviewed PR layers merged into main; new work starts from `c121f2bb3f247220df39dffd552468678254bbc8` on `task/day-three-20260909`. Ten new synthetic intake tests cover full-day versus partial exposure, duplicate slots, missing paired data, invalid timestamps/weather/uncertainty/provenance and the actual CLI raw-hash boundary. 48 analysis tests pass. A sufficient synthetic CSV exits 3; tampered raw bytes exit 2. No physical pilot or model validation occurred. A further non-object JSON metadata counterexample reproduced a traceback; the CLI now returns diagnostic exit 2 for null/list/string metadata.

The [evidence record](../evidence/task-day3-2026-09-09/README.md) contains checks and limits. Work is locally verified and not yet recorded here as pushed/merged. Current edits belong to this task; original checkouts were preserved. Next: finish verification, commit the bounded change and open the new PR; preserve all stated external gates.

## Review amendment — 2026-09-09

Read [the reproduced findings, corrections and current checks](../evidence/review-2026-09-09/README.md)
before the historical day-2 counts below. Review branch `review/day-two-20260909`;
amendment targets the existing day-2 PR, not main. No owner/measurement gate closes.


## 2026-09-09 — EN-D02 night clear-sky case

Ran the existing solver at zero solar load with unchanged assumptions and promoted the result to a
[reproducible table](../analysis/output/thermal_bias_night_table.csv) and a
[results section](../analysis/thermal_bias_results.md): the baseline box reads **-4.0 °C** in calm clear-sky
night against **+22.7 °C** at midday, so the enclosure error is sign-changing, not warm. The daytime table
and figure are byte-unchanged; six new tests assert sign and ordering only. Still SIMULATION / pending
lab data; owner gates unchanged. [Verification](../evidence/task-2026-09-09/README.md).
Branch `task/priority-two-20260909`.

## 2026-09-08 — EN-D01: primary matched-finish thermal control

One additional two-hour-estimate P1 task, outside the original 30-hour sprint;
historical task rows and owner-blocked work remain unchanged. Baseline main
`199cb5d38bc70af271b4e064d79d4d8415ff4630`, clean starting tree; worktree
`/Users/redhose/Developer/daily-prs/2026-09-08/Enclosure-Research`, branch
`task/priority-one-20260908`. Agent used execute-and-test and quality-gates:
baseline 24 tests pass, then five new regressions fail before implementation,
then 29 pass. The initial `python3` (3.13.7) attempt lacked pandas; this was an
environment mismatch, resolved with existing `python` (3.11.8), not a code fix.

Default sweep/CSV/figure now include V0P: a copied V0 with only absorptance
changed to match the shield. Existing 30 numeric CSV rows are preserved exactly;
10 control rows added. External-working-directory CLI and regenerated figure
were checked. No fabricated measurements, new physical approval, external
outreach or deployment. [Verification and limits](../evidence/task-2026-09-08/verification.md).

Containing commit identifies source; local changes are committed as 500ft for
the requested PR. Parent agent verifies push/PR separately. Next command:
`python -m unittest discover -s analysis/tests -v`. Next scientific unblock:
Owner supplies the actual box/reference inventory and authorized provenance;
the model comparison is not an isolated shield-effect or hardware verdict.

## 2026-09-06 — Main-branch placement authorized

Owner explicitly requested these PRs be merged to their respective main branches. This supersedes earlier placement-blocked/draft-only entries for the current changes. The combined main-targeted PR retains prerequisite integrity work, unchanged task ledgers and all actual hardware/disclosure gates. No CAD or experiment is marked complete. Merge completion and resulting main commit are verified by GitHub rather than asserted in advance here.

## 2026-09-06 — Reviewer-driven CAD amendment

This entry supersedes the earlier CAD allocation and readiness wording. The same CAD PR is now draft, pending the owner planning-ledger placement decision. [Review disposition](CAD_REVIEW_DISPOSITION.md) records that block; [CAD_PLAN.md](CAD_PLAN.md) and [CAD_TASKS.csv](CAD_TASKS.csv) contain revised priorities, separate tooling estimates and explicit parked work. No CAD model or new measurement was produced. Original integrity-sprint tasks/evidence remain unchanged. Next work is limited to active input-register tasks and unresolved owner decisions, not the parked portfolio-wide CAD program.

## 2026-09-06 — CAD task amendment

Added [individual CAD work orders](CAD_PLAN.md) and [CAD_TASKS.csv](CAD_TASKS.csv), separating component modeling, fixtures, inspection and release deliverables. This is planning only: no CAD or physical task is complete. The original sprint ledger and evidence are unchanged. CAD branch: `plan/cad-tasks-20260906`; the PR supplies the committed source identity. Next CAD action: the first input-register task in the CAD ledger; owner-gated successors remain blocked. Verification of this amendment is recorded in [CAD_PLAN_CHECKS.md](CAD_PLAN_CHECKS.md).

## 2026-09-05 — baseline and plan

Worktree: `/Users/redhose/Developer/research-sprints/2026-09-05/Enclosure-Research`.
Branch `sprint/evidence-integrity-20260905`; base
`c8c941dabd02541b3f3bfd67dc0edbc0517e6be9`. Initial tree clean. Original
checkout untouched. No commit/push/outreach performed.

Read the applicable execute-and-test and quality-gates skills, CONTRIBUTING,
README, CI, analysis scripts, results, and manuscript claim locations.
Baseline compile, literature coverage, and thermal execution passed. Duplicate
paired timestamp input reproduced completeness 1.5. Evidence is in
[baseline.md](../evidence/sprint-2026-09-05/baseline.md).

Saved six-day/30-hour plan and authoritative task CSV before behavior changes.
Current modifications are new sprint documentation/evidence only; running the
thermal model regenerated its existing table without a tracked numeric diff.
No type/lint command or behavioral suite exists in baseline CI; use standard
library unittest for regressions, adding no test dependency.

Next action: prepare the owner provenance request, then EN-S03 failing regression
tests after the parent presents the plan. Behavioral implementation has not begun.

## 2026-09-05 — scheduled-accounting correction

Parent presented plans and authorized continuation. Prepared owner checklist (not
sent). EN-S03 tests failed on original behavior, then EN-S04 corrected the
accounting. Fifteen regression tests and whole-analysis compile pass; see
[regressions.md](../evidence/sprint-2026-09-05/regressions.md). Existing positional
cadence-only calls now fail with an intended-window instruction. This deliberate
contract change prevents inferred edge denominators. Finite-pair accuracy remains
per observation; availability has unique delivery/sensor/paired numerators.

Next: EN-S05 deployment integration tests first. Historical field outputs remain
untouched. Branch/base unchanged; changes uncommitted.

## 2026-09-06 — software review packet

Resumed same branch/base and rechecked existing changes. Integration tests first
reproduced the missing-window crash and unconfirmed 200% rate; metadata-free
completeness is now null. Consumer tests then caught a missing-data traceback;
the exporter now reports actionable input errors before emitting files. Empty
selected windows are supported; entirely empty sources are explicitly rejected
by the full descriptive-plot exporter.

Added real unittest CI step. Compile, 24 tests, 26/26 bibliography coverage,
thermal execution, and diff checks pass. Exact outputs are in
[final-checks.md](../evidence/sprint-2026-09-05/final-checks.md). Source CLI ran
from `/private/tmp`: synthetic delivery/sensor/paired availability 0.75/0.5/0.25.
Candidate hashes and prewritten procedure preceded 12 additional deterministic
developer cases, all passing; not independent scientific evaluation.

Narrative now highlights painted control and withdraws unsupported completed
measurement, uptime, unattended-operation, and causal/exoneration language.
Historical reported figures are preserved as unverified. Raw exports, frozen
images, thermal CSV values, and rendered reports were not changed. Legacy
rendered reports are not a corrected publication package.

Bounded software lane complete; overall field-validation handoff partial.
EN-S02/09B await confirmed provenance/access and EN-S11 awaits human review.
Owner request prepared, not sent. No commits/push/publication/outreach. HEAD
remains c8c941dabd02541b3f3bfd67dc0edbc0517e6be9; nine tracked files modified plus
new tests/docs/evidence. Ledger estimates are planned hours, not claims of elapsed
calendar days. Next resume command, after checking status and reading ledger:
`python -m unittest discover -s analysis/tests -v`. Next external unblock:
[owner provenance checklist](DEPLOYMENT_PROVENANCE_REQUEST.md). No background
work is scheduled.
