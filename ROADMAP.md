# Roadmap

This is the plan for finishing the project. The current blocker, with its
owner statements, is kept in
[docs/COLOCATION_OWNER_SESSION.md](docs/COLOCATION_OWNER_SESSION.md#current-blocker).
The full decision table is [docs/OWNER_DECISIONS_2026-09-24.md](docs/OWNER_DECISIONS_2026-09-24.md);
work history is in [docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

The owner-authorized v2 direction asks how much target-design calibration
measured geometry, material and power data plus shared thermal laws can replace.
A transfer result will need a withheld enclosure, independent units or swaps,
a future-period split, explicit calibration budgets and simpler physical and
empirical baselines. Report error and interval coverage by exposure regime.
Geometry transfer is an eventual result, not evidence supplied by the current
single-node calculation.

The first-stage floor remains Direction B: measure temperature bias and
uncertainty beside a calibrated reference over day and night, compare with the
model and write up the result. Reporting remains estimation-only with no
pass/fail verdict. A claim that co-location can be skipped would require a
prospective application tolerance with Guibaud. The [decision record](docs/OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions)
separates owner adoption of the direction from unresolved physical and PI gates.

This task corrects PR #56; it does not launch the transfer study or a campaign.
An I1 thermal step at known airflow identifies effective heat/conductance and
capacity/conductance in the single-node limit. It cannot identify every physical
parameter. Broader prediction identifiability needs plausible parameter/noise
ranges and the actual I1/I2/ventilation interventions, not local Fisher
information at one point. A simpler predictor remains an acceptable outcome.

## Where it stands

- The [corrected transient result in PR #56](docs/results.md#transient-result-on-hold)
  has executed initial-state, exact-RC, interval-energy and refinement checks.
  Current output uses explicit sky scenarios and sensitivity labels. Parent
  review remains on HOLD; missing acquisition provenance stays unknown.

- The executed [AQ-SPEC suitability probe](analysis/aqspec_feasibility.md) obtained
  reports but no paired temperature series. Its source inventory and draft data
  request are recorded with the result. External model comparison remains blocked
  on usable channels, metadata and reuse terms.

- The published [thermal predictions](analysis/output/thermal_bias_table.csv)
  are point estimates. Input uncertainty has not been propagated to these
  outputs; [analysis/uncertainty.py](analysis/uncertainty.py) is a separate,
  tested module. The [parameter register](docs/PARAMETER_REGISTER.csv) records
  the source review and unresolved inputs.
- The shield-versus-painted-box ranking reverses under the documented combined
  sensitivity settings for shading, convection and plate-air preheat. The
  [sensitivity results](analysis/thermal_bias_results.md) establish no design
  preference.
- The baseline enclosure is parametric CAD, accepted against an independent
  closed-form check.
- The pilot protocol, intake checker and campaign validation exist as drafts.
- The PI has given the go-ahead, with a test site and manufacturing help
  (owner statement, 2026-09-29).
- The thermal co-location campaign has not run. Earlier deployment and
  electronics work remains recorded in the
  [data guide](docs/data-and-figures.md#deployment-log-plots). Funding expectations,
  rig readiness and the next owner action are recorded in the
  [current blocker](docs/COLOCATION_OWNER_SESSION.md#current-blocker).

- Decided 2026-09-30, before any data: estimation-only reporting, the I1
  load test permitted with a resistive load, a 14-day maximum campaign window,
  and the historical-log request deferred. What's still open needs the rig:
  hardware, calibration records, site and data terms, fan decoupling and unit
  count ([decision table](docs/OWNER_DECISIONS_2026-09-24.md#a00-decisions-recorded-2026-09-30)).

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 0 | Review the corrected PR #56 result | Parent reviewer | Numerical evidence and source limitations accepted; HOLD disposition recorded. **Current software step.** |
| A | Resolve external-data access after the completed AQ-SPEC probe | Owner reviews the draft request; data custodian supplies records and terms | A permitted paired sample and sufficient thermal/reference metadata, or a recorded inability to obtain them. Optional external-data route; no outreach authorized. |
| B | Compare an eligible external dataset with the model, if feasible | Agent, after data suitability is established | Selection, independent-unit/day split and estimation metrics fixed before held-out evaluation; scoped result with uncertainty and exposure limits |
| 1 | Set up the co-location rig at the test site: the enclosure variants, the reference thermometer in its shield, and the loggers | Owner, with the PI's manufacturing help | Rig installed; inventory recorded in the blocker record (enclosure IDs, sensors, reference and its calibration certificate). **Physical campaign step.** |
| 2 | After model corrections and hardware readiness, freeze the protocol, model, processing, coefficients, parameter treatment and weather acquisition procedure with the approver and date | Agent drafts; owner and PI approve | Frozen protocol committed before any data |
| 3 | Run at least 24 h with all arms and the reference side by side, with the I1 resistive-load test as the first mechanism experiment and I2 shading retained as optional mechanism work; stop at 14 days if coverage is still short | Owner runs it; agent checks intake | Raw files and campaign manifest committed; intake passes |
| 4 | Compute bias and uncertainty per variant, day and night; drive the frozen model with independently collected weather under the registered procedure and compare with observations | Agent | Results and comparison merged |
| 5 | Write up the first-stage estimation result in the manuscript and README | Agent | Reviewed result merged |
| 6 | Register a geometry/calibration-transfer comparison after identifying usable parameters and resolving designs/replicates | Owner and PI approve; agent implements only after activation | Frozen holdouts, calibration budgets, baselines and regime-specific metrics before evaluation |

The small Sensor.Community/DWD metadata pilot is a possible fallback, not an
executed result. It requires actual data licences, construction metadata and
checks of distance, elevation, land use and overlapping reference meteorology
before modeling. Historical lab data requires PI data terms and matching hardware
and exposure records. External exploration does not freeze the physical protocol.

## Not in this version

- Executing the eventual geometry-transfer study in this correction task.
- CFD or conjugate heat-transfer runs, unless the pilot disagrees with the
  lumped model by more than its uncertainty.
- Verifying the historical deployment percentages, which needs raw exports
  held outside this repository.
