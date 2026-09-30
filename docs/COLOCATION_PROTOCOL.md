# Co-location pilot protocol (draft)

**Status: draft.** This is the single protocol for the pilot. It becomes the
frozen protocol only when it is committed with the approver's name and date,
before any data is collected; don't backdate a freeze to this draft. The PI has
approved the pilot in principle. The current blocker is in the
[owner session record](COLOCATION_OWNER_SESSION.md#current-blocker) and the
open decisions are in [OWNER_DECISIONS](OWNER_DECISIONS_2026-09-24.md).

On 2026-09-30 this file absorbed the two companion specifications, the pilot
design (sections R1–R3) and the experiment contract (sections C1–C9). Their
section numbers are kept so existing references still point somewhere. The
originals, including their correction history, are at
[pilot-design](https://github.com/500ft/sensor-enclosure-thermal-design/blob/e3ef0dead36a0b39c542eb565014cb4357c7fadf/docs/specs/pilot-readiness/pilot-design-2026-09-24.md)
and
[experiment-contract](https://github.com/500ft/sensor-enclosure-thermal-design/blob/e3ef0dead36a0b39c542eb565014cb4357c7fadf/docs/specs/pilot-readiness/experiment-contract-2026-09-24.md).
The design draws on the [research direction record](research-direction-2026-09-21.md)
§9 (which gap maps to which observable) and the
[2026-09-22 literature review](../literature/REVIEW_2026-09-22.md) (measured
magnitudes and method). Historical deployment claims are a separate question
([provenance request](DEPLOYMENT_PROVENANCE_REQUEST.md)) and don't block the
pilot.

**The rule behind every claim.** A mechanism claim is either backed by a
controlled intervention with a named estimand, or it is labelled an
association. There is no third category, and an uncontrolled day/night
comparison is never promoted to cause.

Contents: [what the pilot must show](#what-the-pilot-must-show) ·
[setup](#setup) · [experiments](#experiments) ·
[acquisition and data](#acquisition-and-data) ·
[data-quality thresholds](#data-quality-thresholds) ·
[uncertainty](#uncertainty) · [analysis](#analysis) ·
[intake and reproduction](#intake-and-reproduction)

---

## What the pilot must show

### R1.1 The question it has to answer

The literature review found two things that shape the design:

1. **No published source measures the electrical power dissipated inside a
   low-cost air-quality enclosure.** The two origin papers blame different
   things: `holder2020` suggests heat from the sensor electronics, and
   `malings2020` says the shell traps heat. Measuring those watts is the pilot's
   real contribution.
2. **The only evidence-based separation of causes points at the sun.**
   `shlipak2025` measured internal temperature returning to ambient at night,
   and `holder2020`'s only attribution test implicated solar load. A steady
   electronics-driven offset would not vanish at night.

**Night versus day does not identify self-heating.** At night, electronics
heating can be exactly cancelled by long-wave loss to the sky, so zero net bias
does not mean zero dissipation. A calculated example in this model (V1
geometry, `eps` 0.9, `A_conv` 0.020 m², `f_sky` 0.05, `T_air` 30 °C, `T_sky`
10 °C): `Q = eps·sigma·A_conv·f_sky·(303.15⁴ − 283.15⁴)` = 0.102972 W gives a
night bias of −1.2e-8 °C. That is a real heat source with essentially no bias.
"The shell traps heat" and "the electronics make heat" are compatible: one is
a resistance, the other a source.

So night and day observations only constrain the combined heat balance. The
dissipation term needs a controlled power intervention (experiment I1 below),
and that is the first mechanism experiment.

`shlipak2025` also found internal air, wall and battery temperatures within
0.25 °C of each other even at peak sun, in one ABS enclosure. That supports the
lumped model and makes one well-placed internal probe defensible, though it
does not prove it for this geometry (see C1). It also found internal fans
largely ineffective and possibly net-heating, so there is no internal-fan arm.

**Expected magnitudes, for sanity checks only, not acceptance criteria.**
Published enclosure biases: +1.88 °C mean and +6.48 °C daily maximum
(`shlipak2025`, PurpleAir PVC), +2.6 °C (`couzo2024`), +5.23 °C (`holder2020`).
A pilot result far outside that range is a reason to check the instruments
before it is a finding.

---

## Setup

### R1.2 Enclosures and reference

Run the whole test for at least 24 hours, so it covers day and night.
Depending on sky temperature and internal heating, the
[model](../analysis/thermal_bias.py) can predict either a negative or a positive
bias at night. Its example scenarios (−4 °C at night, +8 to +23 °C by day) are
illustrations, not acceptance bands.

| Arm | What it is | Differs from V0 by | Status |
| --- | --- | --- | --- |
| V0 | Dark, closed baseline enclosure | — | geometry not yet recorded |
| V0P | Same geometry and sensor placement as V0, with a documented finish change only | surface finish | geometry not yet recorded |
| V1 | Passive vented shield | geometry and venting | geometry not yet recorded |
| V0-U (optional) | V0 hardware with the electronics unpowered, logged externally | internal dissipation only | owner decision |
| REF | Independently characterised reference thermometer at matched height and exposure | — | instrument not yet identified |

V0P exists so that the shield is never judged against an unmatched control;
the repository's own matched-control screen showed the nominal shield
advantage reverses under combined assumptions. V1 differs in geometry, heat
load and airflow, so V0 against V1 does not isolate the effect of sky view.

**Simultaneous by default.** If only one enclosure can be instrumented at a
time, the owner must approve a paired-successive design in advance, run the
campaigns in matched weather, and label every resulting comparison as
confounded by weather and time.

**Reference thermometer.** A calibrated air thermometer in its own
characterised, aspirated shield, at the same height as the test enclosures and
clear of their exhaust and shadow. Sunlight heats a bare thermometer
([NIST explanation](https://www.nist.gov/how-do-you-measure-it/how-do-you-measure-air-temperature-accurately)),
and the reference's own shielding and aspiration add to the uncertainty budget.

**Zones.** Separate the electronics from the air-sensing zone where the
hardware allows. Where it doesn't, measure and record the heat path rather than
assuming it.

### C1 Temperatures to measure

The model has one sensor node; a real enclosure has at least six distinct
temperatures. Treating them as one is an assumption to test at commissioning.

| Node | Symbol | Measured how | If not measured |
| --- | --- | --- | --- |
| Ambient air | `T_air` | the reference, at matched height | the campaign is void; this is the measurand's reference |
| Sensor element | `T_s` | the enclosure's own sensor | — |
| Internal air | `T_int` | independent probe in the sensing zone, own logger | single-node adequacy untested; say so |
| Inner wall | `T_w,i` | surface probe at a declared spot | wall gradient unknown; Biot screening only |
| Outer wall | `T_w,o` | surface probe at the same station | same |
| Electronics | `T_e` | surface probe on the dissipating component | heat path unidentified |
| Mount | `T_m` | probe at the mast or bracket interface | conduction leak unquantified |

**Commissioning.** Before the campaign, log every available node for at least
one full day and night and report the spread. To judge whether one node is
enough: (i) state which prediction the single node is meant to stand for, and
over which exposure; (ii) register a node-equivalence tolerance for that
prediction, with its reasoning; (iii) compare the observed spread with it after
allowing for probe uncertainty. The 0.25 °C figure above is an instrument
target, not this tolerance. If no tolerance can be justified in advance, report
the spread as diagnostic evidence, not as a pass or fail decided afterwards.

**Areas.** Write the area mapping down before comparing any coefficient.
`A_conv` for V0 and for V1 belong to different coupled systems, not one
parameter measured twice. `A_conv` is an effective coupled area, not the total
CAD surface; `A_proj` is a projection at a stated sun geometry.

### R1.3 Record before collecting data

Every value needs its units, its evidence state and how it will be obtained:
`measurement`, `vendor_drawing` or `design_then_inspect`, as in the CAD
contract ([Study B design](specs/study-b-cht/design.md) §5). A drawing cannot
close a `measurement` field.

| Group | Fields | Obtained by |
| --- | --- | --- |
| Identity | hardware ID, sensor ID, firmware version, enclosure revision | measurement |
| Material and optics | material, finish, solar absorptance `alpha` and emissivity `eps`, measured or bounded with the standard named (E903, C1549 or E1918 per `levinson2010`) | measurement; no measured `alpha` for a printed wall exists in the literature, and a colour name is not evidence |
| Geometry | wall thickness, vent count and sizes, open area, sensor stand-off, electronics location, plate gaps | measurement |
| Power | electrical input power (W) and where it is measured, plus the fraction reaching the sensor zone | measurement; this is the new quantity |
| Reference | instrument ID, calibration certificate, stated uncertainty, shield and aspiration | vendor drawing and measurement |
| Siting | mounting height, orientation, exposure, shade, ground and background, site and data permission | owner |
| Schedule | intended UTC start and end, cadence | owner |
| Environment | cloud and sky, solar irradiance, wind, wetness, interventions, maintenance | measurement |

Also record, before any data: positions chosen before looking at
temperatures, any randomised assignment, and the frozen protocol, window and
uncertainty method, committed to the repository.

---

## Experiments

### C2 Intervention matrix

The estimand is the quantity each experiment identifies. "Association" means
the design cannot separate the named confounder.

| # | Mechanism | Intervention | Held fixed | Likely confounders | Measurements | Estimand |
| --- | --- | --- | --- | --- | --- | --- |
| I1 | Internal dissipation | at least 2 documented electronics load states, or a controlled resistive load at the heat source | airflow, enclosure, probe position, mounting, exposure | fan tied to power; heating in the added load's wiring; ambient drift between blocks | measured V and I (never rated W), all C1 nodes, ambient, solar, wind, sky | °C per W at the sensor |
| I2 | Solar loading | shade and unshade outdoors, or a lamp indoors, at fixed power | power, airflow, position | shading also changes the long-wave view; gusts | irradiance on the projected plane, sky condition, all nodes | °C per (W/m²), for a stated orientation |
| I3 | Ventilation | change one vent parameter (total open area at fixed inlet and outlet positions), inspected | material, finish, heat source, power | the vent change also alters radiation entry and view factor | inspected open area, airflow proxy or pressure drop, all nodes | °C per unit open-area ratio, conditional |
| I4 | Surface finish | V0 against V0P on matched hardware | geometry, sensor position, exposure, power | real paint changes `eps` as well as `alpha`; an alpha-only change exists only in the model | measured `alpha` and `eps` per finish, standard named | °C per Δ(`alpha`, `eps`) jointly |
| I5 | Whole design | V0P against V1 | exposure, reference, window | geometry, ventilation, sensor position and heat coupling all differ | as above | a bundled design effect (see C9) |
| I6 (optional, owner) | Aspiration benchmark | fresh air drawn across an isolated probe (the `deford2025` arrangement), not internal recirculation | enclosure, power accounting | the fan adds heat and power; failure modes | fan power, inlet and outlet layout, airflow or failure indicator, fan-off data | °C reduction against passive, at a stated power cost |

### I1 procedure (the first experiment)

I1 is the only design here that identifies the dissipation term, and the
literature has no measured value for a low-cost air-quality enclosure.

1. Temperature probes powered and logged independently, fixed in place, so the
   measurement chain doesn't change with the load state.
2. At least two documented load states. A controlled resistive load at the heat
   source is preferred for a purely thermal test, because it separates heat
   from firmware behaviour.
3. Log actual voltage and current with synchronised timestamps. Rated watts are
   not data.
4. Hold airflow fixed. Powering down a PM unit usually stops its fan too, which
   changes heat and ventilation together. If the fan can't be decoupled, the
   test estimates a combined heat-and-airflow effect and must be labelled that
   way.
5. Randomise or counterbalance the load order and repeat in blocks. Record
   every transition; never drop an inconvenient interval.
6. Settling rule from a step-response test: propose at least 5 estimated
   dominant time constants, check that against the observed response, and
   revise it prospectively if the response isn't first-order.
7. Start under controlled radiation, then repeat outdoors under registered
   conditions. Log sky and long-wave information: `G = 0` is not zero net
   radiation.
8. Keep three quantities apart: measured electrical input, total heat released
   by the enclosure, and heat reaching the sensor zone. The third needs a
   heat-path model or identification; a power meter can't give it.

### C3 State registers (per interval, not per campaign)

- **Power state:** `state_id`, description, measured V, measured I, derived W,
  fan state (`on`, `off`, `absent` or `unknown`), firmware mode, start and end
  UTC.
- **Airflow state:** `state_id`, vent configuration ID, measured open area, any
  forced-flow device and its state, airflow proxy if available, start and end
  UTC.

An interval with fan state `unknown` can't be used for I1, because heat and
ventilation can't be separated. Record it; don't delete it.

### C4 Humidity and pollutant claims

A temperature-only campaign cannot support an RH claim. If RH is an endpoint:

| Channel | Requirement |
| --- | --- |
| Reference RH | independently characterised, with calibration record and stated uncertainty |
| Reference temperature | co-located with the reference RH |
| Sensor RH | the enclosure sensor's own RH |
| Sensor temperature | already required |

Report RH differences in percentage points, and also compare vapour pressure
`e = (RH/100)·e_sat(T)`. If the enclosure only warms the air, vapour pressure
is conserved and the RH drop follows from `e_sat(T)`; wetting, condensation,
air exchange and sensor response can break that, which is what makes it a
test. Register how wet intervals are handled before the run; don't remove them
afterwards because they look bad. If there is no RH reference, the campaign is
temperature only and the RH endpoint is deferred.

Better temperature or RH does not show better PM or gas accuracy, especially
where the existing correction was fitted to onboard variables. Putting a
corrected RH into a fitted PM equation needs retesting against pollutant
references, in a later campaign.

### C5 Calibration

- Check every sensor and the reference against the same standard before and
  after the campaign, with dates. Drift between the two checks is an
  uncertainty component (R3.1 #6), not a correction to apply quietly. If drift
  exceeds the stated uncertainty treatment, mark the affected comparison
  inconclusive and keep all the data.
- Take setup photos if permitted.
- Material properties are needed per claim, not for everything:

| Claim | Required | Optional |
| --- | --- | --- |
| Whole-design ranking (V0, V0P, V1) | matched exposure, characterised reference, geometry by direct inspection | `alpha`, `eps` |
| Finish effect (I4) | documented finish change on matched hardware | measured `alpha` and `eps` (paint changes both) |
| Dissipation (I1) | measured V·I, fixed airflow | heat-path model |
| Parameterised or transfer prediction | `alpha`, `eps`, wall conductivity and thickness, vent open area | — |

Missing CAD is not a reason to skip usable hardware; measure the existing
enclosures directly. A controlled heater gives the response to that imposed
heat path; mapping it back to distributed electronics heat needs an explicit
check. A drawing can't close a `measurement` field, and changing how a
parameter is obtained needs a written amendment made in advance.

---

## Acquisition and data

### Sampling

- Sample every 60 seconds for exactly 24 hours: 1,440 planned slots, with
  synchronised UTC timestamps. A different cadence needs a protocol and code
  amendment made before the run.
- Record sensor temperature, reference temperature, incident solar irradiance
  and local wind speed. Declare which wind is recorded (free-stream or a
  station height), because it decides which convection correlation applies
  (R3.4). Record dewpoint, so sky temperature can be computed rather than
  assumed. Log cloud and sky conditions, wetness, interventions and reference
  aspiration separately.
- Zero sunlight alone does not mean a clear sky. Effective sky temperature
  needs its own measurement or model, with its uncertainty.

### R2.1 Files: one CSV per enclosure plus a campaign manifest

The intake (`analysis/colocation_intake.py`) checks one sensor-reference pair
per CSV. So each enclosure gets its own CSV on identical UTC timestamps, and a
campaign manifest ties the files together. A single wide CSV was rejected: it
would change the tested intake schema for no gain. Don't mix the two layouts.

Passing the intake file by file does not show that the enclosures were paired
or that the campaign is authentic; the manifest carries that claim. Its
validator is built on a kept branch (`impl/t1-campaign-manifest-20260929`) and
waits for the first real data (R2.4).

### R2.2 Campaign manifest

| Field | Rule |
| --- | --- |
| `campaign_id` | unique, never reused |
| `variant_id` → `csv_path`, `metadata_path` | one row per arm (V0, V0P, V1, optional V0-U) |
| `sensor_id`, `reference_id` | the same `reference_id` across arms is expected and correlates them (R3.3) |
| `protocol_commit` | git SHA of the protocol frozen before acquisition |
| `csv_sha256`, `metadata_sha256` | raw-byte hash of every file, recorded at acquisition |
| `calibration_record_ref`, `uncertainty_record_ref` | per instrument |
| `intended_window_start_utc`, `intended_window_end_utc` (exclusive), `cadence_s` | declared, not inferred |
| `event_log_path` | interventions and maintenance |
| `custody`, `authorized_storage`, `retention` | where the raw bytes live; private raw data never goes in git |

### R2.3 Data rules

- Timestamps are ISO-8601 UTC, exactly on the declared grid, with an exclusive
  end. No interpolation and no rounding into a passing intake.
- An empty field means missing. Missing is never zero and never imputed.
- **Pairing is per comparison.** A slot counts for a comparison only if both
  arms of that comparison have finite values at the identical timestamp.
  All-arm complete slots are used only for genuinely joint comparisons, so a
  missing optional arm never discards a valid V0/V0P pair. A slot missing in an
  arm is dropped from that comparison and counted, never back-filled.
- Report per-arm coverage, per-comparison coverage and all-arm coverage
  separately, and check whether missingness depends on temperature or power
  state.
- Extra channels (internal temperature, input power) go in a separate
  instrument file keyed to the same timestamps, so the intake schema is not
  widened.
- Thresholds are never relaxed after the fact. If coverage falls short, keep
  the result as incomplete and record the extension or stop decision (C8).

### R2.4 Implementation

The manifest validator, cross-arm pairing check and their tests are
implementation work (ticket T1 in
[implementation-tickets](specs/implementation-tickets-2026-09-24.md)). Any
such change must keep the single-pair intake behaviour and add a compatibility
test.

---

## Data-quality thresholds

These decide whether the data can be reviewed. They are not thresholds for
validating the model. They apply per arm; cross-arm coverage will be lower and
is reported as its own number.

- At least 90% paired, finite samples over the intended 24 hours (1,440 slots).
- At least 120 paired minutes with solar ≥ 200 W/m², and at least 120 with
  solar ≤ 5 W/m². These guarantee two hours of each condition; they are not
  independent samples.
- A declared expanded paired-temperature uncertainty U95 ≤ 0.5 °C, covering
  calibration, reference radiation and aspiration, drift, position mismatch
  and covariance. This is a target for resolving effects of a few degrees, not
  a claim about the hardware on hand. See R3.2 for what it requires.

---

## Uncertainty

### R3.1 Components

Each is a standard uncertainty `u(x_i)` with a sensitivity coefficient
`c_i = ∂f/∂x_i` (`jcgm2008gum`); where the model isn't analytically
differentiable, use the Guide's numerical form (5.1.3 Note 2). Units are °C
unless stated.

| # | Component | Type | Notes |
| --- | --- | --- | --- |
| 1 | Sensor calibration | A/B | per unit, from its certificate |
| 2 | Reference calibration | B | from its certificate |
| 3 | Reference radiation and aspiration error | B | the reference is not truth; `nakamura2005` shows a corrected passive shield's residual is limited by its reference |
| 4 | Sensor-to-reference position mismatch | B | height and exposure difference |
| 5 | Clock alignment | B | becomes a temperature error through the local time gradient |
| 6 | Drift between the before and after checks | B | bracketing checks required (C5) |
| 7 | Solar and wind measurement | B | enters the as-built prediction, not the bias itself |
| 8 | Model inputs for the as-built prediction | B | `h_c` dominates (R3.4) |
| 9 | One reference serving all arms | — | covariance; see R3.3 |

Each component gets a measurement equation, a distribution, an evaluation
method, a sensitivity coefficient and a basis for any correlation. Type A or B
describes how the uncertainty was evaluated, not the instrument, and Type B
does not automatically mean few degrees of freedom.

### R3.2 What U95 ≤ 0.5 °C requires

`U = k·u_c` (GUM Eq. 18), so U95 ≤ 0.5 °C means `u_c ≤ 0.25 °C` at `k = 2`.
And `k = 2` gives about 95% only under the four GUM G.6.6 conditions:
well-behaved input distributions, comparable contributions, an adequate
first-order approximation, and more than about 10 effective degrees of freedom.
Those have to be shown, not assumed. If one Type B component dominates with few
degrees of freedom, `k = 2` does not deliver 95%; choose the coverage method
from the actual inputs.

### R3.3 One reference for all arms

For simultaneous readings `A` and `B` against the same reference reading `R`:
`b_A = A − R` and `b_B = B − R`, so `b_A − b_B = A − B`. The reference cancels
exactly in the difference. In general
`Var(b_A − b_B) = Var(b_A) + Var(b_B) − 2·Cov(b_A, b_B)`, so ignoring a
positive shared-reference covariance overstates the uncertainty of a
difference (and understates it for a sum or mean).

- **Difference between arms** (the main comparison): the shared-reference term
  cancels for simultaneous readings of the same reference. Derive that
  cancellation with GUM Eq. 13 or 16 and the correlation `r` stated; don't
  assume it. Position mismatch,
  per-probe calibration and non-identical timestamps do not cancel and must be
  carried.
- **Absolute bias of one arm:** the reference uncertainty enters in full.

Treatment (GUM §5.2.4): write the model so the shared reference enters once, as
an explicit independent input, rather than estimating pairwise covariances.

### R3.4 Model inputs for the as-built prediction

- `h_c` dominates and cannot be pinned to 10% (`berdahlbretz1997`). Carry it as
  a band.
- The model's `h = 5.0 + 4.0·U` is mis-referenced: it is Jürges' correlation,
  whose intercept is 5.6, valid for `U ≤ 5 m/s`, on free-stream wind. Against
  station wind `U10` the measured slopes are 0.90–2.9. This is why the recorded
  wind has to be declared.
- `T_sky = T_air − 20 K` is unsupported; compute sky temperature from dewpoint
  instead.
- An error in `alpha` becomes 0.6 K per 10 W/m² of solar heat gain
  (`levinson2010`).

### R3.5 Two thresholds that must never be mixed up

| | Data readiness | Scientific comparison tolerance |
| --- | --- | --- |
| Status | defined: the data-quality thresholds above | not set; the owner or application must supply it |
| Means | the data can be reviewed | a difference matters scientifically |
| Set by | instrumentation and coverage | the application tolerance plus the registered as-built model uncertainty |

Never use the simulated 1.4771 °C nominal advantage, or any other model output,
as an acceptance threshold. Both thresholds are frozen before comparative
results are looked at. If no application tolerance is stated, the study reports
bias and uncertainty only, with no pass or fail.

---

## Analysis

### Metrics

Bias is sensor minus reference. Report signed bias and absolute error
separately (a cooler sensor is not a more accurate one), plus MAE, RMSE,
paired availability and time traces, for each arm, split by the measured sun
and wind conditions registered before the run. Treat night cooling as
depending on radiation and heat load.

Don't fit new model parameters to this data and call it validation; data used
for fitting is development data, and needs a separate later campaign to test.
The 1,440 samples are correlated in time (`arlot2010` on the i.i.d.
assumption), so don't report confidence intervals that treat them as
independent.

Checking the model against the data needs an as-built prediction with its
propagated uncertainty and an application tolerance, both registered before
comparison. Neither exists yet, so the intake never classifies a pilot as
VALIDATED.

### C6 What each comparison can answer

| Comparison | Answers | Does not answer |
| --- | --- | --- |
| V0 against V0P | the effect of the documented finish change on matched hardware | `alpha` alone (paint moves `eps` too); any vent or material effect |
| V0P against V1 | a practical ranking of two complete designs | which of geometry, ventilation, sensor position or heat coupling caused it |
| I1 load states in one unit | °C per W for that unit and configuration | the same coefficient in another geometry |
| I3 vent variants, all else fixed | the open-area effect for that material and heat source | the same effect at another power state, unless crossed (C7) |
| Any arm against the reference | absolute bias, with the reference uncertainty in full | — |
| Two arms, simultaneous, same reference | relative bias, with the shared-reference term cancelling | position mismatch, per-probe calibration, timestamp mismatch |

Three distinct designs cannot support a general law across material, finish
and vent geometry. That needs controlled single-parameter contrasts,
replication and a genuinely withheld geometry family (C7).

### C7 Replication and the follow-on

- Cross the design contrast with power state. More venting may change power
  sensitivity as well as solar bias; plan the interaction before fitting, or it
  can't be estimated.
- Use independently printed units, calibrated probes where available, and
  positions rotated in balanced blocks. Track enclosure, probe and position IDs
  separately.
- Work out the number of replicates from the smallest useful effect and the
  pilot variance, after commissioning. If the pilot can't support that count,
  reduce the claim, not the standard.
- Transfer needs a genuinely withheld geometry family; a finish replicate is not
  an unseen geometry.

### C8 Stopping and extension

1. 24 hours is the commissioning minimum, not a complete campaign.
2. Extend only for missing exposure coverage, never because a favoured design
   is winning. The triggers are registered joint coverage, in particular the
   low-wind, high-sun cell the research question targets, and intervention
   coverage: completed, counterbalanced I1 load blocks. The sunny and dark
   minute counts alone are not enough.
3. Declare the maximum extension window before looking at comparative results.
4. If coverage is still incomplete at the end of that window, keep the result
   as incomplete and record the stop decision. Never relax a threshold after
   seeing outcomes.
5. If the weather never provides both conditions, keep the partial run and
   extend it with a new, pre-declared window.
6. One 24-hour campaign cannot establish seasonal or general accuracy, whatever
   it shows.

### C9 What each claim needs

| Claim | Earned by | Status |
| --- | --- | --- |
| Enclosure bias exists, with this size | absolute comparison against the reference | association until data exists |
| Finish changes bias | I4, matched hardware | intervention, for (`alpha`, `eps`) jointly |
| Dissipation changes bias | I1 | intervention, in °C per W |
| Ventilation changes bias | I3 | intervention, conditional on material and heat source |
| V1 beats V0P | I5 | a bundled design effect. With arms randomly assigned to positions or time blocks it is a causal bundled effect; without randomisation it is association. Never an isolated vent or material effect |
| Solar drives the bias | I2 | intervention |
| "Self-heating dominates" or "solar dominates" | — | not claimable without I1 and I2 together |
| Better T/RH improves PM or gas | — | not claimable; needs a separate campaign with pollutant references |

---

## Intake and reproduction

Rehearse the whole chain on synthetic data with known answers:

```bash
PYTHONPATH=. python -m analysis.colocation_rehearsal --out-dir build/rehearsal
```

It runs the intake and then `compute_metrics` on the same bytes and writes
`rehearsal.json`. Synthetic input always comes out `SYNTHETIC_ONLY`.

Check one arm's file (capitalised names are placeholders):

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

| Exit code | Meaning |
| --- | --- |
| 2 | Malformed or incomplete evidence |
| 3 | Structurally sufficient, but synthetic only |
| 0 | A physical arm eligible for human review. It does not mean the model agrees, or that provenance is authenticated |

Metadata strings and a checksum can't prove permission, calibration or when
the data was collected; a reviewer has to read the referenced records and the
protocol commit.

The synthetic tests cover duplicate slots, missing edges and channels,
malformed weather and time fields, bad uncertainty values and keeping synthetic
data from being promoted:

```bash
PYTHONPATH=. python -m unittest discover -s analysis/tests -p test_colocation_intake.py -v
```
