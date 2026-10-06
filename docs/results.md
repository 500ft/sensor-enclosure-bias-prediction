# Results

This page collects the current outputs. It separates deployment-log observations
from analytical predictions because they have different evidence sources and
validation requirements.

## Deployment-log reliability

The first audit uses two CSV exports stored outside this repository. The outdoor
window is inferred from the internal temperature and humidity signature and
still needs confirmation against the deployment record.

For the provisional 22-day outdoor window in Log A, the manuscript reports:

| Metric | Result |
| --- | ---: |
| Upload success | 95.7% |
| Data completeness | 91.4% |
| Brownout resets | 0 |

These values describe delivery and continuity, not measurement accuracy. A
reference co-location dataset is still required for accuracy and calibration
claims.

**Accounting correction, 2026-09-05:** the numbers above are historical,
reported-but-unverified outputs retained for traceability. The former estimator
counted rows over an observed span and unconfirmed six-minute cadence; duplicate
rows and missing edge intervals could inflate completeness. The revised code
requires an explicit intended schedule and counts unique occupied slots. No
revised field percentage has been computed without the private exports and
confirmed provenance. Upload success is a fraction of received records, not
end-to-end delivery probability or wall-clock uptime. See
[metric definitions](RELIABILITY_METRICS.md) and the
[prepared provenance request](DEPLOYMENT_PROVENANCE_REQUEST.md).

| Deployment window | Battery voltage by record outcome |
| --- | --- |
| ![Internal temperature and provisional deployment window](../analysis/figures/deployment_temp_window.png) | ![Battery voltage distributions](../analysis/figures/deployment_battv_outcome.png) |

![Daily brownout-reset fraction](../analysis/figures/deployment_daily_brownout.png)

The full audit script defines brownout rows, successful posts, missing-value
sentinels, environmental QC flags, and the operational-row filter. Raw CSVs are
not included, so another user cannot independently regenerate these field plots
without obtaining the source exports.

## Thermal-bias model

The [committed day table](../analysis/output/thermal_bias_table.csv) contains
nominal point estimates for the dark box, painted control and shield variants.
The [model interpretation](../analysis/thermal_bias_results.md) records their
assumptions and the combined sensitivity settings that reverse the shield's
nominal advantage over the painted box. Geometry, heat coupling and airflow
differ across those systems, so this comparison establishes no design preference.

![Predicted thermal and relative-humidity bias](../analysis/figures/thermal_bias.png)

The table and figure omit propagated input uncertainty. The standalone
[uncertainty module](../analysis/uncertainty.py) is not connected to them.
These are analytical outputs; no physical thermal comparison or FEA validation
is supplied by this figure.

## Transient result on HOLD

[PR #56](https://github.com/500ft/sensor-enclosure-thermal-design/pull/56) remains
on HOLD under the parent's six-item review of `cdd26ba`. The code, raw weather,
[original output](../analysis/output/thermal_transient_prediction.json) and
[figure](../analysis/figures/thermal_transient_prediction.png) are preserved.
Their original labels do not establish a reviewed prediction or a protocol
freeze. The documentation correction does not change those artifacts.

| Review item | Current evidence and disposition |
| --- | --- |
| Initial state and integration | `simulate` advances before storing its first state and uses fixed `dt_s` instead of actual timestamp intervals. The initial-state defect remains. Existing steady-convergence tests do not check transient accuracy or timestep convergence. |
| Forcing time | `load_weather` interpolates every field as a point sample. Open-Meteo defines shortwave radiation as the preceding-hour mean. Energy-preserving interval handling, timestamp/unit checks, absolute labels and partial-day treatment remain unresolved. |
| Provenance and sky model | The output records the weather hash and provider, but the inspected files do not retain the exact acquisition request, retrieval date or selected weather product/version. The implemented sky-emissivity hybrid and total-cloud assumption lack verified equation-level support. Do not infer missing provenance from current API defaults. |
| Statistical and power interpretation | The bands are sensitivity quantiles from assumed uniform inputs, not measurement-derived uncertainty or calibrated prediction intervals. Marginal overlap cannot decide a paired variant difference. `i1_sensitivity` computes a finite secant for an added watt of sensor-coupled heat, not a differential derivative or a verified response per watt at the supply. Prose is corrected; code/output labels still need correction. |
| Decisions and registration | Funding expectation and unanswered E1-E4 are reconciled in the linked records below. I1 remains the first mechanism experiment. Freeze the model, processing and coefficients before outcomes; separately acquired weather can drive that frozen model under a registered procedure. A future exact weather trajectory cannot yet be supplied. |
| Integration and review | Current main is incorporated with its accepted public-data result and mandatory-first I1. Transient regeneration and numerical/provenance checks remain pending the corrections. Parent review must resolve HOLD before merge. |

The [API variable definitions](https://open-meteo.com/en/docs/historical-weather-api)
distinguish instantaneous temperature/wind from preceding-hour solar means.
Hourly reanalysis cannot establish minute-scale measured forcing at the rig.
The [current blocker](COLOCATION_OWNER_SESSION.md#current-blocker) and
[E1-E4](OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions) hold owner status.
No ranking inference is made from the held transient artifacts.

## Reading the evidence

| Output | Evidence type | Current limitation |
| --- | --- | --- |
| Deployment metrics and plots | Analysis of external field logs | Raw exports and confirmed deployment history are unavailable in the repository |
| Thermal-bias sweep | First-order analytical simulation | Parameters require lab measurement and co-location comparison |
| Literature brackets | Published measurements summarized from cited sources | Not measurements of this enclosure |
| CAD/FEA plan | Proposed method | Solver pipeline and geometry are not yet complete |

See [`data-and-figures.md`](data-and-figures.md) for the complete production path
and [`figure-manifest.json`](figure-manifest.json) for the machine-readable map.
