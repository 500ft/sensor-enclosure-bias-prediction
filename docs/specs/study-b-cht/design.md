# Study B — CHT design and dimensionless extension contract (W1/W2, 2026-09-23)

Historical methods reference, not an active workstream. No CHT result was
produced. [ROADMAP.md](../../../ROADMAP.md) controls any future activation;
[geometry inputs](../../cad_geometry_reference.md) and the
[lumped result](../../studyA_nondimensional.md) remain useful. Sections below
retain the original proposal plus its scientific corrections. The former
work-order amendment in section 6 is superseded by removal of that work queue;
it records no new tooling approval.

## 1. The question Study B answers — and the one it cannot

Study A reduced the lumped model to five groups and showed the linear law holds in the solar-driven
regime (~0.1 °C median) and fails above ~20 °C. The lumped model **assumes an isothermal wall
(Bi ≪ 1) and replaces vent flow with an empirical pre-heat closure `Pi_delta`.** For printed
polymer walls Bi ≈ 0.1–0.6, so both assumptions are the open physics.

**SQ2 (Study B):** how do resolved wall conduction and resolved vent flow change the predicted
bias for printed polymer geometries, relative to the lumped model? Output = disagreement in °C,
regime-binned, with the mechanism attributed.

**Not answered by Study B:** whether either model matches reality. That is Study C. A converged
CHT solve is a *numerical* result and inherits every `bounded`/`TODO-from-lab` input.

## 2. Smallest useful CHT study

| Item | Specification | Evidence state |
|---|---|---|
| Geometry set | V0 dark closed box; V0P identical geometry, finish only; V1 passive vented shield | **all dimensions unresolved** — placeholders bound to the owner inventory (EN-CAD-02) |
| Materials | ≥1 printed polymer with registered `k` (route: datasheet range for the *specific* filament, or measured); high-`k` reference (aluminium) only if the owner approves the comparison | unresolved |
| Boundary conditions | solar flux on sun-facing faces (`alpha*G`, sweep 400–1000 W/m²); long-wave to sky (`eps`, `T_sky`) and to surroundings (`T_air`); external convection `h(U)` or resolved external flow; internal heat source `Q` (W, located at the electronics zone); vent openings as pressure-outlet/inlet or resolved; sensor location | inputs from `thermal_bias.ASSUMPTIONS`, versioned as the illustrative baseline |
| Solver modes | (a) **decoupled thermal-FEA** — solid conduction + radiation with `h` as a Robin BC: validates wall conduction/Biot, **cannot** validate vent flow; (b) **CHT** (`chtMultiRegionFoam` or Elmer) — solid + fluid coupled, buoyancy-driven internal flow: validates both. Run (a) first; (b) only on a subset | toolchain not installed; not authorised this week |
| Outputs | sensor-surface temperature; wall temperature gradient (inner–outer, at designated points); vent mass flow / velocity field; heat-flux balance by surface; **ΔT relative to the lumped model** | — |

## 3. Validation hierarchy and acceptance numbers

Order is mandatory; a later step is meaningless if an earlier one fails. The numbers below are
**numerical-verification thresholds with rationale**, not application acceptance limits. The
model-agreement tolerance vs. physical data stays **TBD** until the owner/application supplies it.

| Step | Check | Threshold | Rationale |
|---|---|---|---|
| 1 | Input ledger | every BC value traceable to `ASSUMPTIONS` or the geometry JSON with units + evidence state | no untraceable input |
| 2 | Thermal **benchmark** (§4) | analytical vs solver within the stated per-case tolerance | proves the solver, not the enclosure |
| 3 | Mesh convergence | ≥3 levels; sensor ΔT change between the two finest < **0.1 °C** | one order below the ~0.5 °C absolute p95 of the lumped law's solar regime and below the pilot's 0.5 °C U95 target |
| 4 | Energy balance | net residual (in − out) < **1 %** of total applied heat | standard closure for a converged steady solve |
| 5 | Limiting cases | G=0 removes absorptance/pre-heat effects; Q=0 removes self-heating; `k→∞` recovers the isothermal lumped case; blocked vent → sealed-box limit; open vent lowers ΔT | directional, must match the lumped model's sign behaviour |
| 6 | Lumped comparison | disagreement reported in **°C** per regime bin (`nondimensional.regime`) and attributed to conduction vs vent flow | the actual Study B result |
| 7 | Physical | later (Study C); never inferred from 1–6 | — |

A solve that skips step 2 or 3 is **unverified (`accepted: null`)**, never a pass.

## 4. Thermal benchmark — required before any CHT claim

Section 9 is explicit: the briefing's proven workflow is IGES→MAPDL **linear-static structural**;
it demonstrates no radiation, no conduction–airflow coupling, no natural convection, no energy
balance. Geometry acceptance cannot qualify a thermal solver. Before Study B reports a number, run
these with an **independent expected answer computed first**:

| ID | Case | Independent expected answer | Validates | Tolerance |
|---|---|---|---|---|
| B1 | 1-D plane wall, thickness `t`, conductivity `k`, convection `h` both sides, fixed far-field temperatures | closed form (series resistance); wall ΔT and flux | conduction + Robin BC; the Biot mechanism | 0.5 % on flux |
| B2 | Heated vertical plate in still air | Churchill–Chu Nusselt correlation | external natural convection | 10 % on `h` (correlation scatter) |
| B3 | Two infinite parallel plates, emissivities `eps1, eps2`, temperatures fixed | closed-form net radiative flux | radiation model | 1 % on flux |
| B4 | Sealed heated box, isothermal high-`k` wall, `Q` internal, `h` external | the lumped model itself (`solve_surface_temperature` with `k→∞`) | end-to-end balance in the isothermal limit | 0.1 °C |
| B5 | Bottom-inlet / side-outlet heated box (Ishizuka 2012 configuration) | Ishizuka's *scaling*: internal rise ∝ `Q^0.8` in the sealed limit; monotone decrease with outlet porosity and outlet height | buoyancy-driven vent flow — **trend only**; Ishizuka's constants are apparatus-specific and are not a target | sign/monotonicity |

Tolerances are proposed, marked numerical; register them before the run. B1–B4 have closed forms
and are agent-buildable once a solver exists; B5 tests the mechanism Study A cannot see.

## 5. Reuse assessment (Section 9 deliverable)

**Shared machinery to call (lives in `500ft/engineering-audit`; do not copy):**
`cadloop/orchestrator.py` (job orchestration, bounded host deadlines), `cadloop/volume.py`
(independent expected-volume oracles, explicit unit parsing), `cadloop/fea/inspect_geometry.py`
(imported bounding box/orientation before any BC), the SOLIDWORKS COM authoring + re-drive +
STEP-export route, and the CadQuery oracle pattern. Proven for: native part authoring, named-
variable re-drive (1e-15), oracle agreement (1e-16), STEP round-trip (1e-16). Record the
engineering-audit revision with every run.

**Enclosure-specific components still needed (live here):**
1. `cad/enclosure/geometry.json` — **one** input file read by both the authoring script and the
   checker; every value carries units, evidence state, source and acquisition route
   (`measurement` / `vendor_drawing` / `design_then_inspect`). Generated from the accepted
   parameter register plus explicitly tagged `provisional_design` choices; never two hand-edited
   value sets.
2. An enclosure **oracle** — hand calculation for walls, vents and cutouts accounting for
   overlapping features; CadQuery construction for the plate stack. Shared inputs are fine;
   copying the author's measured output into the expected file is not verification.
3. An enclosure **contract beyond volume**: bounding dimensions and measured orientation, solid
   count, wall thickness at designated points, vent count and open area, sensor stand-off/position,
   plate gaps, and the reference-sensor mounting datum. Equal-volume parts can still have a
   misplaced vent.
4. A per-feature expected-vs-measured trace (shell, vent cuts, holes, sensor mount) with
   immediate checks on rejected equations and null feature returns.
5. A parameter-behaviour proof: change one parameter (vent width; sensor position), recompute the
   expectation independently, verify dependent positions and invariants, restore, recheck.
6. STEP export → re-import in a separate process → repeat the checks; tolerances registered by
   quantity and unit before the run (the briefing's 1e-15 agreements are observations, not a
   universal tolerance).
7. Result states: `accepted: true` only when all required checks pass; missing expected values or
   omitted checks → `null` (unverified); mismatch → `false`. Screenshots and clean rebuilds are
   explanatory only.

**Accepted vs unresolved dimensions:** as of this document **no enclosure dimension is accepted.**
The repository's geometry entries (`A_proj`, `A_conv`, wall thickness, vent area, sensor stand-off)
are `TODO-from-lab`. The owner's own printed revisions exist physically and can close them by the
`measurement` route; that is an owner action (EN-CAD-02), not something this document supplies.

**Mapping CAD → thermal ledger (must be explicit):** the lumped model's `A_conv` is an *effective
coupled* area, not the total CAD surface; `A_proj` is the sun-facing projection at a stated solar
angle; `Q` is heat *reaching the sensor zone*, not board power. Document the mapping, units and
uncertainty before any as-built prediction, and keep the current illustrative defaults as a
versioned baseline.

**Not demonstrated by the briefing (plan separately):** assembly mates, drawing automation and
tolerances, dependent-feature acceptance, any thermal solve, and a formal independent acceptance
check on the structural FEA output.

## 6. Retired CAD allocation proposal

Historical allocation: *CadQuery for parameter-driven families and STEP checks; Onshape for
hand-modelled fixtures.* Section 9 prefers assessing the native SOLIDWORKS-COM authoring route
already proven in engineering-audit, with CadQuery as the **independent checker**.

Proposed wording for EN-CAD-09 "Done when": *Author with the engineering-audit SOLIDWORKS-COM
route where a host is available; use CadQuery as the independent oracle and STEP round-trip
checker in every case; Onshape only for fixtures the owner models interactively. Host availability
is checked at execution time and recorded per run; no host, no authoring claim.* Statuses stay
`deferred`; the geometry-verification contract in §5 becomes part of EN-CAD-01/03/04 acceptance.
This amendment is retired with the old work queue. A future tooling decision remains owner-held.

## 7. Dimensionless extension contract (W2)

Groups the lumped model lacks or approximates. Each traces to a mechanism and a planned input; none
is introduced to improve a fit. `[m]` = measurable before fabrication from the design; `[built]` =
needs the fabricated part; `[field]` = needs the operating condition.

| Group | Definition | Inputs (units) | Pre-fab? | In lumped? | CHT resolves? | Omitted → failure mode | Limiting behaviour |
|---|---|---|---|---|---|---|---|
| Wall Biot | `Bi = h·t/k` | `h` W/m²K [field], `t` m [m], `k` W/mK [m: datasheet range / built: measured] | yes (with `k` range) | **no** — assumes Bi≪1 | yes (solid region) | isothermal wall overstates coupling; printed polymers (Bi 0.1–0.6) predicted too close to ambient | `k→∞` ⇒ Bi→0 ⇒ lumped recovered; `t→0` same |
| Vent Reynolds | `Re_vent = ρ·u_vent·D_h/μ` | `u_vent` m/s [field/CHT], `D_h` m [m], `ρ,μ` [field] | `D_h` yes; `u_vent` **no** — from CHT or a vent anemometer | **no** — replaced by `Pi_delta(U)` | yes (fluid region) | pre-heat closure has no geometry; two shields with the same outside wind but different vents get the same `Pi_delta` | `A_vent→0` ⇒ sealed box; `u_vent` is **not** ambient `U` |
| Vent area ratio | `A_vent/A_surface` | m² [m] | yes | no | yes | vent sizing invisible to the model | 0 ⇒ sealed; Ishizuka's `β²/(1−β)` form for the resistance |
| Internal dissipation | `N_Q = Q/(αφG·A_proj)` (G>0); night-safe absolute term `Q/(h·A_conv·ΔT_sky)` | `Q` W [built: measured at the enclosure], `α,φ,A_proj` [m] | `Q` only if measured on the electronics | yes (both forms, `nondimensional.theta_linear`) | yes (source term) | self-heating attributed to solar; the Couzo +2.6 °C mechanism unexplained | `Q→0` ⇒ pure shield case; `G→0` ⇒ absolute form only |
| Radiation nonlinearity | `tau = ΔT_sky/T_air` (K/K) with `h_r = 4εσT_air³` | `T_air`, `T_sky` K [field], `ε` [m/built] | yes for a design climate | no — linearised | yes (T⁴ radiation) | the >20 °C failure regime (Study A); cross-climate transfer (Study D) | `ΔT_sky→0` ⇒ no sky sink; large `ΔT` ⇒ linear law drifts |
| Buoyancy | `Ra_H = g·β_T·ΔT·H³/(ν·α_t)` (or `Gr`) on the vent-to-source height `H` | `H` m [m], `ΔT` K [CHT], air properties [field] | `H` yes; `ΔT` no | no | yes | natural vs forced regime misassigned at low wind — exactly the passive-shield worst case | `Ra→0` ⇒ conduction only; high `Ra` ⇒ chimney flow (Ishizuka) |

Dimensional check: every group above is dimensionless (`h·t/k` = W/m²K·m/(W/mK); `ρuD/μ` =
kg/m³·m/s·m/(Pa·s); `Q/(W)`; K/K; `g·β_T·ΔT·H³/(ν·α_t)` = m/s²·1/K·K·m³/(m²/s·m²/s)).

**Held-out rule (carries K2):** groups are chosen here, before data. Their coefficients, if any, are
fitted on the pilot's own data and judged only on held-out printed geometries against the Bernard
and Nakamura benchmarks defined in the direction record §10.

## 8. Triggers and what stays blocked

- **Thermal-FEA fallback (mode a):** may start when (i) B1–B4 pass on an installed solver and (ii)
  a geometry JSON with at least `provisional_design` dimensions exists. Toolchain install is
  **not** authorised this week.
- **CHT (mode b):** additionally needs B5 and an owner allocation for the verification budget.
- **CAD authoring:** EN-CAD-02 inventory (owner) → EN-CAD-01 register → EN-CAD-09 tooling with the
  §5 contract; host availability checked at run time, bounded deadlines, artifact inspected — never
  completion inferred from a launch call.
- `EN-S02`, `EN-R03`, `EN-S09B`, `EN-S11` unchanged; all CAD tasks remain `deferred`.

---

## 9. Verification repairs and identifiability (WP3, 2026-09-24)

The §3 hierarchy and §4 benchmarks below §9 stand, **with these corrections**. They came from the
2026-09-24 critique; several are defects in what §3–§4 originally asserted.

### 9.1 Three different things §3 conflated

| Layer | What it establishes | What it cannot |
|---|---|---|
| **Numerical verification** | the equations are solved correctly (mesh, residual, conservation) | that the equations describe this enclosure |
| **Comparison to an empirical correlation** | agreement with a *fitted* published relation within its validity range | correctness — a correlation is not an exact solution |
| **Physical validation** | agreement with measurement | anything, until Study C exists |

**Correction:** B2 (Churchill–Chu) was written as though the correlation were an exact answer with
"10 % (correlation scatter)". It is **not an analytical solution**, and 10 % is a **proposed check
value**, not a universal scatter. Its validity range must be read from the source — which this repo
has **not** done (`churchill1975` is still **full-read pending**). Until it is read, B2 is a
**trend check**, not a tolerance test.

### 9.2 Do not count convection twice

Either **resolve external flow** or **impose an external film coefficient** at a given interface —
**never both at the same surface**. The original §2 listed "wind/convective coefficient **or**
resolved external flow"; the ambiguity is removed here: the choice is per-interface, declared in the
input ledger, and a surface carrying a resolved boundary layer must not also carry an `h`.

### 9.3 Mesh convergence — the stated rule was insufficient

"≥3 levels; sensor ΔT change between the two finest < 0.1 °C" is **not** a bound on mesh error.
Required instead:
- ≥3 meshes with **recorded refinement ratios**, solver tolerance, and the monitored outputs;
- monitor **vent flow, sensor temperature and heat flux** — not sensor ΔT alone;
- **check for non-monotonic convergence**; a small last-step difference with an oscillating
  sequence does not bound anything;
- **time-step sensitivity** for transient runs, and **domain-size sensitivity** for external flow.

### 9.4 Energy-residual normalisation can divide by zero

"Net residual < 1 % of total applied heat" **fails at `G = 0` and `Q = 0`**, and hides imbalance
where large flows nearly cancel. Declare the normalisation explicitly: use a **fixed reference
scale** (e.g. the maximum of |applied heat| and a declared floor based on the radiative exchange
magnitude), and report the **absolute** residual in W alongside the normalised one.

### 9.5 Limiting cases — conditions, not enforced trends

- **"Open vent lowers ΔT" is withdrawn as an unconditional check.** Increased exchange with ambient
  *tends* to reduce the absolute offset **in a specified heat balance**, but an opening can also
  admit radiation, redirect flow, or **warm a cold sensor**. Test it as a **conditional** statement
  with its conditions stated, and record a violation as information rather than a failure.
- **`k → ∞` recovers the lumped model only if nodes, areas, boundary conditions and couplings also
  match.** It does not equate enclosed air with wall temperature. B4 must declare that mapping or it
  is not a valid check.
- A **vent-flow sign check is necessary but not sufficient.** Before the solver's flow capability is
  called verified, add a **quantitative independent flow/heat-transfer benchmark** with traceable
  boundary conditions.

### 9.6 Target leakage — the trap in the W2 group list

`Re_vent` and `Ra` computed from **solved** velocity or temperature fields are **diagnostics or
implicit model variables**, not pre-build inputs. Likewise a **measured** vent velocity from the
target enclosure.

**Rule:** a before-build prediction may use only quantities available *before* that enclosure is
built and measured — design geometry, independently characterised material and electronics
properties, and environmental forcing. If a group needs a solved or measured target quantity, the
**predictive closure that supplies it must be defined, with its own uncertainty**, and that closure
is part of the model being tested. Undisclosed use of a target-derived quantity invalidates the
no-target-calibration contest (A) in the direction record's K2.

### 9.7 Parameter-identification ledger (required before adding groups)

One temperature trace primarily constrains **combinations** — e.g. `alpha·phi·A_proj` and
`h·A_conv` — not their factors. Adding groups without breaking that degeneracy adds unidentifiable
parameters.

| Parameter | Observable that constrains it | Confounded with | How to break it |
|---|---|---|---|
| `alpha·phi·A_proj` | daytime ΔT vs irradiance | `h·A_conv` | shade/unshade at fixed power (**I2**) |
| `h·A_conv` | ΔT vs wind, and decay after a step | `alpha·phi·A_proj` | power step at fixed solar (**I1**) |
| `Q` reaching the sensor | ΔT response to a documented load change | wall/mount conduction path | controlled resistive load at the source location (**I1**) |
| `eps`, `f_sky` | night ΔT and sky condition | each other, and `Q` | independent `eps` measurement + sky/long-wave logging |
| wall `k`, `t` (Biot) | inner vs outer wall ΔT | contact and coating resistance | direct wall-gradient probes (§1 node map) |
| vent effect | ΔT vs inspected open area | material, source location | **I3** at fixed material and source |

**Rule:** characterise properties independently and use power/shade/flow interventions to break
confounding **before** adding a group. A group that no observable can constrain is not a model
input, it is a fitted parameter.

### 9.8 Biot is a screening ratio, not a verdict

`Bi = h·t/k` screens conduction resistance. It is **not** proof of a novel effect, and a low `Bi`
does **not** make separate plates or a sensor-to-wall gap isothermal. State the characteristic
length, the inner and outer film conditions, the radiation contribution, and the **conduction
direction**. Distinguish **through-wall** gradients from **plate-to-plate** and **sensor-to-wall**
gradients — they are different problems. Use the **actual printed wall structure**: coupon infill
values need not describe a thin perimeter-shell wall.

### 9.9 Time response before transient CHT

Specify a **step-response measurement** and a **candidate reduced thermal network** before
committing to full transient CHT. Steady-state comparison requires a **declared quasi-steady
window**; where forcing changes faster than the thermal response, a steady comparison is invalid.
Retain transient records for separate analysis rather than averaging them away.

### 9.10 Solar is directional

Global horizontal irradiance × an arbitrary sun-facing area is **not** a general directional load.
Either declare orientation with direct/diffuse/reflected components, or label the scalar solar term
an **effective empirical input** and carry it as such. Keep **shortwave transmission** separate from
**long-wave re-radiation** so the two are not double-counted — relevant here because printed walls
are **not** optically opaque in the shortwave band (`amendola2021`).

### 9.11 Closures stay bands until identified

Do not replace the current `h` intercept with a literature value and call it validated: check shape,
wind reference height, direction, turbulence and regime first. **Dewpoint alone does not measure
effective sky temperature under cloud** — use measured long-wave where available, or a documented
sky model **with cloud information and explicit uncertainty**. Uncertain closures are carried as
**bands**, notpoint values, until an intervention identifies them.

### 9.12 Acceptance for Study B (replaces the §3 acceptance line)

A **verification matrix** with one row per check giving: expected value or trend, **applicability
conditions**, independent source, tolerance **with its rationale**, and the fail/**unverified**
state. No check passes on a converged residual or an attractive contour plot alone. Any check
lacking an expected value is `accepted: null` (unverified), never a pass.
