# Sensor Enclosure Thermal Design

How much target-design calibration can measured geometry, material and power
data plus shared thermal laws replace? This repository has a heat-balance
model, an executed numerical correction, a literature review of its assumptions,
and a planned first-stage comparison against a reference thermometer. Transfer
to a withheld enclosure is the research direction; it has not been demonstrated.

[![CI](https://github.com/500ft/sensor-enclosure-thermal-design/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/sensor-enclosure-thermal-design/actions/workflows/ci.yml)
[![Evidence: analytical model](https://img.shields.io/badge/evidence-analytical_model-475569)](docs/results.md)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](.github/workflows/ci.yml)

[Results](#results) · [Roadmap](ROADMAP.md) · [Quick start](#quick-start) ·
[Pilot protocol](docs/COLOCATION_PROTOCOL.md)

![Modelled temperature and relative-humidity bias for the dark box, painted box and passive shield under solar loading](analysis/figures/thermal_bias.png)

*Model output, not a field measurement.
[Figure inputs](docs/data-and-figures.md#thermal-bias-plot).*

## About

An outdoor sensor can end up measuring its own enclosure instead of the air.
Sunlight heats the walls, still air traps the heat, and the electronics inside
add their own. The error changes with time of day, so a single midday check can
mislead.

The project compares enclosure options with a first-order heat-balance model,
checks the model's constants against the literature, and prepares a
co-location pilot: the enclosures mounted next to a reference thermometer for
at least a full day and night. The PI has approved the pilot in principle and offered a test
site and manufacturing help.

## Results

At 1000 W/m² of sun and 0.5 m/s of wind, the model gives these nominal point
estimates of temperature rise above ambient:

| Enclosure | Predicted rise |
| --- | --- |
| Dark closed box | 19.4 °C |
| Same box, painted white | 4.5 °C |
| Passive radiation shield | 3.0 °C |

At this operating point, changing the dark box's absorptance to the white-paint
assumption accounts for most of the predicted reduction. The shield's nominal
bias is about 1.5 °C lower than the painted box's. Geometry, internal heat load
and airflow also differ between these systems.
[Prediction table](analysis/output/thermal_bias_table.csv).

The shield-versus-painted-box ranking reverses when the documented sensitivity
settings for poorer shading, reduced convection and increased plate-air preheat
are applied together. These settings are illustrative, and this model comparison
establishes no design preference.
[Sensitivity results and assumptions](analysis/thermal_bias_results.md),
[calculation](analysis/matched_control_sensitivity.py).
At night the modelled bias can change sign, which is why the pilot covers both
day and night.

The [corrected transient calculation](docs/results.md#transient-result-on-hold)
stores its initial state at the right time, conserves hourly solar input and
passes exact thermal-step and timestep-refinement checks. Its figure shows a
clear-sky assumption and sensitivity to declared inputs. Missing acquisition
metadata and actual sky forcing limit interpretation; parent review remains on
HOLD. No physical accuracy or design-transfer result has been obtained.

![Corrected thermal sensitivity under the clear-sky assumption](analysis/figures/thermal_transient_prediction.png)

*Archived hourly forcing with a stated sky scenario, not rig measurements.
[Inputs, method and reproduction](docs/data-and-figures.md#transient-prediction-plot).*

Other work in the repository:

- **Literature.** A [26-source matrix](literature/literature_matrix.csv) with
  [source assessments](ProConsList/README.md), and a later review of 27 more
  sources against the model's previously uncited constants.
- **Uncertainty.** The steady tables are point estimates. The transient
  draft carries sensitivity bands from assumed uniform ranges by Monte Carlo. The
  standalone [linear propagation module](analysis/uncertainty.py) is tested but
  not connected to either.
- **Reliability accounting.** [Schedule-aware metrics](docs/RELIABILITY_METRICS.md)
  for deployed units. The historical percentages need raw exports that are not
  in this repository, so they are reported but unverified.
- **CAD.** The baseline enclosure is parametric and was accepted against an
  independent closed-form check of volume, bounding box and STEP re-import.

## Quick start

Python 3.12, the CI version. These checks use only files in the repository.

```bash
git clone https://github.com/500ft/sensor-enclosure-thermal-design.git
cd sensor-enclosure-thermal-design
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m compileall -q analysis
PYTHONPATH=. python -m unittest discover -s analysis/tests -v
python analysis/check_literature_coverage.py
```

To regenerate the model tables without overwriting the committed ones:

```bash
OUT_DIR="$(mktemp -d)"
python analysis/thermal_bias.py --no-figure \
  --table "$OUT_DIR/thermal-day.csv" \
  --night-table "$OUT_DIR/thermal-night.csv"
diff -u analysis/output/thermal_bias_table.csv "$OUT_DIR/thermal-day.csv"
diff -u analysis/output/thermal_bias_night_table.csv "$OUT_DIR/thermal-night.csv"
```

No diff means the tables reproduce in your environment. The
[reading guide](docs/START_HERE.md#reviewer-reproduce-the-contained-analysis)
covers external-data prerequisites and the intake checker.

## What's next

The [external-data suitability result](analysis/aqspec_feasibility.md) records
the AQ-SPEC access probe and missing inputs for a temperature comparison. The
[roadmap](ROADMAP.md) now starts with review of the corrected transient result.
An eligible external comparison remains a possible supporting route.

The thermal co-location campaign has not run. Direction B remains the approved
first-stage estimation-only scope. The owner has adopted the direction toward
geometry/calibration transfer; PI agreement on designs or acceptance remains
open. The
[blocker record](docs/COLOCATION_OWNER_SESSION.md#current-blocker) holds current
funding, rig and decision status. The [roadmap](ROADMAP.md) retains mandatory-first
I1. Freeze the model and processing before outcomes; future measured weather
will drive predictions under that procedure once it exists.

## Limits

- The published steady model is lumped; the transient extension remains on HOLD. One 24-hour campaign would not
  establish seasonal accuracy.
- The pilot protocol is a draft until it is frozen with its approver and date.
  Its data-quality targets are proposals, and the model's day and night
  scenarios are not acceptance limits.
- The intake checker catches malformed data. It cannot prove where data came
  from, and a file that passes it is not a thermal validation.

## Documentation

| Document | What it covers |
| --- | --- |
| [Reading guide](docs/START_HERE.md) | Where to start |
| [Results](docs/results.md) | What is modelled, provisional or unavailable |
| [Data and figures](docs/data-and-figures.md) · [manifest](docs/figure-manifest.json) | Where each plot and input came from |
| [Model assumptions](analysis/thermal_bias_results.md) | Geometry, radiation and convection terms |
| [Pilot protocol](docs/COLOCATION_PROTOCOL.md) | What the side-by-side test measures |
| [Owner decisions](docs/OWNER_DECISIONS_2026-09-24.md) | Open questions for the pilot |
| [Working manuscript](paper/manuscript_v1.md) | Literature and analysis written up |
| [CAD/FEA plan](docs/cad_fea_plan.md) | Proposed geometry and higher-fidelity work |

```text
analysis/      thermal and reliability models, intake checks, tests and figures
literature/    source matrix and design comparisons
ProConsList/   per-source assessments
paper/         working manuscript and bibliography
templates/     record templates for baselines, deployments and calibration
docs/          methods, results and protocols
evidence/      recorded checks
```

## Contributing and reuse

Read [CONTRIBUTING.md](CONTRIBUTING.md). Literature changes must keep the
bibliography, matrix, assessments and synthesis in sync. Analysis changes need
a reproduction, units, input sources and tests.

There is no open-source license yet; contact the owner about reuse or about
the nonpublic data. When referencing the work, give the commit and say that
the results are modelled. The project's earlier name is explained in the
[identity note](docs/REPOSITORY_IDENTITY.md).
