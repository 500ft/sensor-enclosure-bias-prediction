# PhD scope & novelty gate — 2026-09-16

Historical scope review and scientific errata. It is retained for the corrected
claims and source record. [ROADMAP.md](../ROADMAP.md) alone defines current work;
older degree-scope judgments and work proposals below are not active milestones.

**Purpose.** Resolve, before investing in Studies B–D, the question the proposal itself flags as
exposed: is a dimensionless-collapse prediction of enclosure sensor bias a **PhD-scale open axis**,
or an **MS-scale design study**? This document records the novelty check, the Study A theory result,
the honest verdict, and the narrowed framing that reaches PhD scale.

## 1. Novelty verdict: **borderline — PhD only if narrowed**

A literature check (2015–2026, cross-checked against the repo's 26-source matrix) found:

**Established (not novel):**
- Radiation-shield/screen error and its wind + shortwave dependence — Nakamura & Mahrt 2005 (JTECH
  22:1046), empirical correction to ~0.13 °C RMSE; worst case low-wind + high-irradiance.
- Standard test methods already in the matrix: WMO No.8, Duvall 2021 (EPA 30-day protocol),
  ASTM D8406-22, CEN/TS 17660-1:2021.
- **Energy-balance shelter models already reduce error to a few coefficients** — Bernard et al.
  2019 (*Climate* 7(2):26): the direct methodological competitor.
- CFD-fitted per-geometry correction curves — repo's Liu 2023, Jin 2026.
- Low-cost AQ enclosure self-heating T/RH bias (~2.6 °C) — Barkjohn 2021, Couzo 2024 (*Atmosphere*
  15:415) — documented and empirically corrected post-hoc.
- Dimensionless heat-transfer framework (Biot/Nusselt/Reynolds) — textbook.

**Open / under-addressed:**
- **No published dimensionless COLLAPSE of enclosure bias onto a-priori groups across
  geometry + material + ventilation + wind + irradiance simultaneously.** Existing models are
  empirical met-variable regressions (Nakamura–Mahrt), per-shelter coefficients fitted *after
  building* (Bernard), or single-geometry CFD curves (Liu/Jin).
- **Internal-dissipation ratio as a design axis** — classical shields have ~no internal power; AQ
  enclosures have watts. No source combines self-heating + vent geometry + surface optics in one
  predictive scaling.
- **Predict-before-build** — no validated forward model from material/finish/vent geometry to bias
  prior to fabrication.
- **3D-print-specific effects** (filament, finish, layer-induced emissivity; and low-k wall
  conduction — see Study A Biot gate) tied to a scaling model.

**Why borderline:** the *method* (similarity collapse) and the *internal-dissipation + predict-
before-build* framing are genuinely under-addressed, but every underlying phenomenon is established,
so novelty lives in **synthesis + method**, not new physics. Two substantive risks the proposer must
own: (1) radiation-dominated, low-Reynolds, buoyancy-mixed geometries may not nondimensionalise as
tidily as forced-convection Nu–Re; (2) **[corrected 2026-09-24 — see Erratum 2]** the original
second risk claimed Study A had shown the collapse is "not universal". It had not; that residual
measured linearisation error. The real limitation is that the *linear approximation* degrades at
large bias, and that physical accuracy remains untested.

## 2. Study A result (done) — dimensionless reduction holds; the *linear approximation* is bounded

**Corrected 2026-09-24 (see Erratum 2).** See [studyA_nondimensional.md](studyA_nondimensional.md).
The lumped model reduces to five groups at fixed `tau` (`Pi_G, N_Q, N_r, f_sky, Pi_d`), and the
**exact nonlinear dimensionless balance is consistent with the solver to tolerance** (max residual
5.478e-9 over 1,944 points). The *linearised* closed form predicts the nonlinear solver to
**~0.23 °C / 2–4 % median** and exceeds the selected 3 % relative approximation band at large bias.
**That is approximation error, not a failure of dimensionless representation, and not a kill
criterion.** The Biot gate shows printed polymers (`Bi ~ 0.1–0.6`) violate
the isothermal-wall assumption that classical metal-screen physics relies on.

**Consequence for scope:** "bias always collapses onto a few groups" is falsified for the general
case. The defensible contribution is **the collapse domain and its boundary** — where prediction-
before-build works, where it fails, and why.

## 3. The narrowing that reaches PhD scale

Drop general shield physics. Anchor on the one axis meteorology never modelled:

> **Can an internal-dissipation ratio (self-heat vs solar load) together with a vent-Reynolds /
> vent-to-surface area-ratio group and a wall-Biot group predict the onboard-T/RH bias of a
> low-cost 3D-printed air-quality-sensor enclosure — and its downstream PM/gas calibration error —
> *before fabrication*, and where does that prediction break down?**

Three requirements to be PhD, not MS (all from the novelty check):
1. **Experimental**, not simulated only — a designed set of printed material/finish/vent variants.
2. Carries the **internal-dissipation, vent-Re, and wall-Biot** axes shield work omits.
3. **Maps where the collapse fails** (radiation-dominated regime) rather than assuming universality.

If the experimental collapse cannot beat Bernard's post-build coefficients on *prediction*, this
is honestly an MS design/ranking study and should be presented as such.

## 4. Reframed studies

| Study | What | Status |
|---|---|---|
| **A** | Nondimensional reduction + approximation test on the model | **Done** — exact balance consistent to solver tolerance; the *linearised* form degrades at large bias. Physical accuracy untested |
| **B** | DOE over the model + CHT (`chtMultiRegionFoam`) on a subset with mesh-convergence; **add wall conduction (Biot) and resolved vent flow** the lumped model omits | Analytical DOE runnable now; CHT needs toolchain (FEA stub) — Owner/allocation gated |
| **C** | Pilot: 3 printed enclosures (**varied material/finish/vent**, instrumented for internal T + self-heat power), 1 reference, 2 weeks, through the committed intake gate + rehearsal; **Study-A prediction recorded before deployment** | Physical — PI/permission/hardware gated |
| **D** | Decisive: full material/finish/vent-ratio DOE, environmental-chamber control of wind + irradiance, two climates (adds the radiation-nonlinearity group) | Funded — chamber time + sensors |

## 5. Literature-matrix gaps to close (novelty defense)

The 26-source matrix is missing the sources this specific question must argue against. Add, with
full ProConsList assessments (currently characterised at abstract level only — **full reads
pending**, do not cite as assessed until read):

1. **Bernard et al. 2019, *Climate* 7(2):26** — the direct methodological competitor (energy-
   balance shelter coefficients). *Highest priority.*
2. **Nakamura & Mahrt 2005, JTECH 22:1046** — the canonical wind/shortwave shield-error correction.
3. **GRUAN RS41 radiation error, AMT 15:383 (2022)** — nearest heat-transfer/ventilation-speed
   treatment (bare sensor).
4. **Couzo 2024 (Barkjohn 2021 quotes it secondhand) (*Atmosphere* 15:415)** — the PurpleAir self-heating T/RH bias the
   thesis rests on.
5. **Vented-enclosure / electronics-cooling** (A_in/A_out optimum, buoyancy-driven vent flow) — the
   engineering base for the vent-Re / area-ratio axis.

## 6. What is unchanged

No physical data, permission, or PI approval is created by this analysis. `EN-S02`, `EN-R03`,
`EN-S09B`, `EN-S11` stay blocked; CAD deferred; FEA a stub. Studies C/D remain conditional on the
same external gates. This document is a scoping decision aid, not authority to run an experiment or
claim a validated framework. **Do not claim a "framework across sensing systems" — Study A has
already shown the collapse is not universal.**

## Erratum (2026-09-22, after full-text reads)

The 2026-09-16 novelty check above was abstract-level. Full-text reads on 2026-09-22 corrected two
citations: the direct methodological competitor *Climate* 7(2):26 is **Bernard et al. 2019** (first
author was mis-recorded as "Barbaresco"), and *Atmosphere* 15:415 is **Couzo, Valencia and Gittis
2024** (mis-recorded as "Cha"). **Barkjohn et al. 2021 contains no own T/RH bias measurement**; the
+2.6 °C figure is Couzo 2024's. The names in §1/§5 above have been corrected in place; the
substantive verdict is unchanged and is now source-level — see
[COMPETITOR_MATRIX_2026-09-22.csv](COMPETITOR_MATRIX_2026-09-22.csv) and the six new
`ProConsList/` entries (all full-read). The five "matrix gaps" in §5 are closed.

## Erratum 2 (2026-09-24) — novelty narrowed, and two arguments withdrawn

An independent critique, **verified numerically before acceptance**, corrected three things here.

**1. Air-STORM (`shlipak2025`) is a direct competitor and was missing from the competitor matrix.**
It is a transient forward model of an air-quality enclosure driven by material properties, weather
and **internal heat generation**, experimentally evaluated and intended for design planning *before*
build. It therefore **overlaps the broad "forward modelling of an enclosure" claim** made above.
Now added to [COMPETITOR_MATRIX_2026-09-22.csv](COMPETITOR_MATRIX_2026-09-22.csv).

**2. Categorical novelty statements are withdrawn.** Claims that enclosure forward modelling, wall
conduction or internal heat generation have *never* been addressed are **not supportable**. The
statement "nobody has measured the watts" is replaced by the bounded form: *no source located in
this repository's search record reports a measured internal dissipation for a low-cost air-quality
enclosure together with an attribution of the observed T/RH bias to it.* The remaining gap is
**narrower than previously written and provisional** until a documented broader search.

**Narrowed working question:** *can design-known geometry, characterised finish/material properties
and measured electronics power predict ambient T and RH measurement error on a previously untested
printed enclosure, and what accuracy is added by resolving wall conduction, ventilation and
transient response?* Air-STORM's endpoint is enclosure **temperature**; this project's endpoint is
calibrated **measurement bias**, with quantified uncertainty and a transfer test. "Previously
untested" must be defined explicitly — no calibration on that *unit*, on that *geometry*, or no
measurement after fabrication are three different claims. Post-print dimensional inspection can
support an *as-built* prediction but cannot retroactively become a before-fabrication test.

**3. The "PhD if it beats Bernard, MS otherwise" verdict is withdrawn.** Degree scope is an academic
judgement, not a research criterion. The criteria are **useful transfer, accuracy, calibration cost
and falsifiable claims**. Also: a per-enclosure fitted baseline cannot simultaneously use
target-enclosure calibration data *and* be called a no-target-data comparator — it is a **calibrated
reference performance level**, and must be labelled as such. Counting named dimensionless groups is
**not** a complexity penalty; audit actual calibrated parameters, empirical closures and property
measurements instead.

**Superseded elsewhere:** the Study A "no universal law" verdict in §2 is **withdrawn** — see the
corrected verdict in [studyA_nondimensional.md](studyA_nondimensional.md). The exact nonlinear
dimensionless balance holds to solver tolerance (max residual 5.478e-9 over 1,944 points), so
**dimensionless similarity was never falsified**; what exceeded threshold was linearisation error.
