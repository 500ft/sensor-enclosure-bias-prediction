# Roadmap

This is the plan for finishing the project. The current blocker, with its
owner statements, is kept in
[docs/COLOCATION_OWNER_SESSION.md](docs/COLOCATION_OWNER_SESSION.md#current-blocker).
The full decision table is [docs/OWNER_DECISIONS_2026-09-24.md](docs/OWNER_DECISIONS_2026-09-24.md);
work history is in [docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

The project is finished when measured temperature bias for the enclosure
variants, taken beside a reference thermometer over at least one full day and
night, has been compared with the model's predictions and written up. This is
Direction B in the [direction record](docs/research-direction-2026-09-21.md),
chosen on 2026-09-25 as the floor.

If no maximum tolerable error is stated for the sensor's intended use, the
study reports bias and uncertainty only, with no pass/fail verdict. That is
allowed by the decision table and does not block anything.

Direction A (predicting new geometries before they are built) stays
conditional on the pilot showing a reproducible bias above the instrument
uncertainty.

## Where it stands (2026-09-30)

- A lumped heat-balance model predicts, at 1000 W/m² sun and 0.5 m/s wind, a
  rise of 19.4 °C for the dark box, 4.5 °C for the same box painted white and
  3.0 °C for the passive shield. At night the modelled bias can change sign.
- The model's constants have been checked against 27 fully read sources, and
  the uncertainty is propagated to the prediction.
- The baseline enclosure is parametric CAD, accepted against an independent
  closed-form check.
- The pilot protocol, intake checker and campaign validation exist as drafts.
- The PI has given the go-ahead, with a test site and manufacturing help
  (owner statement, 2026-09-29).
- The owner reports an existing co-location setup with logged data. Where
  those logs are is not known yet.

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Find the existing co-location logs: the logger or storage system, or the person in the lab who has them | Owner | Location recorded in the blocker record. **Current step.** |
| 2 | List what physically exists: which enclosure variants are built, which sensor sits in each, and which reference thermometer is used, with any calibration certificates | Owner | Inventory recorded (decision rows 3 and 4) |
| 3 | Review the existing logs against the protocol: day and night coverage, reference pairing, gaps | Agent | Review merged; states whether a new run is needed |
| 4 | If needed, freeze the protocol and run 24 h or more with all variants and the reference side by side | Owner runs it; agent prepares and freezes the protocol | Raw files committed with the campaign manifest |
| 5 | Compute bias and uncertainty per variant, day and night, and compare with the model | Agent | Results and comparison merged |
| 6 | Update the manuscript, README and portfolio | Agent | Merged |

Analysis of logs collected before the protocol was frozen is labelled
retrospective. It still counts toward the finish line.

## Not in this version

- Direction A: held-out geometries and pre-build prediction.
- CFD or conjugate heat-transfer runs, unless the pilot disagrees with the
  lumped model by more than its uncertainty.
- Verifying the historical deployment percentages, which needs raw exports
  held outside this repository.
