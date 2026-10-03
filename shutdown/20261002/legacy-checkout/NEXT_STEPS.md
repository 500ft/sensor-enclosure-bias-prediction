# Next Steps

Ordered by dependency. Each phase unblocks the next; items within a phase can run in parallel.

## Phase 0 — Desk work (this week, no hardware)

- [ ] **Set numeric pass/fail targets with the PI** and fill the four TODOs in
  `templates/calibration_metrics.md`: calibrated temperature RMSE (°C), calibrated RH RMSE (%RH),
  minimum autonomy (days), maintenance interval (days). Every downstream result is scored against
  these, so they must be fixed *before* data exists.
- [ ] **Verify the two self-flagged citations against the PDFs**: Botero cone dimensions and author
  list; Theisen RMSE figures (1.22 °C → ~1.08 °C with wind). The manuscript already marks these
  for confirmation.

## Phase 1 — Screening physics (1–2 days; the missing MechE content)

- [ ] **Write a one-page lumped thermal model of radiation error** (absorbed solar flux vs.
  convective coupling, ΔT ≈ αG·A_p / (h·A_s)). Check it reproduces Theisen's ~1 °C low-wind bias.
  This justifies white coating + ventilation as the two levers and makes the paper predictive.
- [ ] **Stack-effect hand calc for the helical/chimney candidate.** Screening estimate:
  Δp = ρgH(ΔT/T) ≈ 0.024 Pa for H = 0.2 m, ΔT = 3 K → ~0.2 m/s ideal, less after helix friction,
  and the draft only appears once the error already exists. Expect to cut this candidate; decide
  on the calc, not after a month of field time.
- [ ] **Fan energy budget.** Continuous 680 mW ≈ 16.3 Wh/day ≈ 490 Wh/month (battery-dominating);
  duty-cycled 30 s per 5-min sample ≈ 1.6 Wh/day (trivial). Pick the duty-cycle scheme — this
  becomes the paper's centerpiece experiment (aspirated accuracy at ~5–10% of fan energy).
- [ ] **Measure the logger's current-draw profile** (sleep vs. active) → predicted autonomy vs.
  battery capacity, to compare against observed autonomy later.
- [ ] **Add these as a new "a priori screening analysis" subsection in §4** and update the §2.3
  candidate list and `geometries_options.csv` to reflect what survives screening.

## Phase 2 — Lock the experiment design (half a day + PI sign-off)

- [ ] **Cut the test matrix to three variants**: (1) current box unchanged (baseline),
  (2) two-zone COTS IP-rated box + white PETG shield module, (3) duty-cycled fan-aspirated shield.
- [ ] **Write the comparison protocol into §4**: all variants deployed *simultaneously*
  side-by-side next to the reference; one week of all-sensors-in-one-shield inter-calibration
  first; optional mid-test sensor swap between shields; hourly aggregation; errors binned by
  irradiance × wind class; bootstrap confidence intervals resampled by day; time-split
  calibration validation (already specified).
- [ ] **Decide the durability scope**: either a cheap accelerated bench test (UV lamp +
  water-spray cycles on coated PLA/PETG coupons) or explicitly literature-only durability claims.
  Don't leave it ambiguous — 30 days outdoors cannot show UV degradation.
- [ ] **Fix the drift metric in `analysis/compute_metrics.py`**: regress on daily-mean residuals
  instead of raw samples so the diurnal cycle doesn't alias into "drift."

## Phase 3 — Hardware documentation and build (lab time)

- [ ] **Fill the Section 3 baseline inventory** (the README "next data needed" list): exact sensor
  part numbers + datasheets, MCU/logger, power system, enclosure material and geometry, sensor
  placement, logging interval, storage/transmission, firmware behavior, known failures.
- [ ] **Bench check the current box**: confirm sensor operation, timestamps, battery-voltage
  logging; add internal enclosure temperature and RH sensors (needed for the MLR covariates and
  the §6 diagnosis logic).
- [ ] **Build variant 2**: COTS IP-rated junction box + printed white PETG vent/shield module,
  cable glands, vent plug or desiccant in the sealed zone, internal RH logged.
- [ ] **Build variant 3**: duty-cycled fan shield — firmware spins the fan before each sample (or
  on high-irradiance/low-wind trigger). This is the sense→decide→actuate mechatronics content.
- [ ] **Print and coat weathering coupons** if Phase 2 chose the accelerated bench test.

## Phase 4 — Deploy (calendar time; start as early as possible)

- [ ] **One-week inter-calibration deployment**: all sensors together in one shield, outdoors.
- [ ] **30-day co-location**: all three variants side-by-side next to the reference instrument.
  Keep the deployment log (`templates/deployment_log.csv`), photograph everything, log every
  maintenance event and failure — failures are data in this framing.

## Phase 5 — Analysis and writing

- [ ] Run `analysis/compute_metrics.py` per channel → populate §5.1 (raw accuracy) and
  §5.3 (autonomy/completeness) tables.
- [ ] Fit linear and multiple-linear calibrations with the time split → populate §5.2.
- [ ] Binned-error analysis (irradiance × wind) with bootstrap CIs; code failure modes → §5.4.
- [ ] Discussion: identify the dominant limiting factor; fill the §7 decision framework with
  measured numbers instead of placeholders.
- [ ] Manuscript V2 → PI review.

## Phase 6 — Stretch / portfolio

- [ ] HardwareX-style open-hardware writeup (Botero's venue) — the repo documentation is already
  most of the way to their format.
- [ ] Portfolio assets: CAD renders, exploded views, failure photos, before/after calibration plots.
- [ ] Advanced calibration comparison: simple recursive (Kalman-style) bias estimator vs. static
  MLR — the bridge to state estimation for robotics work.
