# Enclosure software review packet — partial field-validation handoff

## Day-3 preparation — 2026-09-09

Ten new synthetic intake tests cover full-day versus partial exposure, duplicate slots, missing paired data, invalid timestamps/weather/uncertainty/provenance and the actual CLI raw-hash boundary. 48 analysis tests pass. A sufficient synthetic CSV exits 3; tampered raw bytes exit 2. No physical pilot or model validation occurred. A further non-object JSON metadata counterexample reproduced a traceback; the CLI now returns diagnostic exit 2 for null/list/string metadata.

Review [DAY3_PLAN.md](https://github.com/500ft/sensor-enclosure-thermal-design/blob/ddf0a23098964ecfd036e32105dfa9564adc4ea7/docs/DAY3_PLAN.md), [deliverable](COLOCATION_PROTOCOL.md), and [commands/evidence](../evidence/task-day3-2026-09-09/README.md). Base: `c121f2bb3f247220df39dffd552468678254bbc8`; new PR branch: `task/day-three-20260909`. No original Owner/External gate is closed. Final source identity is the PR head, reported in its delivery record rather than embedded circularly here.

Actual site/equipment identification, PI/data permission and measurements cannot be supplied by web research.

## Review amendment — 2026-09-09

Read [the reproduced findings, corrections and current checks](../evidence/review-2026-09-09/README.md)
before the historical day-2 counts below. Review branch `review/day-two-20260909`;
amendment targets the existing day-2 PR, not main. No owner/measurement gate closes.


## 2026-09-09 addendum — night clear-sky case (EN-D02)

The existing solver at G = 0 with unchanged assumptions predicts a **-4.0 °C cold bias** for the
baseline box in calm clear-sky night, against the midday warm bias above: the enclosure error is
sign-changing over the diurnal cycle, so a field co-location needs 24 h coverage. Daytime table and
figure are byte-unchanged; six new tests assert sign and ordering only. Still SIMULATION / pending lab
data. [Verification](../evidence/task-2026-09-09/README.md).

## 2026-09-08 addendum — matched-finish thermal control

New task EN-D01 uses base `199cb5d38bc70af271b4e064d79d4d8415ff4630` and
branch `task/priority-one-20260908`. Source identity is the addendum's containing
commit / PR head, not the older candidate manifest below. See
[task verification](../evidence/task-2026-09-08/verification.md) for five red/green
regressions, all 29 tests, consumer CLI/figure checks and artifact hashes.
`V0P` is a new variant ID and adds ten CSV rows; all thirty legacy rows remain
unchanged. These are analytical controls, not new field measurements. The
historical review packet below remains the record of the earlier integrity sprint.


Prepared 2026-09-06; sprint began 2026-09-05. Repository:
`/Users/redhose/Developer/research-sprints/2026-09-05/Enclosure-Research`, remote
`https://github.com/500ft/Enclosure-Research.git`.
Base `c8c941dabd02541b3f3bfd67dc0edbc0517e6be9`; branch
`sprint/evidence-integrity-20260905`. Final commit: this packet's containing
commit (reported in the PR; not self-embedded).
Source identity: [candidate SHA-256 manifest](../evidence/sprint-2026-09-05/candidate.json).
This is source-distributed CLI work, not a published package or deployment.

## Plan and evidence

- [Six-day / 30-hour roadmap](https://github.com/500ft/sensor-enclosure-thermal-design/blob/1ed27b40395122bf3b2e63fa3981b73d851e6d31/docs/SPRINT_ROADMAP.md)
- [Authoritative task ledger](SPRINT_TASKS.csv)
- [Progress and exact next command](SPRINT_PROGRESS.md)
- [Baseline, runtime, and complete 150% reproduction](../evidence/sprint-2026-09-05/baseline.md)
- [Test-first red/green evidence](../evidence/sprint-2026-09-05/regressions.md)
- [Final commands, statuses, and retained outputs](../evidence/sprint-2026-09-05/final-checks.md)
- [Actual external-working-directory consumer CLI proof](../evidence/sprint-2026-09-05/consumer-output.md)

## Must-have acceptance evidence

| Deliverable | Evidence | Boundary |
|---|---|---|
| Unique schedule accounting; explicit edges/cadence; duplicate/off-grid diagnostics | [metric tests](../analysis/tests/test_compute_metrics.py), [contract](RELIABILITY_METRICS.md) | Software checks do not confirm deployment intent |
| Separate delivery/sensor/pair availability and unchanged paired-row residual meaning | [consumer output](../evidence/sprint-2026-09-05/consumer-output.md) | Availability is unique slots; accuracy is paired observations; neither is uptime |
| Unavailable completeness without provenance; empty selected windows; clear missing-source errors | [deployment tests](../analysis/tests/test_deployment_metrics.py), [CLI tests](../analysis/tests/test_metrics_cli.py) | Whole empty plot-source logs explicitly rejected; no private replay |
| Painted control and corrected evidence narrative | [results](results.md), [sensitivity](../analysis/thermal_bias_results.md), [manuscript](../paper/manuscript_v1.md) | 19.4/4.5/3.0°C analytical; legacy rendered reports not regenerated |
| Behavioral tests in actual workflow | [CI](../.github/workflows/ci.yml), [local results](../evidence/sprint-2026-09-05/final-checks.md) | No remote Actions run claimed |

Intentional API changes: cadence-only compute_metrics calls now require intended
start/end or raise ValueError; CLI invalid/incomplete schedules exit 2. read_rows
retains timestamped records missing a channel. Generic completeness aliases
paired availability; exporter completeness_pct means delivery availability.
Definitions, missing-data states, and timestamp matching are in
[RELIABILITY_METRICS.md](RELIABILITY_METRICS.md).

## Reproduce

The primary agent independently reran the delegated software checks on2026-09-06:
[actual rerun record](../evidence/sprint-2026-09-05/parent-verification.json).
This is additional software verification, not independent human or physical validation.

From checkout root with Python 3.11 and requirements installed:

```bash
python -m compileall -q analysis
python -m unittest discover -s analysis/tests -v
python analysis/check_literature_coverage.py
python analysis/thermal_bias.py --no-figure
python evidence/sprint-2026-09-05/evaluate_candidate.py
git diff --check
```

Observed: 24 tests pass; bibliography 26/26; thermal runs; four candidate hashes
match; 12/12 additional developer cases pass. No configured type/lint command.
Complete historical field reproduction is not possible from this clone alone.

## Evaluation and pending feedback

[Selection/original expectations](../evidence/sprint-2026-09-05/evaluation-procedure.md)
preceded [additional outputs](../evidence/sprint-2026-09-05/evaluation.md). No
disagreements occurred. Same-developer deterministic cases are not an independent
scientific evaluation; hashes establish identity only. Human feedback is pending.
No physical experiment, private import, or corrected publication package occurred.

## Incomplete work / three remaining priorities

1. EN-S02/09B: confirmed window, cadence, timezone, device/reset semantics, and
   authorized logs; reconcile historical 91.4% in a new versioned campaign.
   [Prepared, unsent owner request](DEPLOYMENT_PROVENANCE_REQUEST.md).
2. Physical baseline/reference co-location: measure matched-finish controls and
   uncertainty before claiming a hardware shielding advantage.
3. EN-S11: independent human/source review, then deliberately regenerate any
   corrected rendered publication package and decide commit/PR disposition.

Evidence-supported project bullet: “Built and regression-tested schedule-aware
sensor-log analysis that separates delivery, valid sensing, and reference-paired
availability while preventing duplicate-row inflation.” This states engineering
quality, not adoption or measured field performance.

Review Enclosure-Research against docs/SPRINT_ROADMAP.md. Repository:
/Users/redhose/Developer/research-sprints/2026-09-05/Enclosure-Research. Base commit:
c8c941dabd02541b3f3bfd67dc0edbc0517e6be9. Final commit: PR head (see GitHub PR). Review index:
docs/REVIEW_READY.md. Incomplete work: confirmed deployment metadata and authorized
field rerun, physical reference comparison, independent human review, publication
package regeneration. Reproduce the changed behaviors and counterexamples, rerun
appropriate checks, and assess the code and evidence independently. Review first;
make further changes only if requested.
