# Roadmap

This is the plan for finishing the project. The current blocker, with its
owner statements, is kept in
[docs/COLOCATION_OWNER_SESSION.md](docs/COLOCATION_OWNER_SESSION.md#current-blocker).
The full decision table is [docs/OWNER_DECISIONS_2026-09-24.md](docs/OWNER_DECISIONS_2026-09-24.md);
work history is in [docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

The owner adopted a public-data-first investigation on 2026-10-04. First assess
external-data suitability, then make a narrowly scoped external model comparison
only if paired temperature channels, exposure metadata and data terms permit it.
Public data does not establish a transferable enclosure ranking or replace the
physical campaign.

The project is finished when measured temperature bias for the enclosure
variants, taken beside a reference thermometer over at least one full day and
night, has been compared with the model's predictions and written up. This is
Direction B in the [direction record](docs/research-direction-2026-09-21.md),
chosen on 2026-09-25 as the floor.

The study is registered as estimation-only: it reports bias and uncertainty,
with no pass/fail verdict, because no maximum tolerable error has been stated
for the sensor's intended use
([decided 2026-09-30](docs/OWNER_DECISIONS_2026-09-24.md#a00-decisions-recorded-2026-09-30)).

Direction A (predicting new geometries before they are built) stays
conditional on the pilot showing a reproducible bias above the instrument
uncertainty.

## Where it stands

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
  [data guide](docs/data-and-figures.md#deployment-log-plots). The owner still
  needs to book the PI date and inventory the rig, including calibration, power
  measurement, siting and simultaneous or sequential operation.

- Decided 2026-09-30, before any data: estimation-only reporting, the I1
  load test permitted with a resistive load, a 14-day maximum campaign window,
  and the historical-log request deferred. What's still open needs the rig:
  hardware, calibration records, site and data terms, fan decoupling and unit
  count ([decision table](docs/OWNER_DECISIONS_2026-09-24.md#a00-decisions-recorded-2026-09-30)).

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| A | Resolve external-data access after the completed AQ-SPEC probe | Owner reviews the draft request; data custodian supplies records and terms | A permitted paired sample and sufficient thermal/reference metadata, or a recorded inability to obtain them. **Current external-data step.** |
| B | Compare an eligible external dataset with the model, if feasible | Agent, after data suitability is established | Selection, independent-unit/day split and estimation metrics fixed before held-out evaluation; scoped result with uncertainty and exposure limits |
| 1 | Set up the co-location rig at the test site: the enclosure variants, the reference thermometer in its shield, and the loggers | Owner, with the PI's manufacturing help | Rig installed; inventory recorded in the blocker record (enclosure IDs, sensors, reference and its calibration certificate). **Physical campaign step.** |
| 2 | Freeze the protocol: fill the R1.3 register for the actual hardware, choose positions, state the window and uncertainty method, commit it with the approver and date | Agent drafts; owner and PI approve | Frozen protocol committed before any data |
| 3 | Run at least 24 h with all arms and the reference side by side, with the I1 resistive-load test as the first mechanism experiment and I2 shading retained as optional mechanism work; stop at 14 days if coverage is still short | Owner runs it; agent checks intake | Raw files and campaign manifest committed; intake passes |
| 4 | Compute bias and uncertainty per variant, day and night, and compare with the model | Agent | Results and comparison merged |
| 5 | Update the manuscript, README and portfolio | Agent | Merged |

The small Sensor.Community/DWD metadata pilot is a possible fallback, not an
executed result. It requires actual data licences, construction metadata and
checks of distance, elevation, land use and overlapping reference meteorology
before modeling. Historical lab data requires PI data terms and matching hardware
and exposure records. External exploration does not freeze the physical protocol.

## Not in this version

- Direction A: held-out geometries and pre-build prediction.
- CFD or conjugate heat-transfer runs, unless the pilot disagrees with the
  lumped model by more than its uncertainty.
- Verifying the historical deployment percentages, which needs raw exports
  held outside this repository.
