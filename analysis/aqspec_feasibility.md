# AQ-SPEC temperature-data feasibility

The executed probe obtained no paired sensor/reference temperature time series.
The selected reports downloaded and parsed, but do not supply the observations
needed to calculate enclosure temperature bias. This is an access and suitability
result, not a negative result for an enclosure design.

## Scope and reproducibility

The [source inventory](results/aqspec_source_inventory.json) records the requested
and resolved URLs, retrieval times, response status, byte counts and SHA256 for
successful downloads. Attribution: South Coast Air Quality Management District,
AQ-SPEC. Downloads and extracted PDF text remain outside git.

The probe covered the evaluations entry page, summary table, field page, sensor
index, AirSensor and AQY network pages, the library dashboard announcement,
website terms, and the selected documents below. PA-II was
chosen because the AirSensor guide explicitly documents a temperature channel;
the recent field report supplies identifiable units and exposure dates. Selection
was exploratory and did not use temperature-error outcomes.

Reproduce into a fresh directory outside the repository, with `curl` and Poppler's
`pdftotext` installed:

```sh
python3 analysis/aqspec_availability_probe.py /absolute/external/aqspec-probe
```

The script downloads the listed sources and parses static links and PDF text. A
failed individual download is recorded in the inventory; the script completing
does not mean data suitability passed. No direct tabular-file anchors were found
on the inspected HTML pages. This is a bounded search, not proof that AQ-SPEC has
no releasable data. JavaScript exports and undocumented APIs are not resolved by
the link scan. Manual inspection of the summary page's export code shows an Excel
export of the displayed pollutant-performance summary, not timestamped records.

## Sample and channel inventory

| Source | Material actually available | Missing for temperature bias |
| --- | --- | --- |
| [PA-II field report](https://www.aqmd.gov/docs/default-source/aq-spec/field-evaluations/purpleair-pa-ii---field-evaluation_2026.pdf?sfvrsn=ea8b667e_3), revision F20260602.0 | Downloadable, text-parseable PDF; units 0969, 1215, 2529 at Mecca; exposure 2025-12-06 through 2026-02-02; manufacturer dimensions and supply voltage, p. 6 | Sensor-temperature and independent thermometer records; thermal calibration and exposure metadata |
| Same report, pp. 6, 12 | PM reference is Teledyne API T640; stated sensor cadence 120 s and reference cadence 1 min; PM plots label local standard time | Row timestamps, timezone/clock corrections and thermal-channel cadence; the pollutant reference designation does not establish a calibrated air thermometer |
| Same report, p. 4 | States AQMD performed no sensor calibration for this evaluation | Temperature-element identity, sampling mode, firmware, heat loads, thermometer certificate and uncertainty |
| [DataViewer guide](https://www.aqmd.gov/docs/default-source/aq-spec/research-projects/airsensor-dataviewer-user-guide.pdf?sfvrsn=e2cd861_8), pp. 5-7 | Historical interface shows UTC timestamps, PM channels A/B, sensor temperature in F and RH; unit/location fields; describes CSV export and weather summaries | No paired reference-temperature column shown, no verified reference/radiation/wind overlap or calibration; screenshots are not acquired rows |
| [AirSensor page](https://www.aqmd.gov/aq-spec/special-projects/airsensor) | Says the DataViewer is temporarily offline; links its software and guide | Working documented export route. The guide's legacy viewer URL failed DNS resolution in this environment; that alone does not prove worldwide unavailability |
| [Field protocol](https://www.aqmd.gov/docs/default-source/aq-spec/protocols/sensors-field-testing-protocol.pdf?sfvrsn=5824c061_0), sections 2.1-2.4 | Distinguishes outdoor mounting from a louvered aluminum shelter; discusses meteorology and pollutant reference equipment | Selected units' mounting heights, radiation exposure, local wind and thermometer shielding/aspiration; generic protocol does not establish their actual installation |

Report and guide tables/plots were visually checked as well as text-extracted.
No plot was digitized into measurement data. Downloading a readable PDF proves
report access, not time-series access.

Other AQ-SPEC network routes remain distinct from this selected field evaluation.
The [AQY network page](https://www.aqmd.gov/aq-spec/special-projects/aeroqual-aqy-deployments)
links AQPortal dashboards for processed pollutant data, and the
[library announcement](https://www.aqmd.gov/home/research/pubs-docs-reports/newsletters/may-jun-jul-2026/empowering-communities--air-quality-sensor-library-and-new-dashboard)
links a newer JustAir dashboard with downloads. Their interactive exports were
not evaluated for paired thermal channels in this bounded probe. The older
DataViewer's offline notice must not be generalized to those services.

## Licence and interpretation

No explicit data licence or permission to redistribute the requested paired
series was established. The [website terms](https://www.aqmd.gov/privacy/terms-of-use),
under Trademarks and Copyrights, say documents may be protected and reproduction
may require permission. The field report limits its stated purpose to information
and education. Neither an accessible URL nor the linked R software's open-source
status establishes data reuse rights. Keep downloaded originals local and request
terms for analysis, derived publication and raw redistribution separately.

A usable sample would change this conclusion if it supplied simultaneous sensor
and calibrated air-reference temperatures with units, timestamps, quality flags,
thermal placement and reuse terms. Meteorology must overlap those rows if the
analysis is to examine solar or wind dependence. Co-location reduces horizontal
separation; height, radiation exposure and reference uncertainty still matter.
Community sensors paired with a distant weather station would introduce spatial
confounding. Day/night associations alone would not isolate solar heating.

No bias, uncertainty estimate, fit, design ranking or final-test evaluation was
computed. No split or protocol was frozen. Before a later external comparison,
record selection, whole-unit/contiguous-day development and holdout rules, and
bias/uncertainty metrics. Retain estimation-only reporting. Separate sensor-element
heating, PCB conduction and total enclosure dissipation; actual element, sampling
and power settings are needed before applying a datasheet or thermal model.

The Sensor.Community/DWD metadata fallback was not executed in this first task.
The physical campaign and historical deployment evidence remain separate. Lab
data would need PI use terms plus hardware and exposure metadata.

## Draft data request for owner review

Not sent. Suggested recipient: AQ-SPEC data custodian.

We are assessing whether your PA-II evaluation or another co-location dataset
supports an estimation-only study of sensor temperature bias. Could you provide
a small machine-readable day/night sample, its data dictionary and the following?

- Per-unit sensor temperature and simultaneous independent air-reference
  temperature, units, timestamps/timezone, cadence, clock adjustments, missing
  values, flags and processing history. Please distinguish sensor-internal
  temperature from station ambient temperature.
- Reference thermometer model/ID, calibration certificate and uncertainty,
  shielding/aspiration; matching radiation, wind and RH records with instrument
  locations and heights, if available.
- Unit IDs, temperature-element models, enclosure construction, sensor/PCB
  placement, sampling/firmware/power settings and mounting/exposure details,
  including whether each unit was inside the additional shelter.
- The applicable data licence or written conditions for research analysis,
  publication of derived results, raw redistribution and required attribution.
  If channels were not recorded, please identify those gaps and any suitable
  alternative dataset.

For any historical lab alternative, the owner should ask the PI who owns the
logs, what may be accessed/published, and where the matching hardware, reference
calibration and exposure records are. No access or permission is assumed.

## Owner exercise

Once a permitted paired sample exists, reproduce a daily block mean of
`T_sensor - T_reference` for each unit after documented time alignment and quality
filtering. State coverage and reference calibration uncertainty. A shared reference
calibration error does not average away with logger samples; account for correlated
terms and use days/units, rather than rows, for independent replication. Explain
how absorbed radiation, convection, radiation loss and electronics heat enter the
thermal balance. The present downloads cannot supply that calculation.
