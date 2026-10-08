# Research-direction decision record — 2026-09-21

Current disposition: the owner-authorized v2 question is how much target-design
calibration measured geometry, material and power data plus shared thermal laws
can replace. [ENC-1](OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions)
supersedes the earlier unresolved owner-adoption question. Direction B remains
the first-stage estimation-only floor, and PI/physical decisions remain open.
The [roadmap](../ROADMAP.md) is the only active plan, with dependency order and
completion evidence. The dated proposals below preserve history without adding
work authorization.

The [executed correction](results.md#transient-result) tests a single-node
thermal step and weather integration. Later identifiability must cover plausible
parameters/noise and actual I1/I2/ventilation interventions. Local Fisher
information alone is insufficient. A simpler predictor is acceptable. Later
confirmation needs geometry and future-period holdouts, independent units or
swaps, measured deployment inputs distinguished from frozen coefficients,
calibration budgets, simpler physical/empirical baselines and regime-specific
error/coverage. No arbitrary precision percentage is an application requirement.
Heated cold-climate boxes and PM-correction effects remain separate. The
cross-shield refitting claim remains unverified pending its actual source.

Historical decision aid. Base:
`main` at `84e0ef3`. Companion to the historical owner draft [PR #20](https://github.com/500ft/sensor-enclosure-thermal-design/pull/20)
(the retired question draft, available through [history](history/README.md)). Authority: scope decision in
[PHD_SCOPE_AND_NOVELTY.md](PHD_SCOPE_AND_NOVELTY.md); result in [studyA_nondimensional.md](studyA_nondimensional.md).
The analytical results below do not supply thermal co-location measurements;
older deployment/electronics evidence remains separate.

## 1. Historical comparison of the two directions

The original decision aid compared these questions:

| | **Direction A — pre-build prediction (narrowed)** | **Direction B — bounded engineering study (PR #20)** |
|---|---|---|
| Question | Do an internal-dissipation ratio, a vent-flow group and a wall-Biot group predict the onboard-T/RH bias of a low-cost 3D-printed AQ enclosure *before fabrication*, and where does that prediction fail? | How do surface finish and ventilation geometry affect the T/RH bias of *this project's* enclosure under varying solar and wind? |
| Scale | **Reworded 2026-09-24 — automatic degree verdicts withdrawn.** Judge on *useful transfer, accuracy, calibration cost and falsifiable claims*, not on beating one baseline. Still requires experimental validation on held-out geometries | Design/ranking study; honest, achievable with the existing three variants |
| Physics it adds | Internal dissipation, resolved vent flow, wall conduction. **Corrected 2026-09-24: these are axes classical *meteorological shield* work omits — they are NOT unaddressed generally. Air-STORM (`shlipak2025`) already forward-models an AQ enclosure from materials, weather and internal heat generation.** The narrowed contribution is predicting *measurement bias* on an untested geometry with quantified uncertainty, not forward modelling as such | None new; applies known shield physics to one enclosure |
| Demotes to | Direction B if transfer is not demonstrated — a research judgement on the evidence, **not** an automatic consequence of one benchmark | — |
| Needs | Multi-geometry/material printed variant set + held-out test + CHT | Three variants + reference, 24 h+ |

The original recommendation to pursue A did not adopt it. Direction B needs
physical observations of its own, and its pilot becomes a held-out check for A
only if the predictor and split were fixed without fitting to that geometry.
See the selected direction below and the current ENC-1 disposition above.

## 2. Historical Direction A proposal

- **Main hypothesis (H1):** in the solar-driven regime, signed enclosure bias is predicted before
  fabrication by `(Pi_G, N_Q, N_r, f_sky, Pi_delta)` plus a wall-Biot correction, to within the
  registered instrument uncertainty, on geometries *not used* to build the law.
- **SQ1** — which groups predict signed bias in the solar-driven regime? *(Study A: answered
  analytically; see §3.)*
- **SQ2** — how do wall conduction (Bi) and resolved vent flow (Re_vent) change the prediction for
  printed polymer geometries? *(Study B: CHT; not started.)*
- **SQ3** — where does the reduction fail, and does that failure predict downstream PM/gas
  calibration error? *(Study A maps the analytical failure regime; the calibration link is
  untested.)*
- **Competing explanation (must be tested, not dismissed):** a **post-build empirical correction**
  (fitted energy-balance coefficients per built enclosure, Bernard et al. 2019 style; or a
  met-variable regression, Nakamura & Mahrt 2005 style) predicts as well or better at lower cost.
  **This is the K2 benchmark.** It must be implemented as an explicit comparator on the same
  held-out data before any pre-build claim.

## 3. What the analytical evidence supports today (ANALYTICAL only)

From `python -m analysis.nondimensional` at `84e0ef3` (1944-point daytime DOE; regimes set by
mechanism, see `nondimensional.regime`):

| Regime | n | abs residual med / p95 | rel residual med / p95 | Reading |
|---|---:|---|---|---|
| solar_driven | 1220 | **0.10 / 0.46 °C** | 1.6% / 15.9% | law holds in absolute terms |
| near_zero (|ΔT|<1 °C) | 169 | 0.05 / 0.47 °C | n/a | relative error meaningless |
| radiation_dominated (ΔT<0) | 349 | 0.36 / 0.47 °C | n/a | small absolute error, sub-ambient |
| high_nonlinearity (ΔT>20 °C) | 206 | **1.9 / 14.2 °C** | 6.2% / 19.5% | **law fails** |

Overall R² = 0.972. **Claim the evidence supports:** the five-group linear law reproduces the
lumped model's solar-driven daytime bias to ~0.1 °C median / <0.5 °C p95, and fails by several °C
once bias exceeds ~20 °C. **Corrected 2026-09-25 — the previous sentence here claimed a universal
collapse had been "falsified at the preregistered 3 % band", which contradicted the very next
paragraph and is withdrawn.** Nothing was falsified and nothing was preregistered: the exact
nonlinear dimensionless balance is consistent with the solver to tolerance (max residual 5.478e-9
over 1,944 points), and the 3 % relative band is a **selected approximation threshold** applied to
an **exploratory** exercise with no dated pre-run record. What the residual shows is that the
*linearised* form loses accuracy at large bias.

**Open methodological point for the owner** *(revised 2026-09-24: this is a threshold on
approximation error, not a scientific kill criterion, and it was **not** preregistered — no dated
pre-run record exists, so the exercise is exploratory)*: the threshold was stated as *relative*
3%, but the law's natural error is *absolute* °C, and the physical acceptance will be an absolute
uncertainty (U95). A relative band near ΔT→0 is unphysical. Proposal: **re-register the criterion
as absolute °C against the registered U95**, recorded as a prospective amendment — not applied
retroactively to call the current result a pass.

## 4. Historical Direction A criteria and selected scope

- **K1** — no reproducible physical bias above the registered instrument + propagation uncertainty.
- **K2** — pre-build groups do not predict *held-out* geometries better than the post-build
  benchmark (§2) after honest complexity accounting (parameters counted on both sides).
- **K3** — internal dissipation, vent flow and wall Biot cannot be independently varied *and*
  measured in the printed variant set.
- **K4** — the CHT/lumped disagreement cannot be bounded well enough to design the pilot (Study B).

**Revised 2026-09-25 — no automatic demotion.** A fired criterion is *evidence for a judgement*,
not a switch. Weigh it against the others, the available units and exposure, and the cost of the
calibration it would take to do better. Presenting the work as Direction B is a legitimate outcome
reached on the evidence, never an automatic consequence of one criterion.

**Direction selected 2026-09-25: B (bounded engineering study) is the immediate scope.** Direction A
is retained as a conditional follow-on, activated only by a credible held-out design family, frozen
predictor provenance, and validation resources. Rationale: B yields useful evidence without first
requiring a new geometry family, a CFD installation, or a broad novelty claim — and its measurements
remain usable by A later. "A with B as a floor" was not a guarantee: B needs hardware, reference
characterisation, permission and observations of its own.

## 5. Contribution boundary and permitted language

Contribution, if A survives: **a regime-dependent collapse domain and its failure boundary for
low-cost printed enclosures with internal dissipation**, with pre-build prediction demonstrated on
held-out geometries against a post-build baseline. **Not** a universal framework across sensing
systems. Claim levels: `simulated` (all of §3), `experimentally supported` (none yet),
`not supported` (universal collapse).

## 6. Claim / evidence matrix

| ID | Claim | Class | Evidence | Status | Permitted wording | Prohibited wording |
|---|---|---|---|---|---|---|
| C1 | dark enclosure has solar self-heating bias | ANALYTICAL | `thermal_bias_results.md` §2; day table | simulated | "the model predicts ~19 °C at 1000 W/m², 0.5 m/s" | "measured", "observed" |
| C2 | paint and passive shielding are separate variants (V0P vs V1) | ANALYTICAL | `thermal_bias.build_variants`; A3 screen | simulated | "same-geometry painted control" | "shield is better" (unqualified) |
| C3 | night bias can change sign with sky temperature | ANALYTICAL | `thermal_bias_results.md` night section | simulated | "conditional sign reversal in the model" | "nights are cold-biased" |
| C4 | five-group law is exact for the *linearised* model | ANALYTICAL | `studyA_nondimensional.md` §2 | derived | "exact for the linearised balance" | "exact" (unqualified) |
| C5 | **CORRECTED 2026-09-24** — the *linearised* form loses accuracy above ~20 °C; the **exact nonlinear dimensionless balance holds to solver tolerance** | ANALYTICAL | `test_nondimensional.ExactBalanceTests` (max residual 5.478e-9 / 1,944 pts); `LinearisationErrorTests` | simulated | "the linear approximation degrades at large bias" | "collapse fails", "no universal law", "kill criterion tripped", "validated" |
| C6 | printed-wall Biot is a first-order validity concern | ANALYTICAL (hand calc) | `studyA_nondimensional.md` §3 | derived from handbook k | "Bi ~0.1–0.6 for k=0.13–0.29 W/mK at 3 mm" | "printed walls are non-isothermal" (as measured fact) |
| C7 | internal dissipation is an under-addressed design axis | LITERATURE (abstract-level) | `PHD_SCOPE_AND_NOVELTY.md` §1 | **full-read pending** | "not found in the checked sources" | "no one has done this", "novel" |
| C8 | physical validation is pending | — | `SPRINT_TASKS.csv` EN-R03 blocked | blocked | "pending" | any agreement/accuracy claim |

## 7. Relationship to PR #20

PR #20's question is Direction B, and its literature review (Tarara 2007, Holden 2013, Theisen
2020, Botero 2022, Deford 2025) is the correct base for B. It does not cite the Direction-A
competitors (Bernard 2019, Nakamura & Mahrt 2005, Barkjohn/Couzo) — that is Tuesday's work
(T1/T2), not an edit to #20. Merge/edit of #20 is the owner's call; if A is chosen, #20's
"Question" section needs one added sentence naming the pre-build prediction aim and the post-build
benchmark. Recorded here as a follow-up, not applied.

## 8. Unchanged

No physical data, permission, hardware, geometry or funding is created by this record. `EN-S02`,
`EN-R03`, `EN-S09B`, `EN-S11` stay blocked; CAD deferred; FEA a stub.

## 9. Literature-to-experiment translation (T3, 2026-09-22)

Each surviving gap from §2/§6 maps to one observable the pilot must record, the instrument or model
input that supplies it, and the shortcut that is **not** allowed. Model inputs feed
[`thermal_bias.ASSUMPTIONS`](../analysis/thermal_bias.py) entries currently marked
`bounded`/`TODO-from-lab`; nothing below is measured yet.

| Gap (group) | Observable to record | Instrument / model input | Not allowed |
|---|---|---|---|
| Internal dissipation (`N_Q`) | Electrical input power at the enclosure, and the fraction reaching the sensor zone | In-line power meter or shunt on the node supply (W, logged at cadence); sensor-zone vs electronics-zone temperature difference; replaces `Q_int_V0` / `Q_int_shielded` | Inferring `Q` from nominal board/datasheet power |
| Vent flow (`Re_vent`, `A_vent/A_surface`) | Vent count, hydraulic diameter and open area; an airflow proxy at the vent (velocity or ΔP) *or* a declared CHT flow boundary | Calipers/drawing for geometry; hot-wire or thermal anemometer at a vent, or CHT (Study B) with the flow BC stated | Substituting ambient wind for vent velocity or vent Reynolds number |
| Wall conduction (`Bi`) | Wall thickness and material conductivity for each printed variant | Calipers (mm); `k` from a traceable datasheet range for the *specific* filament, or a measured value; replaces the handbook `k` in `nondimensional.biot` | Treating the filament name/colour as conductivity evidence |
| Optical (`alpha`, `eps`) | Solar absorptance and long-wave emissivity of each finish | Reflectance/emissivity measurement, or a bounded range with source; replaces `alpha_V0`, `alpha_shield`, `eps_surface` | Equating colour name with `alpha`/`eps` |
| Solar / wind forcing (`Pi_G`, `h`) | Irradiance on the projected area and wind at sensor height, at the sample cadence | Pyranometer (W/m²) and anemometer (m/s) co-located at matched height; already required by [COLOCATION_PROTOCOL.md](COLOCATION_PROTOCOL.md) | Using a distant station's wind as the local `h` input |
| Sky forcing (`N_r`, `f_sky`) | Sky/cloud condition; sky view of the sensor element | Sky notes at minimum; IR sky temperature if available; `f_sky` from geometry, declared per variant | Assuming a fixed 20 K clear-sky depression at night |
| Failure boundary (SQ3) | Which regime each observation falls in (`nondimensional.regime` of the *as-built* prediction) | Computed from the inputs above **before** comparison; recorded with the prediction | Assigning regimes after seeing the residual |

Done when every gap has an observable and a named instrument or model input; the pilot data
contract (Thursday, R2) carries these as required columns. No threshold here changes the 24 h
data-readiness criteria in the protocol.

## 10. Competitor test (T2, 2026-09-22) — source-level, six full reads

[COMPETITOR_MATRIX_2026-09-22.csv](COMPETITOR_MATRIX_2026-09-22.csv); per-source assessments in
`ProConsList/` (`bernard2019`, `nakamura2005`, `vonrohden2022`, `barkjohn2021`, `couzo2024`,
`ishizuka2012`), all read in full. The abstract-level scan of 2026-09-16 mis-cited two authors;
see the erratum in [PHD_SCOPE_AND_NOVELTY.md](PHD_SCOPE_AND_NOVELTY.md).

What the checked sources establish, stated as "not found in the checked sources," not "no one has
done this":

- **No checked source predicts enclosure bias before fabrication.** Bernard 2019 and von Rohden 2022
  fit coefficients to the built object; Nakamura 2005 and Couzo 2024 are empirical corrections;
  Ishizuka 2012's pre-build design equations are indoor, still-air, no solar.
- **Internal power dissipation** is absent as a modelled term in Bernard, Nakamura, von Rohden and
  Barkjohn; asserted-but-unmeasured in Couzo; present only in Ishizuka (indoor).
- **Wall conduction / Biot** is absent in all six (lumped into a fitted surface loss in Ishizuka;
  boom conduction included but not parameterised in von Rohden).
- **Nakamura's `X = Rad/(ρ·Cp·T·U)` is already a single dimensionless forcing group that reaches
  R² 0.98** for one shield. This project's `Pi_G` generalises `X` (absorptance, shading, area
  ratio, radiation coupling); it is not a new idea, and the added groups (`N_Q`, `Bi`, `Re_vent`)
  must earn their place on held-out data.
- **Ishizuka's `X = Re·β²/(1−β)` chimney parameter** is the concrete basis for the vent-flow
  group in Study B; its constants are apparatus-specific and do not transfer.

**K2 benchmark (revised 2026-09-24).** Comparators: a Bernard-style two-coefficient energy-balance
fit and a Nakamura-style single-group regression. Two separate contests, never conflated:

- **(A) No-target-calibration.** Freeze parameters from drawings, independently characterised
  materials/electronics and *training* designs; predict a **withheld geometry family** without using
  its thermal response to tune anything. A finish replicate is not an unseen geometry.
- **(B) Limited-calibration.** Allocate an explicit calibration period on the new geometry and fit
  **all** eligible methods on that identical allocation; compare on later, disjoint time blocks.

A per-enclosure fitted baseline **cannot** both use target-enclosure calibration data and be called
a no-target-data comparator — it is a *calibrated reference performance level*, labelled as such. A
source-trained baseline needs an explicit rule for assigning coefficients to a new design.

Report absolute error, tail error, interval coverage, **calibration effort** and computational
effort **separately**, with acceptable accuracy defined from the intended application **before**
viewing outcomes. **Counting named dimensionless groups is not a complexity penalty** — audit actual
calibrated parameters, empirical closures and property measurements. A smaller model can be useful
at comparable accuracy with less target calibration even if a well-calibrated model has lower error.

*(Full rewrite of the comparison and verification contracts is critique work package 3, outstanding.)*
