# Start here — Sensor Enclosure Thermal Design

The [README](../README.md) is the overview and the [roadmap](../ROADMAP.md) is
the plan. This guide is for reading the work quickly or rerunning it.

## Two-minute read

Read the [README results](../README.md#results), compare the
[dark, painted and shielded variants](../analysis/thermal_bias_results.md), then
look at the [pilot protocol](COLOCATION_PROTOCOL.md). So far the project has a
model comparison, a literature check of its constants, and tested intake and
reliability code. The thermal campaign has not run; older deployment and
electronics work is retained below. PI approval is in principle, and campaign
readiness follows the [current blocker](COLOCATION_OWNER_SESSION.md#current-blocker).
Read the [PR #56 hold](results.md#transient-result-on-hold) before using its
transient outputs. Direction B remains approved; the proposed switch is pending
in [E1-E4](OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions).

## Reviewer: reproduce the contained analysis

Set up as in the [README](../README.md#quick-start), using Python 3.12 (the CI
version). Record the dependency versions you get, because the requirements
pin direct packages only.

```sh
git rev-parse HEAD
python --version
python -m compileall -q analysis
PYTHONPATH=. python -m unittest discover -s analysis/tests -v
python analysis/check_literature_coverage.py
```

The tests use synthetic fixtures and the model inputs in the repository. The
coverage check confirms the bibliography, matrix and assessments agree; it
doesn't show the review is complete.

The [table comparison in the README](../README.md#quick-start) regenerates the
day and night tables into a temporary folder. No diff means the model output
reproduced, not that the model is right. CI runs the same comparison, and the
[figure guide](data-and-figures.md) lists each plot's generator and inputs.

## The pilot intake

The [protocol](COLOCATION_PROTOCOL.md) is still a draft, and no real
co-location data is in the repository yet.

```sh
PYTHONPATH=. python -m unittest discover -s analysis/tests -p test_colocation_intake.py -v
```

| Result | Exit code | Meaning |
| --- | --- | --- |
| Malformed or incomplete | 2 | Fails the intake structure or quality rules |
| Enough synthetic data | 3 | A test fixture; it can never count as physical evidence |
| A physical pilot | 0 | Ready for a person to check its provenance; not authenticated and not a validation |

The checker ties the CSV bytes to the metadata and checks the schedule,
duplicates, missing channels, sun and dark coverage, timestamps and the
uncertainty field. A metadata string saying permission or calibration exists
doesn't prove it does. See the [code](../analysis/colocation_intake.py) and
[tests](../analysis/tests/test_colocation_intake.py).

## Historical deployment logs

The raw exports and deployment history behind the historical reliability
percentages are outside this repository. Use the
[provenance request](DEPLOYMENT_PROVENANCE_REQUEST.md) before trying to
reproduce them. The [reliability definitions](RELIABILITY_METRICS.md) keep
scheduled completeness, continuity and channel availability apart; they
measure data delivery, not sensor accuracy.

## Contributing

Read [CONTRIBUTING.md](../CONTRIBUTING.md). Keep the
[bibliography](../paper/references.bib), the
[literature matrix](../literature/literature_matrix.csv), the source
assessments and the synthesis in sync, and keep units and uncertainty in any
model change. The [review index](REVIEW_READY.md) lists the evidence; the
[CAD/FEA plan](cad_fea_plan.md) describes future work. There is no open-source
license, and this guide grants no reuse permission.

The [repository identity note](REPOSITORY_IDENTITY.md) explains the rename.
The September 11 [correction](specs/evidence-gap-correction/test-report.md)
explains which early deliverables were preparation rather than finished work.
