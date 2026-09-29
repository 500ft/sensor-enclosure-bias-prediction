# Day/night co-location pilot — proposed 2026-09-09

Status: reviewer-ready **draft**, not a prospectively frozen campaign protocol.
Permission, available facilities and the next evidence step are recorded in the
[current owner decision and blocker](COLOCATION_OWNER_SESSION.md#current-blocker).
Existing historical deployment claims remain unverified. Review
[required provenance](DEPLOYMENT_PROVENANCE_REQUEST.md) for those historical
claims; it is not a prerequisite for reviewing a separately documented campaign.

## Decisions and why

Use one full 24-hour window as the minimum pilot, not midday alone. The [model](../analysis/thermal_bias.py) can predict either negative or positive night bias depending on sky temperature and internal dissipation. Its example −4 °C or +8–23 °C scenarios are **not** measurement acceptance bands, universal predictions or calibrated field tolerances.

Use simultaneous dark closed baseline V0, same-geometry painted baseline V0P, and matched-finish shield where actual equipment permits. If only one enclosure exists, perform paired successive campaigns with weather matching and label the comparison confounded by time; do not claim randomized simultaneous control. V1's different geometry, heat load and convection are not an isolated sky-view treatment.

Prefer a calibrated reference air thermometer in an independently characterized aspirated shield, at the same measurement height and away from the test boxes' exhaust/shadow. Shielding is necessary because radiation can heat the thermometer independently of air temperature; [NIST's air-temperature explanation](https://www.nist.gov/how-do-you-measure-it/how-do-you-measure-air-temperature-accurately), inspected 2026-09-09, explains this distinction. Reference shielding and aspiration are also uncertainty contributors, not perfection by assumption.

## Freeze before data

Record device and firmware IDs, geometry/finish/sensor location, heat dissipation, paired reference/calibration, site exposure and sharing permission. Choose positions before viewing temperatures and record any randomized assignment. Commit the approved protocol, intended window and uncertainty method before acquisition; do not backdate a freeze from this draft's date.

Proposed pilot acquisition is 60-second sampling for exactly 24 hours (1,440 planned slots), with synchronized sample-time UTC timestamps. This is a new campaign choice, not inferred historical logger cadence. Choose a different cadence only by a prospective protocol/code amendment. Keep raw samples and omissions; do not interpolate or silently round timestamps into a passing intake.

Record sensor/reference temperature, incident solar irradiance and local wind speed. Log cloud/sky conditions, wetness, interventions and reference aspiration separately. Effective sky temperature needs its own measurement/model uncertainty; zero sunlight alone does not establish clear-sky radiative cooling.

## Proposed quality thresholds, not thermal-model validation thresholds

- At least 90% paired finite samples over the **intended** 24-hour schedule.
- At least 120 paired minute samples with solar ≥200 W/m² and 120 with solar ≤5 W/m². These are two-hour exposure-coverage requirements, not independent sample counts or proof that a stationary regime was reached.
- Declared combined expanded paired-temperature uncertainty U95 ≤0.5 °C, supported by calibration, reference radiation/aspiration, drift, location mismatch and covariance. This is a proposed instrumentation target to resolve multi-degree effects; it is not claimed as available hardware accuracy.
- Pre/post zero or side-by-side calibration checks and setup photographs with permission. If drift exceeds the registered uncertainty treatment, classify the affected comparison inconclusive; retain all data.

If weather never supplies both regimes, retain the partial pilot and extend prospectively; do not change thresholds after seeing performance. One 24-hour campaign can reveal a discrepancy but cannot establish seasonal/general accuracy.

## Hypotheses and analysis

Define bias as sensor minus reference. Report dark/painted/shield bias, MAE, RMSE, paired availability and time traces by measured solar/wind regime. Treat night cooling as conditional on radiation and heat load. Fit no new parameters on these observations while calling them validation; if used for fitting, relabel them development and register a separate later campaign.

Model agreement requires an as-built prediction with propagated model/input uncertainty and an application tolerance registered before comparison. Neither is currently available. The pilot intake therefore deliberately produces **no VALIDATED classification**. Use the existing reliability CLI for residual metrics after admissibility and human provenance review; paired samples are temporally correlated, so do not report iid confidence intervals over 1,440 rows.

## Intake contract and reproduction

Rehearsal of the whole chain on synthetic data with known answers: `PYTHONPATH=. python -m analysis.colocation_rehearsal --out-dir build/rehearsal` (EN-R03S). It runs the intake CLI and then `compute_metrics` on the same bytes and writes `rehearsal.json`; synthetic input is always `SYNTHETIC_ONLY`.

New CLI: `python -m analysis.colocation_intake CSV_PATH --metadata METADATA_JSON`; capitalized paths are placeholders for real artifacts, not files claimed to exist.

Run from the repository root. The requested compatibility name is also usable as
`python -m analysis.intake_gate CSV_PATH --metadata METADATA_JSON`.
`analysis/intake_gate.py` delegates to the existing canonical
`analysis/colocation_intake.py`; it is not a separate admission policy.
Both module entrypoints have tested identical output and exit codes. See
[evidence reconciliation](specs/evidence-gap-correction/test-report.md) and the
[owner session packet](COLOCATION_OWNER_SESSION.md) before treating software
readiness as permission to acquire data.

CSV header exactly: `timestamp,sensor_temperature,reference_temperature,solar_w_m2,wind_m_s`.

Metadata requires `window_start,window_end,sensor_id,reference_id,site_id,firmware,clock_basis,calibration_reference,uncertainty_reference,permission_reference,protocol_reference,evidence_kind,paired_u95_c,csv_sha256`. Identity/reference fields are nonempty strings linking reviewable records; `evidence_kind` is physical or synthetic. The CSV SHA-256 binds raw bytes. No sample “approved” physical manifest is provided.

Exit 2 means malformed or incomplete evidence; 3 means structurally sufficient **synthetic-only** data; 0 means a physical-labeled pilot is eligible for **human review**, never model agreement or authenticated provenance. Metadata strings and a checksum cannot prove permission, calibration, truth or pre-acquisition timing. A reviewer must inspect the referenced records and protocol commit.

Runnable synthetic checks: `PYTHONPATH=. python -m unittest discover -s analysis/tests -p test_colocation_intake.py -v`. They exercise duplicate slots, missing edges/channels, malformed weather/time, bad uncertainty and synthetic non-promotion. For the current physical-data disposition, see the [owner session record](COLOCATION_OWNER_SESSION.md#current-blocker).
