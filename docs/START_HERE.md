# Start here — Sensor Enclosure Bias Prediction

The [README](../README.md) is the overview and the [roadmap](../ROADMAP.md) is
the only plan. It states prerequisites and completion evidence without a
schedule. This guide is for reading the work quickly or rerunning it.

## Two-minute read

Start with the [model results](../README.md#results), then compare the
[dark box, painted control and vented shield](../analysis/thermal_bias_results.md).
The [protocol](COLOCATION_PROTOCOL.md) defines their proposed physical comparison.
The repository also contains a literature review, tested intake and reliability
code, and older deployment and electronics work. The thermal co-location
campaign has not run. The PI approved it in principle; the [current equipment
record](COLOCATION_OWNER_SESSION.md#current-blocker) lists what is still needed.
Read the [transient result and its limits](results.md#transient-result) before
using its outputs. The first field stage will estimate bias and uncertainty.
The [decision history](OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions)
records the later geometry-transfer direction and unanswered questions.

The [protocol setup table](COLOCATION_PROTOCOL.md#r12-enclosures-and-reference)
defines V0, V0P and V1 as the proposed physical arms; the README also plots an
aspirated model case, V2. The [intervention table](COLOCATION_PROTOCOL.md#c2-intervention-matrix)
defines I1 through I6 and the quantity each comparison estimates. The
[parameter register](PARAMETER_REGISTER.csv) defines `P-` input IDs, units and
evidence status. For example, `P-QINT-V0` names the modeled heat reaching the
V0 sensor, while `P-PHI` names the shield's assumed solar factor. Neither has
been measured for the planned rig.

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
[geometry reference](cad_geometry_reference.md) retains useful CAD inputs and
checks. There is no open-source license, and this guide grants no reuse permission.

The [repository identity note](REPOSITORY_IDENTITY.md) explains the rename.
The September 11 [correction](specs/evidence-gap-correction/test-report.md)
explains which early deliverables were preparation rather than finished work.

## Retired work queues

The unused FEA stub, competing CAD work orders and obsolete campaign/question
plans were removed after tracing their consumers. [History](history/README.md)
links their prior versions and explains retained reproducible evidence. Use the
roadmap for active work, not the older sprint ledger or dated proposals.
