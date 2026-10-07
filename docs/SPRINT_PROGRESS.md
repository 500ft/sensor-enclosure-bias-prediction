# Progress log

What changed and when, newest first, one line per change that matters. The
plan is in the [roadmap](../ROADMAP.md) and the current blocker in the
[owner session record](COLOCATION_OWNER_SESSION.md#current-blocker). The
earlier, longer version of this log is kept at
[commit 4d1134e](https://github.com/500ft/sensor-enclosure-thermal-design/blob/4d1134ecf598f0abd53161d3339fb0fd5576eadf/docs/SPRINT_PROGRESS.md).

## Week of 2026-10-05

- **10-04** Transient prediction model: one thermal mass per variant on the
  steady balance, two weeks of Brooklyn weather, 400 Monte Carlo draws from
  declared ranges; predicts the I1 °C-per-watt response before data. Physical
  testing paused until funding starts.

## Week of 2026-09-28

- **09-30** Pilot policy decided before any data: estimation-only (no
  pass/fail), I1 load test permitted with a resistive load, 14-day maximum
  campaign window, historical-log request deferred. The rig is still the next
  step.
- **09-30** Owner: there are no co-location logs yet; the rig will be set up
  at the PI's test site, and data collected before then isn't usable. The
  retrospective-review route is closed. The current step is setting up the
  rig, then freezing the protocol before the first run.
- **09-30** The pilot now has one protocol. The draft protocol, the pilot
  design (R1–R3) and the experiment contract (C1–C9) were merged into
  [COLOCATION_PROTOCOL.md](COLOCATION_PROTOCOL.md), keeping every requirement
  and section number. One conflict was settled in favour of the later rule:
  pairing is per comparison, so a missing optional arm never discards a valid
  V0/V0P pair.
- **09-30** One roadmap: the finish line is Direction B, the measured
  day-and-night bias of the built enclosures beside a reference, compared with
  the model. README rewritten
  ([#49](https://github.com/500ft/sensor-enclosure-thermal-design/pull/49)).
- **09-30** PI go-ahead recorded, with a test site and manufacturing help. The
  next step is finding the existing co-location logs the owner reports
  ([#48](https://github.com/500ft/sensor-enclosure-thermal-design/pull/48)).
- **09-29** CI moved to Python 3.12 so numpy 2.5 installs
  ([#42](https://github.com/500ft/sensor-enclosure-thermal-design/pull/42)).

## Week of 2026-09-21

- **09-26** Baseline enclosure V0 as parametric CAD, accepted against an
  independent closed-form check of volume, bounding box, solid count and STEP
  re-import ([#41](https://github.com/500ft/sensor-enclosure-thermal-design/pull/41)).
- **09-26** Input uncertainty propagated through the model
  ([#38](https://github.com/500ft/sensor-enclosure-thermal-design/pull/38)).
  Provenance audit and parameter register
  ([#40](https://github.com/500ft/sensor-enclosure-thermal-design/pull/40)).
- **09-26** Experiment contract (which claims need a controlled intervention),
  Study B repairs and implementation tickets
  ([#37](https://github.com/500ft/sensor-enclosure-thermal-design/pull/37)).
- **09-24** Critique corrections, each checked numerically first. Three earlier
  claims were withdrawn: Study A's "no universal law" verdict (it had compared
  a linearised formula with the nonlinear solver it came from), the day/night
  self-heating test (radiative cooling can cancel electronics heating at
  night), and the claim that a shared reference makes the uncertainty about three
  times too small (for a difference against the same reference, that term
  cancels). The withdrawn wording was then removed
  from the documents that repeated it
  ([#34](https://github.com/500ft/sensor-enclosure-thermal-design/pull/34),
  [#35](https://github.com/500ft/sensor-enclosure-thermal-design/pull/35),
  [#36](https://github.com/500ft/sensor-enclosure-thermal-design/pull/36)).
- **09-24** Pilot design: three variants, data schema, uncertainty budget and
  the owner's decision list
  ([#32](https://github.com/500ft/sensor-enclosure-thermal-design/pull/32),
  [#33](https://github.com/500ft/sensor-enclosure-thermal-design/pull/33)).
- **09-22** Literature: 27 fully read sources checked against the model's
  uncited constants; the Biot table corrected
  ([#25](https://github.com/500ft/sensor-enclosure-thermal-design/pull/25)).
- **09-22** Competitor review from full texts. Two author mis-citations fixed;
  no checked source predicts enclosure bias before fabrication, and none models
  wall conduction ([#22](https://github.com/500ft/sensor-enclosure-thermal-design/pull/22)).
  The 09-24 critique then found a direct competitor, Air-STORM, which narrowed
  the novelty claim further.
- **09-20 to 09-22** Research-direction decision record, and a design for a
  conjugate-heat-transfer study (Study B)
  ([#21](https://github.com/500ft/sensor-enclosure-thermal-design/pull/21),
  [#23](https://github.com/500ft/sensor-enclosure-thermal-design/pull/23)).
  Research question draft ([#20](https://github.com/500ft/sensor-enclosure-thermal-design/pull/20)).

## Week of 2026-09-14

- **09-16** Novelty check: borderline, and only publishable if narrowed. The
  model reduces exactly to five dimensionless groups. Printed polymer walls
  give a Biot number of 0.1–0.6 at 3 mm, so wall conduction matters for printed
  enclosures ([#19](https://github.com/500ft/sensor-enclosure-thermal-design/pull/19)).
- **09-15** Evidence-preservation fix, ledger reconciliation and a sensitivity
  screen ([#18](https://github.com/500ft/sensor-enclosure-thermal-design/pull/18);
  plan [#17](https://github.com/500ft/sensor-enclosure-thermal-design/pull/17)).

## Week of 2026-09-07

- **09-13** Synthetic rehearsal of the whole CSV-to-analysis chain with known
  answers, tightened twice
  ([#13](https://github.com/500ft/sensor-enclosure-thermal-design/pull/13),
  [#14](https://github.com/500ft/sensor-enclosure-thermal-design/pull/14),
  [#15](https://github.com/500ft/sensor-enclosure-thermal-design/pull/15)).
- **09-12** Intake metadata fixed; CI dependencies pinned so the model tables
  reproduce byte for byte
  ([#11](https://github.com/500ft/sensor-enclosure-thermal-design/pull/11),
  [#12](https://github.com/500ft/sensor-enclosure-thermal-design/pull/12)).
- **09-11** README and presentation rewrite
  ([#10](https://github.com/500ft/sensor-enclosure-thermal-design/pull/10)).
- **09-10** Day/night pilot proposed, with an intake checker that refuses
  malformed data ([#9](https://github.com/500ft/sensor-enclosure-thermal-design/pull/9)).
- **09-09** Painted closed-box control added: white paint alone takes the
  modelled rise from 19.4 °C to 4.5 °C
  ([#7](https://github.com/500ft/sensor-enclosure-thermal-design/pull/7)).
  Night-bias interpretation corrected
  ([#8](https://github.com/500ft/sensor-enclosure-thermal-design/pull/8)).
- **09-07** Reliability metrics made schedule-aware
  ([#5](https://github.com/500ft/sensor-enclosure-thermal-design/pull/5)).

## Week of 2026-08-31

- **09-04** Reported numbers tied to committed artifacts
  ([#1](https://github.com/500ft/sensor-enclosure-thermal-design/pull/1)).

## Before September

Repository started 2026-06-12 with the heat-balance model, the literature
matrix and the deployment reliability analysis.
