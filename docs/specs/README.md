# Specifications

A plain index of the files in this folder. For the current plan, read the
[roadmap](../../ROADMAP.md). The pilot protocol itself is
[docs/COLOCATION_PROTOCOL.md](../COLOCATION_PROTOCOL.md); the two pilot specs
below are its detailed companions and will be folded into it when it is frozen.
Dated records and finished plans keep their original wording, because they
describe what was true or intended at the time.

## In use: the pilot

| File | What it is |
| --- | --- |
| [pilot-readiness/pilot-design-2026-09-24.md](pilot-readiness/pilot-design-2026-09-24.md) | The three enclosure variants, the data schema and custody, and the uncertainty budget. Its data-quality thresholds are quoted from the protocol |
| [pilot-readiness/experiment-contract-2026-09-24.md](pilot-readiness/experiment-contract-2026-09-24.md) | Which temperatures to measure, which claims need a controlled intervention (such as switching the electronics' power) and which stay correlations, the calibration plan and the stopping rule |
| [implementation-tickets-2026-09-24.md](implementation-tickets-2026-09-24.md) | Software tickets for the pilot. T2 (uncertainty propagation) is done; T1 (campaign manifest) is built on a kept branch and waits for the first real data |

## Later work

| File | What it is |
| --- | --- |
| [study-b-cht/design.md](study-b-cht/design.md) | Design for a conjugate-heat-transfer model. Only needed if the pilot disagrees with the lumped model by more than its uncertainty |
| [cad-unattended-run-contract-2026-09-25.md](cad-unattended-run-contract-2026-09-25.md) | What an unattended CAD run on the host would need; nothing was run |

## Records and finished plans

| File | What it records |
| --- | --- |
| [evidence-gap-correction/test-report.md](evidence-gap-correction/test-report.md) | The 2026-09-11 correction of what earlier work had and had not finished |
| [evidence-gap-correction/plan.md](evidence-gap-correction/plan.md) | Scope of that correction |
| [pilot-readiness/scope.md](pilot-readiness/scope.md) | Scope for the 2026-09-15 workday |
| [cad-development/scope.md](cad-development/scope.md) | Early CAD scope |
