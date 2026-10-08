# Preserved research history

The [roadmap](../../ROADMAP.md) holds the current geometry/calibration-transfer
direction and first-stage estimation study. These records retain earlier work;
they do not add active questions or establish that a proposed study was run.

- [Earlier question exercise](https://github.com/500ft/sensor-enclosure-thermal-design/blob/2beffdf412e57145062994e5626863de80438016/docs/research-question-draft.md) and
  [dated direction record](../research-direction-2026-09-21.md).
- [Earlier deployment and electronics evidence](../data-and-figures.md#deployment-log-plots),
  [reliability accounting](../RELIABILITY_METRICS.md) and the broader historical
  context retained in [the manuscript](../../paper/manuscript_v1.md).
- [CAD assets and accepted checks](../START_HERE.md), retained at their original paths.
- [Original PR #56 source, tests, weather and outputs at cdd26ba](https://github.com/500ft/sensor-enclosure-thermal-design/tree/cdd26ba6d9c535156a17fb68c3546f20e10cac20/analysis).
  Its transient output/figure are superseded by the corrected calculation; the
  raw weather bytes and steady tables are unchanged. The earlier sky attribution,
  time handling and uncertainty labels must not be reused as current findings.

Dated day plans and sprint logs are history. No data, CAD or calibration asset
was deleted as part of the v2 reconciliation.

## Removed work queues and unused code

The owner-authorized dependency cleanup removed these active files. Their last
versions remain at [the pre-cleanup commit](https://github.com/500ft/sensor-enclosure-thermal-design/tree/2beffdf412e57145062994e5626863de80438016).

| Removed paths | Reason and retained material |
|---|---|
| `analysis/cad_fea/thermal_fea_pipeline.py`, `analysis/cad_fea/README.md` | The CLI performed no solve; solver stages were unimplemented and had no runtime or test consumers. The steady/transient models and their verification remain. |
| `docs/CAD_PLAN.md`, `docs/CAD_TASKS.csv`, `docs/CAD_DEPENDENCIES.json`, `docs/CAD_PLAN_CHECKS.md` | Retired work orders, an empty dependency map and its document-only validator. Geometry, build/oracle code, accepted checks and the dated owner disposition remain. |
| `docs/cad_fea_plan.md`, `docs/specs/cad-development/scope.md` | Superseded CAD/FEA workstreams. Useful variant and input definitions now live in the [geometry reference](../cad_geometry_reference.md); scientific CHT methods/corrections remain in [the methods reference](../specs/study-b-cht/design.md). |
| `docs/specs/pilot-readiness/scope.md`, `docs/specs/evidence-gap-correction/plan.md` | Competing execution plans. The current protocol, owner decisions and [executed correction checks](../specs/evidence-gap-correction/test-report.md) remain. |
| `docs/research-question-draft.md`, `docs/lab-meeting-research-question-2026-09-21.txt` | Superseded question/proposal drafts. The dated direction record, literature corrections and decision provenance remain. |

Markdown references to removed documents point to that immutable commit.
Old paths in executed logs and ledger rows describe historical work.

## Retained for reproduction and provenance

- Steady and corrected transient source, tests, weather/source records, numerical
  outputs and figures remain at their original paths. The sensitivity and
  nondimensional calculations preserve model limitations and ranking corrections.
- CAD source, geometry, independent oracle, acceptance records, parameter register
  and calibration/input templates remain useful to qualify actual specimens.
- Deployment/electronics evidence, manuscript, report generators and their
  dependencies remain together so retained deliverables can be reproduced.
- `SPRINT_TASKS.csv` remains an executed ledger, not an active queue. Existing
  tests use it to distinguish the blocked physical campaign from its completed
  synthetic rehearsal. Dated day plans and progress logs preserve that context.
- The uncertainty and intake/metrics code, CHT methods and software contracts retain
  scientific and leakage corrections. Their presence does not authorize new work;
  [ROADMAP.md](../../ROADMAP.md) controls activation.

No raw data, frozen evaluation inputs, calibration records, executed numerical
results or scientific figures were removed. Valid CI jobs and dependencies remain
because they still serve retained code and deliverables.
