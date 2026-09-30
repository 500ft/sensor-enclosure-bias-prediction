# Sensor Enclosure Thermal Design

How much does an outdoor sensor enclosure bias the temperature it reports,
and which enclosure is worth the extra cost? This repository has a heat-balance
model that compares enclosure designs, a literature review of its assumptions,
and a planned side-by-side test against a reference thermometer.

[![CI](https://github.com/500ft/sensor-enclosure-thermal-design/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/sensor-enclosure-thermal-design/actions/workflows/ci.yml)
[![Evidence: analytical model](https://img.shields.io/badge/evidence-analytical_model-475569)](docs/results.md)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](.github/workflows/ci.yml)

[Results](#results) · [Roadmap](ROADMAP.md) · [Quick start](#quick-start) ·
[Pilot protocol](docs/COLOCATION_PROTOCOL.md)

![Illustration comparing a closed sensor box, a passive shield, and an aspirated shield](docs/media/hero.jpg)

*Concept illustration (AI-generated). All results below are model predictions.*

## About

An outdoor sensor can end up measuring its own enclosure instead of the air.
Sunlight heats the walls, still air traps the heat, and the electronics inside
add their own. The error changes with time of day, so a single midday check can
mislead.

The project compares enclosure options with a first-order heat-balance model,
checks the model's constants against the literature, and prepares a
co-location pilot: the enclosures mounted next to a reference thermometer for
at least a full day and night. The PI has approved the pilot and offered a test
site and manufacturing help.

## Results

At 1000 W/m² of sun and 0.5 m/s of wind, the model predicts these temperature
rises above ambient:

| Enclosure | Predicted rise |
| --- | --- |
| Dark closed box | 19.4 °C |
| Same box, painted white | 4.5 °C |
| Passive radiation shield | 3.0 °C |

Most of the improvement comes from the white paint. The shield adds about
1.5 °C on top of paint, not the 16.4 °C the dark-box comparison suggests. The
two designs also differ in geometry and airflow, so this compares systems, not
shielding alone. At night the modelled bias can change sign, which is why the
pilot has to cover both.
[Source and interpretation](docs/results.md#thermal-bias-model).

![Analytical enclosure temperature and relative-humidity bias under solar loading](analysis/figures/thermal_bias.png)

*Model output, not a field measurement. [Figure inputs](docs/data-and-figures.md#thermal-bias-plot).*

Other work in the repository:

- **Literature.** A [26-source matrix](literature/literature_matrix.csv) with
  [source assessments](ProConsList/README.md), and a later review of 27 more
  sources against the model's previously uncited constants.
- **Uncertainty.** Input uncertainty is propagated through the model to the
  prediction.
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

The owner reports an existing co-location setup with logged data. The next
step is finding those logs and reviewing them against the protocol; a new
24-hour run is only needed for whatever they don't cover. The
[roadmap](ROADMAP.md) has the steps, and the
[blocker record](docs/COLOCATION_OWNER_SESSION.md#current-blocker) has the
current status.

## Limits

- The model is lumped and steady-state. One 24-hour campaign would not
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
