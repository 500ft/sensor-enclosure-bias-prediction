# Review index

What to review, and where each piece of evidence lives. The plan is in the
[roadmap](../ROADMAP.md), the history in the [progress log](SPRINT_PROGRESS.md)
and the current blocker in the
[owner session record](COLOCATION_OWNER_SESSION.md#current-blocker). The
earlier, longer version of this index is kept at
[commit 4d1134e](https://github.com/500ft/sensor-enclosure-thermal-design/blob/4d1134ecf598f0abd53161d3339fb0fd5576eadf/docs/REVIEW_READY.md).

Nothing here has had an independent review, and nothing has been measured.

## Review now

1. **The pilot protocol** ([protocol](COLOCATION_PROTOCOL.md),
   [design](specs/pilot-readiness/pilot-design-2026-09-24.md),
   [experiment contract](specs/pilot-readiness/experiment-contract-2026-09-24.md)).
   This is what the PI's test will follow once it is frozen. Worth checking:
   whether 120 sunny and 120 dark minutes and a paired U95 of 0.5 °C are the
   right bar, and whether the reference-thermometer setup is realistic.
2. **The model comparison** ([results](results.md),
   [assumptions](../analysis/thermal_bias_results.md)). Dark box 19.4 °C,
   painted 4.5 °C, shield 3.0 °C at 1000 W/m² and 0.5 m/s. The night case can
   change sign.
3. **The 09-24 corrections**
   ([critique response in the progress log](SPRINT_PROGRESS.md#week-of-2026-09-21)).
   Three claims were withdrawn; check that none survives in a live document.

## Reproduce

Run the [README quick start](../README.md#quick-start) and the table
comparison under it. The [reading guide](START_HERE.md#reviewer-reproduce-the-contained-analysis)
has the full sequence.

## Evidence records

| Folder | What it holds |
| --- | --- |
| [task-week-2026-09-21](../evidence/task-week-2026-09-21/README.md) | Week of 2026-09-21 packet: consistency review, gate set, evidence (F1–F4) |
| [week-2026-09-21](../evidence/week-2026-09-21/baseline.md) | Day-by-day notes for that week ([day 2](../evidence/week-2026-09-21/day2.md), [day 3](../evidence/week-2026-09-21/day3.md)) |
| [task-2026-09-16](../evidence/task-2026-09-16/README.md) | Evidence-preservation fix, ledger reconciliation, sensitivity screen |
| [plan-review-2026-09-14](../evidence/plan-review-2026-09-14/README.md) | Review of the replacement 09-15 plan |
| [task-2026-09-12](../evidence/task-2026-09-12/README.md) | Synthetic CSV-to-analysis rehearsal |
| [presentation-2026-09-10](../evidence/presentation-2026-09-10/README.md) | README presentation checks |
| [review-2026-09-09](../evidence/review-2026-09-09/README.md) | Review of the night-case interpretation |
| [task-2026-09-09](../evidence/task-2026-09-09/README.md) | Night clear-sky case: a −4.0 °C bias for the baseline box |
| [task-day3-2026-09-09](../evidence/task-day3-2026-09-09/README.md) | Intake checker tests |
| [task-2026-09-08](../evidence/task-2026-09-08/verification.md) | Painted closed-box control |
| [sprint-2026-09-05](../evidence/sprint-2026-09-05/) | First integrity sprint baseline |
