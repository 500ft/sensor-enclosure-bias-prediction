# Start here — Sensor Enclosure Thermal Design

## Recruiter or prospective supervisor

Read the [results](../README.md#results), compare the
[dark, painted and shielded variants](../analysis/thermal_bias_results.md), then
inspect the [co-location protocol draft](COLOCATION_PROTOCOL.md).

The present contribution is source-linked design comparison and tested
reliability/intake tooling—not an experimentally validated enclosure.

## Reviewer: reproduce the contained analysis

Follow the [README environment setup](../README.md#quick-start), from the root.
Use Python 3.11 and record the installed dependency versions; requirements are
not a complete transitive environment lock.

```sh
git rev-parse HEAD
python --version
python -m compileall -q analysis
PYTHONPATH=. python -m unittest discover -s analysis/tests -v
python analysis/check_literature_coverage.py
```

The tests use synthetic fixtures and repository-contained model inputs.
Bibliography coverage checks consistency across the 26 entries; it does not
prove that a literature review is exhaustive.

The [README table comparison](../README.md#quick-start) regenerates both day and
night CSVs into a temporary directory. No diff means the current model output
reproduced—not that the physical model is correct. The [CI workflow](../.github/workflows/ci.yml)
runs the same comparison. [Figure provenance](data-and-figures.md) records the
existing plot's generator and inputs.

## Understand the pilot intake

The [protocol](COLOCATION_PROTOCOL.md) is a **draft**, not an approved experiment.
No real co-location CSV exists in this repository.

```sh
PYTHONPATH=. python -m unittest discover -s analysis/tests -p test_colocation_intake.py -v
```

| Intake outcome | Exit | Meaning |
| --- | --- | --- |
| Malformed or incomplete input | 2 | Does not meet the registered intake structure/quality rules |
| Sufficient synthetic data | 3 | Developer fixture only; cannot become physical evidence |
| Physical-labeled pilot | 0 | Eligible for human provenance review, not authenticated or validated |

The checks bind CSV bytes to metadata and cover the planned schedule, duplicates,
missing channels, exposure coverage, timestamp validity and uncertainty fields.
A string claiming permission or calibration does not prove either occurred.
See the [implementation](../analysis/colocation_intake.py) and
[tests](../analysis/tests/test_colocation_intake.py).

The model's example night/day biases are not acceptance bands. Actual model
agreement needs an as-built prediction, propagated uncertainty and an
application tolerance fixed before observations.

## External deployment-log analysis

The historical raw exports and deployment history are outside this repository.
Use the [provenance request](DEPLOYMENT_PROVENANCE_REQUEST.md) before attempting
to reproduce historical percentages. A source unavailable to a reviewer is
not treated as a successful reproduction.

[Reliability definitions](RELIABILITY_METRICS.md) separate scheduled
completeness, continuity and channel availability. These are delivery metrics,
not sensor accuracy. Do not fabricate acquisition windows or silently replace
historical percentages with a different denominator.

## Contributor route

Read [Contributing](../CONTRIBUTING.md). Keep [bibliography](../paper/references.bib),
[literature matrix](../literature/literature_matrix.csv), source assessments
and synthesis synchronized. Preserve units and uncertainty in model changes.

The [review index](REVIEW_READY.md) is the evidence entry point. The
[CAD/FEA plan](cad_fea_plan.md) and [pilot draft](COLOCATION_PROTOCOL.md) describe
future work without claiming it exists. No open-source license is included;
this guide grants no new reuse or disclosure permission.

See [repository identity](REPOSITORY_IDENTITY.md) for the rename and formatting references.

## September 11 completion correction

Read the [item-by-item correction](specs/evidence-gap-correction/test-report.md) before interpreting a prepared protocol, software check, or search export as a completed research gate. It identifies actual deliverables and the remaining measurement, review, or source-reading work separately.
