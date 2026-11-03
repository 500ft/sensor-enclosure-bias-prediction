# Study A — Nondimensional reduction of the enclosure-bias model (theory, 2026-09-16)

**Status: SIMULATION reduction of the existing lumped model. No physical data.** Every input
inherits the `bounded` / `TODO-from-lab` status of [`thermal_bias.ASSUMPTIONS`](../analysis/thermal_bias.py).
This document derives the dimensionless groups and reports the **approximation accuracy** of the
linearised closed form. **Corrected 2026-09-24:** an earlier version framed this as a "collapse
test" with a "kill criterion" and concluded the collapse was not universal. That was wrong — see
the corrected verdict in §5. The exact nonlinear dimensionless balance holds to solver tolerance.

## 1. Governing balance

The steady lumped balance solved by `thermal_bias.solve_surface_temperature`:

```math
\alpha \phi G A_\text{proj} + Q = h A_\text{conv} (T_s - T_l) + \varepsilon \sigma A_\text{conv} \left[ f \left(T_s^4 - T_\text{sky}^4\right) + (1 - f)\left(T_s^4 - T_l^4\right) \right]
```

with local air $T_l = T_\text{air} + \delta$ (shield plate pre-heat), $h = h_\text{ext} \times$ `conv_boost`,
$f = f_\text{sky}$, and reported bias $\Delta T = T_s - T_\text{air}$.

## 2. Dimensionless groups

Linearise radiation about ambient, $h_r = 4 \varepsilon \sigma T_\text{air}^3$ (5.69 W/m²K at 30 °C, ε 0.90). With
$\theta = \Delta T / \Delta T_\text{sky}$ and $\Delta T_\text{sky} = T_\text{air} - T_\text{sky}$:

| Group | Definition | Meaning | Novelty relevance |
|---|---|---|---|
| $\Pi_G$ | $\alpha \phi G A_\text{proj} / (h A_\text{conv} \Delta T_\text{sky})$ | heating number: absorbed solar vs convective removal | bundles absorptance, shading, irradiance, area ratio, wind (via `h`) |
| $N_Q$ | $Q / (\alpha \phi G A_\text{proj})$ | internal-dissipation ratio: self-heat vs solar load | **the axis shield physics never had** (AQ self-heating) |
| $N_r$ | $h_r / h$ | radiation/convection coupling | governs the radiation-dominated failure regime |
| $f$ | $f_\text{sky}$ | fraction of the element radiating to cold sky | sets night sub-ambient behaviour |
| $\Pi_d$ | $\delta / \Delta T_\text{sky}$ | ventilation/pre-heat number (wind-dependent) | empirical closure; maps to a vent-Reynolds group in Study B |

The balance reduces **exactly (for the linearised model)** to a closed form:

```math
\theta = \frac{\Pi_G (1 + N_Q) - N_r f + \Pi_d \left(1 + N_r (1 - f)\right)}{1 + N_r}
```

Implemented in [`analysis/nondimensional.py`](../analysis/nondimensional.py) (`theta_linear`), written to
stay finite at night (`solar = 0`) by folding `N_Q` back into an absolute internal-load term.

## 3. The Biot gate — why printed AQ enclosures are physically open

The lumped reduction assumes an **isothermal wall**, i.e. $\mathrm{Bi} = h t / k \ll 1$. That holds for metal
meteorological screens; it does **not** hold for low-cost printed polymer enclosures:

| Wall (3 mm) | k [W/mK] | Bi at h=7 | Bi at h=25 | source |
|---|---|---|---|---|
| PLA, printed 100 % infill | 0.182–0.267 | 0.08–0.12 | 0.28–0.41 | measured |
| ABS, printed **through-layer** | 0.1039 | 0.20 | 0.72 | measured |
| ABS, printed in-plane | 0.1664 | 0.13 | 0.45 | measured |
| PETG, printed 100 % infill | 0.290 | 0.07 | 0.26 | measured |
| PLA Aero (foaming filament) | 0.114 | 0.18 | 0.66 | measured |
| PET-G at 25 % infill | 0.057–0.104 | 0.20–0.37 | 0.72–1.32 | measured |
| Aluminium | 205 | ~0 | ~0 | handbook |

### 3.1 Worked calculation — wall Biot screening

*Format: question → inputs (with provenance IDs) → assumptions → model → substitution → result →
unit check → sensitivity → decision → validation. Canonical inputs are defined once in
[`PARAMETER_REGISTER.csv`](PARAMETER_REGISTER.csv); they are referenced here, not redefined.*

**Question.** Is the isothermal-wall assumption underlying the lumped model admissible for a printed
polymer enclosure wall?

**Inputs**

| Symbol | Value | Unit | ID | Provenance / evidence |
|---|---|---|---|---|
| `t` | 3 | mm | — | **provisional** — nominal wall thickness; not measured on our specimens |
| `k` | 0.104–0.290 | W/mK | `P-KWALL` | `measured_result_external` — three labs, ASTM C177 / E1530; **our specimens not measured** |
| `h` | 6.8–25 | W/m²K | `P-HFLOOR`, `P-HSLOPE` | back-solved from the project's own implied range; both inputs **contradicted by source** |

**Assumptions.** One-dimensional conduction through the wall thickness; `h` is the *combined*
external film coefficient; `k` is the **through-layer** value where direction is resolved
(`janek2026`), which is the direction a wall conducts. Anisotropy ratio **1.60**, so an in-plane `k`
would understate `Bi` by up to ~60 %.

**Model.** $\mathrm{Bi} = h t / k$ — the ratio of internal conduction resistance to external film resistance.
$\mathrm{Bi} \ll 1$ is the condition under which a single wall node is defensible. This is a **screening
ratio, not a verdict**: low `Bi` does not make separate plates, or a sensor-to-wall gap, isothermal
(Study B §9.8).

**Substitution.** Worst credible case, through-layer ABS at the high film coefficient:
$\mathrm{Bi} = 25\ \text{W/m}^2\text{K} \times 0.003\ \text{m} \div 0.1039\ \text{W/mK}$

**Result.** $\mathrm{Bi} \approx 0.72$ (worst credible); range across materials and film conditions **0.07 – 0.72**.
Two significant figures — the inputs support no more.

**Unit check.** $(\text{W/m}^2\text{K} \cdot \text{m}) / (\text{W/mK}) = (\text{W/mK})/(\text{W/mK}) = 1$ ✓ dimensionless.

**Sensitivity.** $\mathrm{Bi} \propto h t / k$, so it is linear in each. Infill is the largest lever: `lopes2023`
shows infill *pattern alone* moves effective `k` by **82 %** at fixed density, which would push
`Bi` to ~**1.3** for a genuinely infilled wall. Using the old handbook PLA value (0.13) inflated
`Bi` by **40–105 %** — that error is corrected above.

**Decision.** Treat the single-node lumped model as **provisional, not invalid**: at `Bi ≈ 0.1` a
lumped wall is a reasonable engineering approximation; at `Bi > 1` it is **violated**. Since the
range spans both, the model is retained *with the validity question registered* rather than assumed
either way. This is why the commissioning node-spread test exists (experiment contract §1).

**Validation.** Measure wall thickness and through-thickness `k` on **our** printed specimens, and
measure the inner/outer wall gradient directly (node map `T_w,i` / `T_w,o`). **Status: unverified —
no property of our specimens has been measured.** A caveat none of the cited sources addresses: a
3 mm wall printed with perimeter shells may be near-solid regardless of the infill *setting*, so the
low-infill rows are an **upper bound** on the effect for a real wall.

**Corrected 2026-09-22.** This table previously used *handbook bulk* conductivities (PLA 0.13, ABS
0.17, PETG 0.29). Three independent labs measured **printed** PLA at 0.182–0.267 W/mK
([`baraboi2026`](../literature/REVIEW_2026-09-22.md), `tychaniczkwiecien2025`, `rodriguez2023`), so
k = 0.13 was too low and **inflated Bi by 40–105 %**. The conclusion is unchanged and in fact better
supported, but the mechanism is different: the high-Bi end comes from **through-layer anisotropy**
(`janek2026`: 0.1039 W/mK, anisotropy ratio 1.60), **reduced infill** (`lopes2023`: infill *pattern*
alone moves effective k by 82 % at fixed density) and **foaming filaments** — not from a low bulk
conductivity. Caveat none of these sources addresses: a 3 mm wall printed with perimeter shells may
be near-solid regardless of the infill setting, so the low-infill rows are an upper bound on the
effect for a real wall.

Measured `Bi ~ 0.07–0.72` (up to ~1.3 if genuinely infilled) means wall conduction is a **first-order effect** the classical (metal, `Bi≈0`)
shield literature structurally omits. This is a physically-grounded open axis independent of the
literature scan, and it is where Study B's CHT check earns its keep (resolving the wall/air field
the lumped model cannot).

## 4. Collapse test — preregistration

- **DOE:** full-factorial daytime sweep over `alpha, phi(solar_factor), A_proj, A_conv, Q, G, wind,
  f_sky` across the bounded ranges in `nondimensional.DOE_AXES` (1944 points). Night is reported
  separately (small, radiation-dominated).
- **Law under test:** the closed form of §2 (parameter-free theory), residual reported as both
  absolute °C and relative.
- **Acceptance (predictive claim holds):** p95 **relative** residual ≤ ~3% (the model's own
  daytime linearisation uncertainty) across the DOE.
- **Kill criterion (verbatim from the plan):** scatter about the law larger than the model's own
  uncertainty ⇒ **there is no law; the project stays a ranking study.**

## 5. Result — the linearised approximation is bounded; the exact balance holds

`python -m analysis.nondimensional`:

| Regime | N | abs median | abs p95 | rel median | rel p95 |
|---|---:|---:|---:|---:|---:|
| all daytime | 1944 | 0.23 °C | 2.0 °C | 3.6% | **63.9%** |
| bias > 1 °C | 1656 | 0.23 °C | 2.3 °C | 2.6% | 24.0% |
| bias > 3 °C | 1076 | 0.21 °C | 4.0 °C | 2.1% | 12.3% |
| solar-driven θ>0.3 | 723 | 0.27 °C | 6.3 °C | 2.4% | 11.9% |

Overall `R² = 0.972`.

> ### Corrected verdict (2026-09-24)
>
> **The earlier verdict — "the kill criterion is tripped, there is no universal clean law" — was
> wrong, and is withdrawn.** That comparison was between a *linearised* closed form and the
> *nonlinear* solver **derived from the same heat balance**. It therefore measures **approximation
> error**, not the validity of a dimensionless representation.
>
> The **exact nonlinear dimensionless balance**
>
> ```math
> \Pi_G + \Pi_Q = \theta - d + \frac{N_r}{4\tau} \left\{ f \left[(1 + \tau\theta)^4 - (1 - \tau)^4\right] + (1 - f)\left[(1 + \tau\theta)^4 - (1 + \tau d)^4\right] \right\}
> ```
>
> was derived and evaluated at **all 1,944 DOE points**: maximum absolute residual **5.478e-9**,
> i.e. solver tolerance (`nondimensional.balance_residual`; regression test
> `ExactBalanceTests`). **Dimensionless similarity is not falsified by anything in this module.**
>
> Correct statement: *the linearised closed form exceeds the selected approximation-error threshold
> in parts of the illustrative DOE; the exact nonlinear dimensionless balance remains consistent
> with the original model. Physical accuracy and cross-design transfer are untested.*
>
> Three further corrections: the 3 % **relative** band is a **selected approximation threshold**, not
> a measured model uncertainty or a scientific kill criterion; **absolute °C** is the primary metric
> because relative error is ill-conditioned near zero bias; and the regime bins are **output-based
> diagnostics of a known solver**, not a prospective field rule. The DOE/threshold exercise is
> labelled **exploratory** — no dated pre-run record supports calling it preregistered.

What the approximation results *do* show:

- **Median collapse is tight** (~2–4% relative, ~0.23 °C absolute) — the solar-driven regime is
  well-predicted by the five groups.
- **The tail behaviour is an approximation limit, not a similarity failure:** it concentrates at (a) the `theta ≈ 0` crossing,
  where relative error is meaningless (absolute error stays bounded, p95 ≤ ~5 °C), and (b) large
  `dT` where radiation nonlinearity (dropped by the linearisation) grows.

This matches the repo's own [matched-control sensitivity screen](../analysis/thermal_bias_results.md)
(A3): the enclosure advantage is not robust to combined assumptions, so a *universal* collapse was
never likely. The honest scientific contribution is therefore **the collapse domain and its
boundary**, not a claim that bias always collapses.

**Per-regime diagnostic (added 2026-09-21, W3):** `python -m analysis.nondimensional` now bins the
DOE by mechanism (`nondimensional.regime`) and `--out` writes the groups, absolute/relative
residuals and regime per point. Solar-driven: 0.10 / 0.46 °C (med / p95 abs); high-nonlinearity
(ΔT>20 °C): 1.9 / 14.2 °C — the law's failure domain. See
[research-direction-2026-09-21.md](research-direction-2026-09-21.md) §3.

**Extension (2026-09-23, Study B design):** the groups this reduction lacks — wall Biot, vent
Reynolds, vent area ratio, radiation nonlinearity, Rayleigh — are specified with inputs, limits and
failure modes in [specs/study-b-cht/design.md](specs/study-b-cht/design.md) §7.

## 6. Honest limits

- **Radiation nonlinearity** — the linearised law is the reduction hypothesis; ground truth is the
  full nonlinear solver. At fixed climate ($\tau = \Delta T_\text{sky} / T_\text{air} \approx 0.066$) the collapse is onto the 5
  groups; **varying `T_air` across climates (Study D) adds a sixth radiation-nonlinearity group.**
- **`Pi_d` is an empirical closure**, not first-principles ventilation physics; Study B replaces it
  with a resolved vent-Reynolds treatment via CHT.
- **`Bi << 1` is assumed** by the whole reduction and is violated for printed polymers — a modelled
  bias the lumped model cannot self-diagnose.
- These are model outputs under the stated assumptions, **not measurements**. Same status as every
  number in `thermal_bias_results.md`: SIMULATION / pending lab data.
