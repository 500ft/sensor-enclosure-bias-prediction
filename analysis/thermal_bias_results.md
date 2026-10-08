# Thermal self-heating bias: analytical baseline results

**SIMULATION OUTPUT -- pending lab and co-location data. Not a measurement, not a
certified or regulatory-grade result.** Every value below is a first-order
analytical prediction produced by `analysis/thermal_bias.py`. This lumped
steady-state result is retained as an analytical baseline for the comparisons
in [the roadmap](../ROADMAP.md). Geometry/input definitions are in the
[geometry reference](../docs/cad_geometry_reference.md); higher-fidelity
modeling is conditional on a separately justified question.

Regenerate with:

```bash
python3 analysis/thermal_bias.py
# figure -> analysis/figures/thermal_bias.png
```

## 1. What this models and why FEA is not needed for it

The paper's central enclosure error mechanism is **radiative self-heating**:
under solar load the enclosure/shield surface runs hot, the air the sensor sees
runs hot, and temperature / relative-humidity (and gas) readings are biased high
in temperature and low in RH. This mechanism is *first order* and does **not**
require FEA to bound. For each variant we solve the steady-state lumped energy
balance on the sensor-coupled surface:

```
alpha * solar_factor * G * A_proj  +  Q_internal
    =  h_eff * A_conv * (T_s - T_local)
       +  eps * sigma * A_conv * [ f_sky*(T_s^4 - T_sky^4) + (1-f_sky)*(T_s^4 - T_local^4) ]
```

and report the sensor temperature rise above **true** ambient, `dT = T_s - T_air`,
then map `dT` to the reported RH error (warm air at fixed water-vapor content
reads low RH). The former FEA stub performed no solve and has been removed.
These outputs compare assumptions in the lumped model; the combined sensitivity
screen below limits any design preference.

## 2. Bias-vs-variant table (analytical system comparison)

The painted baseline in Section 4 is a primary control, not an optional
footnote: at 1000 W/m² and 0.5 m/s the predicted rises are 19.4°C dark box,
4.5°C painted box, and 3.0°C shield. The incremental system advantage relative
to the painted box is approximately 1.5°C. Differences in coupled heat load,
geometry, and convection prevent attributing this entire difference to shielding.

The painted control is now a first-class `V0P` variant in the default CSV and
figure, not just the single-point sensitivity calculation. It is copied from
`V0` with only absorptance changed from 0.90 to 0.30. Equal emissivity is a
modeling assumption, not a measured property of a paint or filament. The main
[CSV](output/thermal_bias_table.csv) contains all four variants at every reported
operating point; the existing V0/V1/V2 values are unchanged.

| G [W/m²] | wind [m/s] | V0P dT [°C] | V0P RH error [%RH] | V0P minus V1 dT [°C] |
|---:|---:|---:|---:|---:|
| 800 | 0.0 | 3.4679 | -8.9307 | 0.5156 |
| 800 | 0.5 | 2.9290 | -7.6692 | 0.5265 |
| 800 | 1.0 | 2.5343 | -6.7176 | 0.5353 |
| 800 | 2.0 | 1.9955 | -5.3794 | 0.5425 |
| 800 | 5.0 | 1.2175 | -3.3637 | 0.4899 |
| 1000 | 0.0 | 5.2965 | -12.9049 | 1.6087 |
| 1000 | 0.5 | 4.4796 | -11.1857 | 1.4771 |
| 1000 | 1.0 | 3.8793 | -9.8651 | 1.3803 |
| 1000 | 2.0 | 3.0576 | -7.9743 | 1.2405 |
| 1000 | 5.0 | 1.8674 | -5.0543 | 0.9571 |

The last column is the difference of the exported rounded predictions. It is
neither measured shielding benefit nor an uncertainty bound. The small
800 W/m² differences also show why the dark-box comparison alone overstates the
incremental design case. Physical matched-finish comparisons, geometry inventory
and joint-uncertainty evaluation remain required before a validation verdict.

Ambient case: `T_air = 30 degC`, `RH_true = 50 %`, clear-sky `T_sky = 10 degC`
(20 K depression). `dT` in degC (sensor rise above true ambient); `RH_err` in
%RH (reported minus true; **negative = reads dry**).

| G [W/m^2] | wind [m/s] | V0 dT | V0 RH_err | V1 dT | V1 RH_err | V2 dT | V2 RH_err |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 800  | 0.0 | 17.6 | -30.7 | 3.0 | -7.7 | 1.1 | -3.0 |
| 800  | 0.5 | 15.0 | -28.0 | 2.4 | -6.4 | 1.1 | -3.0 |
| 800  | 1.0 | 13.1 | -25.6 | 2.0 | -5.4 | 1.1 | -3.0 |
| 800  | 2.0 | 10.4 | -21.9 | 1.5 | -4.0 | 1.1 | -3.0 |
| 800  | 5.0 |  6.4 | -15.1 | 0.7 | -2.0 | 1.1 | -3.0 |
| 1000 | 0.0 | 22.7 | -35.0 | 3.7 | -9.4 | 1.3 | -3.7 |
| 1000 | 0.5 | 19.4 | -32.4 | 3.0 | -7.8 | 1.3 | -3.7 |
| 1000 | 1.0 | 17.0 | -30.0 | 2.5 | -6.6 | 1.3 | -3.7 |
| 1000 | 2.0 | 13.5 | -26.1 | 1.8 | -4.9 | 1.3 | -3.7 |
| 1000 | 5.0 |  8.3 | -18.6 | 0.9 | -2.5 | 1.3 | -3.7 |

**Range across wind 0-5 m/s at G = 1000 W/m^2 (worst-case solar):**

| Variant | dT calm -> windy [degC] | RH_err [%RH] | Dominant contributor |
|---|---|---|---|
| V0 Baseline closed box | **22.7 -> 8.3** | -35.0 -> -18.6 | Solar on dark wall + self-heating; ventilation-limited |
| V1 Passive multi-plate shield | **3.7 -> 0.9** | -9.4 -> -2.5 | Residual plate-to-air pre-heat; flushes with wind |
| V2 Actively aspirated reference | **~1.3 (flat)** | ~-3.7 | Forced convection dominates; wind-independent |

**Bracketing against measured values in the source literature** (predictions vs.
published *measurements*; all model values remain predictions):

| Prediction | Measured bracket | Sources |
|---|---|---|
| V1 passive multi-plate, dT 0.9-3.7 degC | Good stacked-plate passive shields measure dT -0.7 to +2.2 degC full-sun (89% of daytime readings <= 1.5 degC); poorer passive geometries reach +5.4 degC (cones) and +7.4 degC (open-bottom tubes). A $3 Gill-style shield showed MAE 0.99 degC vs. a mechanically aspirated reference in the open, warm-biased at low wind. 3D-printed cone shields measured max daytime errors 0.3-1.5 degC vs. a Vantage Pro. | Tarara & Hoheisel 2007; Holden et al. 2013; Botero-Valencia et al. 2022 |
| V2 aspirated, ~1.3 degC flat | Measured aspirated shields average < +/-0.5 degC vs. a passive Gill reference — the V2 prediction is conservative (high) by ~2x. | Tarara & Hoheisel 2007 |
| Wind dependence (both V0/V1 fall steeply with wind) | Passive multi-plate 3D-PAWS temperature RMSE fell 1.22 -> 1.08 degC above 1 m/s wind and approached the 0.8 degC sensor floor above ~5 m/s vs. an actively aspirated Mesonet reference. | Theisen et al. 2020 |
| V0 closed box, dT 8.3-22.7 degC | **Not directly bracketed.** The source set contains no measured sealed-dark-box-in-sun bias; the nearest measured anchors are the worst passive geometry (+7.4 degC) and a fully exposed sensor (max +4.1 to +6.0 degC daytime). V0 exceeding all of these is *expected* (closed dark enclosure + internal dissipation, no ventilation) but is a model claim only until the solar-heat-soak test (Section 7) measures it. | Tarara & Hoheisel 2007; Botero-Valencia et al. 2022 |

Note the V1 and V2 curves cross near ~3 m/s: a well-ventilated passive shield can
match or beat forced aspiration once natural convection is strong, which is exactly
the literature finding that aspiration helps **mainly at low wind** (Theisen et al.;
Deford et al.).

Figure: `analysis/figures/thermal_bias.png` (left: dT vs wind; right: RH_err vs
wind; solid = 1000 W/m^2, dashed = 800 W/m^2; V0P is the painted control).
Marker shapes distinguish variants on the 1000 W/m² curves as well as color.

## 3. Assumptions block (every input, with status)

Status: `bounded` = bounded engineering assumption to be measured/refined;
`geometry/TODO-from-lab` = placeholder pending `templates/baseline_system_description.md`;
`physics` = standard correlation/constant; `swept` = varied in the sweep.

| Input | Value | Units | Status |
|---|---|---|---|
| Clear-sky solar G | 800-1000 | W/m^2 | swept |
| Ambient air T_air | 30 | degC | bounded |
| True ambient RH | 50 | % | bounded |
| Clear-sky depression (T_air - T_sky) | 20 | K | bounded |
| alpha, baseline box surface (dark) | 0.90 | - | bounded |
| alpha, light/white shield surface | 0.30 | - | bounded |
| Long-wave emissivity eps | 0.90 | - | bounded |
| f_sky, baseline (area seeing cold sky) | 0.50 | - | bounded |
| f_sky, shield (sensor sees cold sky) | 0.05 | - | bounded |
| A_proj baseline / shield | 0.030 / 0.012 | m^2 | geometry/TODO-from-lab |
| A_conv baseline / shield element | 0.090 / 0.020 | m^2 | geometry/TODO-from-lab |
| shield_solar_factor (flux reaching sensor) | 0.18 | - | bounded |
| Internal self-heat: single-zone / two-zone | 0.8 / 0.1 | W | bounded/TODO-from-lab |
| h_ext = 5.0 + 4.0*wind | -- | W/m^2K | physics |
| shield natural-convection boost | 1.4 | - | bounded |
| shield air pre-heat (calm) | 1.2 | K | bounded |
| pre-heat wind half-life | 1.5 | m/s | bounded |
| h_fan (V2 forced convection) | 25 | W/m^2K | bounded |

Optical properties (alpha, eps) are color/finish dependent and are **not** on
filament datasheets; they are model inputs to be measured or bounded, not
assumed (consistent with `paper/manuscript_v1.md` 2.3 and the CAD/FEA plan).

## 4. Sensitivity (which uncertain input dominates)

One-at-a-time perturbations at G = 1000 W/m^2, wind = 0.5 m/s (`dT` in degC):

| Perturbation | V0 dT | V1 dT |
|---|---:|---:|
| baseline | 19.4 | 3.0 |
| V0 surface painted white (alpha 0.90 -> 0.30) | **4.5** | - |
| V0 internal load doubled (0.8 -> 1.6 W) | 20.1 | - |
| V0 low emissivity (0.90 -> 0.50) | **26.4** | - |
| V1 shading worse (solar_factor 0.18 -> 0.30) | - | 4.4 |
| V1 no convection boost (1.4 -> 1.0) | - | 3.4 |
| V1 plate air pre-heat doubled (1.2 -> 2.4 K calm) | - | 3.9 |

Takeaways: V0 bias is driven hardest by **surface optical properties** -- solar
absorptance and IR emissivity -- not by internal load. Painting the baseline
white (alpha 0.90 -> 0.30) alone cuts V0 from ~19 to ~4.5 degC. The listed
one-at-a-time shield perturbations move V1 by at most ~1.5 degC. That is
comparable to the incremental advantage over the painted control; it does not
establish robustness to joint uncertainty or measured manufacturing variation.

## 5. RH-error mapping

The reported RH is computed by holding the **absolute** water-vapor content at
the ambient partial pressure and raising the sensor temperature to `T_s`; RH is
then the fixed actual vapor pressure over the saturation pressure at the warmer
sensor temperature (Magnus/Tetens `e_s`). A warm sensor therefore reports a
**low** RH. This converts each thermal `dT` into the measurable RH bias the paper
cares about (table 2): e.g. V0's ~19 degC rise reads about **-32 %RH**, while
V1's ~3 degC rise reads about **-8 %RH** at low wind.

## 6. Use of the comparison

The tables above compare assumed systems. Their geometry, heat coupling and
ventilation change together. The painted-control and combined-sensitivity
results qualify the earlier design recommendations: no design preference is
established by this comparison. Surface properties, independent airflow and
sensor-coupled heat remain measurement inputs for the current research question.
The aspirated model is a numerical comparator, not a calibrated instrument.

## 7. Validation dependency

The [roadmap](../ROADMAP.md) requires qualified measurements and identifiability
before field comparisons. Predictions for the actual specimens must use the
registered inputs, model and processing; comparison with a calibrated reference
then estimates error and uncertainty. The earlier ruggedization/FEA proposal is
not a prerequisite. Gas cross-sensitivity remains outside this thermal comparison.

---

*This lumped analytical result remains reproducible. The retired FEA proposal
supplied no additional result. All numbers are SIMULATION, pending lab data.*

## Night clear-sky case (EN-D02, 2026-09-09) — a conditional sign reversal

Everything above is a daytime slice. The same energy balance, with the same clear-sky
depression and **no solar load**, predicts the opposite error: long-wave loss to the cold sky
dominates and a sky-exposed enclosure reads *below* ambient. From
[`analysis/output/thermal_bias_night_table.csv`](output/thermal_bias_night_table.csv), regenerated
by `python analysis/thermal_bias.py` (assumptions unchanged; G = 0 W/m²):

| variant | ΔT, calm | ΔT, 5 m/s | RH error, calm |
| --- | ---: | ---: | ---: |
| V0 baseline closed box | -4.03 °C | -1.39 °C | +13.2 %RH |
| V1 passive multi-plate shield | -0.012 °C | — | +0.03 %RH |
| V2 aspirated reference | -0.005 °C | — | +0.01 %RH |

Against the daytime V0 warm bias of +22.7 °C at 1000 W/m² and calm, these two
steady-state scenarios exhibit opposite signs. They motivate sampling both day
and night during co-location, including at least a full diurnal cycle; they do
not simulate a 24 h transient or establish that one day validates the design.
Cloud cover, wind and sky temperature need coverage beyond a single nominal
case. V1's smaller modeled night bias is a **whole-system comparison**: sky
view, geometry, internal load and convection all differ from V0. It cannot
isolate the effect of blocking sky view. The painted control V0P is identical
to V0 at night because its only changed parameter, solar absorptance, multiplies
the zero solar load; no claim is made that real paint leaves emissivity unchanged.

Same status as every other number here: **SIMULATION / pending lab data.** Sign and ordering are
asserted by [tests](tests/test_thermal_bias.py) (`NightClearSkyTests`); magnitudes are model outputs
under the stated assumptions, not measurements. Sky-temperature depression can
change **both magnitude and sign**: with the same 30 °C air and 0.8 W V0 load,
changing only sky temperature from 10 to 29 °C changes calm-night ΔT from
−4.028 to +0.566 °C in the existing solver. This is a sensitivity counterexample,
not a measured clear-sky condition. At G = 0 and ambient surface temperature,
cold bias occurs only when sky-directed radiative loss exceeds internal heating.
The assumed shield plates/surroundings remain at local air temperature; their
own nighttime radiative cooling is not independently solved. The small V1/V2
predictions therefore need particular caution before a physical shield claim.

## Matched-control sensitivity screen (A3, 2026-09-16) — the nominal advantage is not robust to combined assumptions

The one-at-a-time [sensitivity block](#4-sensitivity-which-uncertain-input-dominates) shows which
single assumption moves V1's bias most; it does **not** establish robustness when several move
together. [`analysis/matched_control_sensitivity.py`](matched_control_sensitivity.py) runs a finite
screen — 8 V1 assumption combinations (`solar_factor` ∈ {0.18, 0.30}, `conv_boost` ∈ {1.4, 1.0},
calm plate pre-heat ∈ {1.2, 2.4 K}, the repository's own illustrated values) across 3 operating
cases (day G=1000/wind 0.5, nominal night G=0/sky 10 °C, warm-sky night G=0/sky 29 °C, all at
air 30 °C) — on the **existing** solver, and reports the paired absolute-bias advantage of V1 over
the identical-geometry painted control V0P (`|bias_V0P| − |bias_V1|`; positive means V1 is closer
to true ambient).

In the day case the nominal advantage is **+1.4771 °C** (V0P +4.4796, V1 +3.0025). Combining all
three illustrated V1 perturbations reverses it to **−1.5531 °C** (V1 +6.0327): the shield is now
*further* from ambient than the painted box. At G=0 the solar-absorptance and plate-pre-heat terms
vanish, so night V1 bias depends only on convection, not on `solar_factor` or pre-heat; the two
night cases duplicate predictions by design and are controls, not independent evidence.

This is an **illustrative** screen: the perturbation values are figures already in the repository,
combined to expose a planning consequence, not measured bounds or a probability distribution. It
supplies no confidence interval, joint-uncertainty bound, probability of superiority, or
as-built model-agreement tolerance. Its output is a list of the assumptions (shield shading,
convection boost, plate-to-air pre-heat) that must be **measured or more tightly justified** before
any hardware preference — not a go/no-go on the shield. Reproduce with
`python -m analysis.matched_control_sensitivity --out <fresh-path>.csv`. Same status as every other
number here: **SIMULATION / pending lab data.**
