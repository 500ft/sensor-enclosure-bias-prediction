# Day/night co-location pilot — draft protocol

**Status: draft.** It becomes the pilot protocol only when it is frozen and
committed, with the approver and date, before any data is collected. Don't
backdate a freeze to this draft. The PI has approved the pilot in principle;
the current blocker is in the
[owner session record](COLOCATION_OWNER_SESSION.md#current-blocker).

The detailed design (variants, data schema, uncertainty budget) is in
[pilot-design](specs/pilot-readiness/pilot-design-2026-09-24.md), and the
rules on which claims need a controlled intervention are in the
[experiment contract](specs/pilot-readiness/experiment-contract-2026-09-24.md).
Historical deployment claims are a separate question
([provenance request](DEPLOYMENT_PROVENANCE_REQUEST.md)) and don't block this
pilot.

## Design

**One full 24 hours, not a midday check.** Depending on sky temperature and
internal heating, the [model](../analysis/thermal_bias.py) can predict either a
negative or a positive bias at night. Its example scenarios (−4 °C at night,
+8 to +23 °C by day) are illustrations, not acceptance bands.

**Enclosures side by side.** Run the dark closed box (V0), the same box
painted (V0P) and a shield with matching finish at the same time, as far as
the hardware allows. If only one enclosure exists, run paired campaigns one
after another in matched weather, and label the comparison as confounded by
time. V1 differs in geometry, heat load and airflow, so comparing it with V0
does not isolate the effect of sky view.

**Reference thermometer.** A calibrated air thermometer in its own
characterised, aspirated shield, at the same height as the test enclosures and
clear of their exhaust and shadow. The shield matters because sunlight heats a
bare thermometer ([NIST explanation](https://www.nist.gov/how-do-you-measure-it/how-do-you-measure-air-temperature-accurately)).
The reference's own shielding and aspiration add to the uncertainty budget.

## Record before collecting data

- Device and firmware IDs, geometry, finish, sensor position and internal
  heat dissipation for each enclosure.
- The paired reference and its calibration.
- Site exposure, and permission to share data and photos.
- Positions, chosen before looking at any temperatures, and any randomised
  assignment.
- The frozen protocol, the intended window and the uncertainty method,
  committed before acquisition.

## Acquisition

- Sample every 60 seconds for exactly 24 hours: 1,440 planned slots, with
  synchronised UTC timestamps. Changing the cadence needs a protocol and code
  amendment made before the run.
- Record sensor temperature, reference temperature, incident solar irradiance
  and local wind speed. Log cloud and sky conditions, wetness, interventions
  and reference aspiration separately.
- Keep every raw sample and every gap. Don't interpolate or round timestamps.
- Zero sunlight alone does not mean a clear sky. Effective sky temperature needs
  its own measurement or model, with its uncertainty.

## Data-quality thresholds

These decide whether the data is usable. They are not thresholds for
validating the thermal model.

- At least 90% paired, finite samples over the intended 24 hours.
- At least 120 paired minutes with solar ≥ 200 W/m², and at least 120 with
  solar ≤ 5 W/m². These guarantee two hours of each condition; they are not
  independent samples.
- A declared expanded paired-temperature uncertainty U95 ≤ 0.5 °C, covering
  calibration, reference radiation and aspiration, drift, position mismatch
  and covariance. This is a target for resolving effects of a few degrees, not
  a claim about the hardware on hand.
- Calibration or side-by-side checks before and after, and setup photos if
  permitted. If drift exceeds the stated uncertainty treatment, mark the
  affected comparison inconclusive and keep all the data.

If the weather never provides both conditions, keep the partial run and extend
it with a new, pre-declared window. Don't change the thresholds after seeing
the results. One 24-hour run can reveal a discrepancy; it cannot show seasonal
or general accuracy.

## Analysis

- Bias is sensor minus reference. Report bias, MAE, RMSE, paired availability
  and time traces for the dark, painted and shield enclosures, split by
  measured sun and wind conditions.
- Treat night cooling as depending on radiation and heat load.
- Don't fit new model parameters to this data and call it validation. If the
  data is used for fitting, label it development and plan a separate later
  campaign.
- Paired samples are correlated in time, so don't report confidence intervals
  that treat the 1,440 rows as independent.

Checking the model against the data needs an as-built prediction with its
propagated uncertainty and an application tolerance, both registered before
comparison. Neither exists yet, so the intake never classifies a pilot as
VALIDATED.

## Intake and reproduction

Rehearse the whole chain on synthetic data with known answers:

```bash
PYTHONPATH=. python -m analysis.colocation_rehearsal --out-dir build/rehearsal
```

It runs the intake and then `compute_metrics` on the same bytes and writes
`rehearsal.json`. Synthetic input always comes out `SYNTHETIC_ONLY`.

Check a real campaign file (capitalised names are placeholders):

```bash
python -m analysis.colocation_intake CSV_PATH --metadata METADATA_JSON
```

`python -m analysis.intake_gate` is an alias for the same checker, with
identical output and exit codes.

The CSV header must be exactly:

```text
timestamp,sensor_temperature,reference_temperature,solar_w_m2,wind_m_s
```

The metadata must include `window_start`, `window_end`, `sensor_id`,
`reference_id`, `site_id`, `firmware`, `clock_basis`, `calibration_reference`,
`uncertainty_reference`, `permission_reference`, `protocol_reference`,
`evidence_kind` (`physical` or `synthetic`), `paired_u95_c` and `csv_sha256`.
The reference fields are non-empty strings pointing to records a reviewer can
check; the checksum ties the metadata to the exact CSV bytes.

Exit codes:

| Code | Meaning |
| --- | --- |
| 2 | Malformed or incomplete evidence |
| 3 | Structurally sufficient, but synthetic only |
| 0 | A physical pilot eligible for human review. It does not mean the model agrees, or that provenance is authenticated |

Metadata strings and a checksum can't prove permission, calibration or when
the data was collected; a reviewer has to read the referenced records and the
protocol commit.

The synthetic tests cover duplicate slots, missing edges and channels,
malformed weather and time fields, bad uncertainty values and keeping synthetic
data from being promoted:

```bash
PYTHONPATH=. python -m unittest discover -s analysis/tests -p test_colocation_intake.py -v
```
