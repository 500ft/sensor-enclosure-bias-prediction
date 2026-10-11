# Jin et al. (2026, Sensors): CFD-trained radiation-error correction

Source: Wei Jin, Qingquan Liu, Wei Dai, Xin Hong, Xilong Cao and Haiwen Sun,
*Optimized Design and Radiation Error Correction of a Naturally Ventilated Air
Temperature Sensor for Atmospheric Environmental Monitoring*, Sensors 26(12),
3853. [DOI](https://doi.org/10.3390/s26123853) ·
[full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/).
This is `jin2026sensors`, distinct from `jin2026` (Atmosphere, shield design).

Full-text assessment replaces the abstract-only entry. Sections 1–6, tables,
figure captions and the data statement were read; Figures 1, 2, 9 and 10 were
also inspected as images. Numerical facts from this paper live here. These are
reported results, without an independent reproduction of the authors' data or code.

## Geometry and CFD domain

[Section 2.1 and Figure 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sec2dot1-sensors-26-03853)
describe a thin-film Pt100 in an 8 mm copper sphere, white-coated plastic guide
plates and upper/lower aluminum shields with silver outer and black inner
surfaces. The structural screen selects 24 mm plate spacing and 45° inclination
under the nominal conditions, rather than a globally optimized design
(Sections 3.1–3.3). These dimensions belong to their device, not this project's rig.

[Section 2.2 and Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sec2dot2-sensors-26-03853)
use a fluid/solid domain labeled 2000 × 2000 × 1300 mm, velocity inlet,
pressure outlet, remaining exterior no-slip walls and coupled solid/air
interfaces. Table 1 supplies material properties; Table 2 reports a mesh screen
using probe temperature. Section 3.1 specifies FLUENT, standard k–ε, wall
functions, SIMPLE and solar ray tracing, at a nominal ambient temperature of
300 K. Rounded probe-temperature stability does not establish domain-size or
model-form independence.

## Actual training data and refitting

[Sections 4.1–4.3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sec4-sensors-26-03853)
construct 784 CFD samples for the optimized structure. The approximate
training/validation/test split is 70/15/15%; exact split counts and the sampling
recipe across environmental combinations are not specified. Geometry and
material are fixed in these samples, not features supplied to a cross-design model.

The inputs are solar, long-wave and scattered radiation, air density,
wind speed, solar elevation and albedo; the target is CFD probe radiation error.
[Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sensors-26-03853-t003)
reports these investigated environmental ranges. It does not specify the joint
coverage of the training split.

| Input | Reported range | Unit |
| --- | ---: | --- |
| Solar radiation P1 | 50–1200 | W/m² |
| Long-wave radiation P2 | 50–500 | W/m² |
| Scattered radiation P3 | 50–300 | W/m² |
| Air density ρ | 0.7361–1.225 | kg/m³ |
| Wind speed V | 0.5–8 | m/s |
| Solar elevation E | 10–90 | degrees |
| Surface albedo f | 0.1–0.9 | dimensionless |

The MLP has a 7–16–12–1 topology. Inputs and output are standardized with
training-set statistics; predictions are inverse-transformed. Adam/MSE training
uses learning rate 0.001, batch size 8, maximum 1000 epochs and validation-loss
early stopping with patience 30, restoring the best weights. The stated random
seed is 0. MLR, SVR and MLP share the CFD split; the authors select MLP using the
CFD test comparison. That comparison therefore participates in model selection.

Section 5.3 explicitly excludes the field dataset from training, validation and
testing of the fitted model; here “testing” refers to the internal CFD split.
It reports applying the trained MLP outdoors without field refitting. The Pt100
was nevertheless calibrated before deployment (Section 5.1). No withheld-design
experiment, cross-geometry refitting requirement or proof of zero calibration
is reported. Absence of field refitting is not absence of instrument calibration.

## CFD interpolation and field errors

[Table 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sensors-26-03853-t004)
compares predictions with CFD labels on the internal test split:

| Model | RMSE [°C] | MAE [°C] | Correlation r |
| --- | ---: | ---: | ---: |
| MLR | 0.0319 | 0.0220 | 0.7304 |
| SVR | 0.0098 | 0.0044 | 0.9798 |
| MLP | 0.0032 | 0.0020 | 0.9979 |

[Sections 5.1–5.3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sec5-sensors-26-03853)
compare the proposed sensor with a nearby MET ONE 076B aspirated-shield reference
at Nanjing Meteorological Observatory. A common acquisition system records the
probe, CMP-21 pyranometer and 03002V anemometer. The text describes a three-day
campaign at 10-minute intervals. Figures 9 and 10 use sample-number axes ending
at 192, with no timestamps or exclusion rule reconciling the plotted support to
the stated duration. This leaves complete day/night coverage and the exact
field sample count unverified; repeated records are not independent units.

Field prediction also requires calculated solar elevation and ground long-wave
radiation, empirically estimated scattered radiation, and fixed site assumptions
for air density and albedo (Section 5.2). The scattered-radiation estimation
recipe and ground-temperature measurement method are not detailed enough here
to reconstruct all inputs. The reference sensor's calibration uncertainty is
not supplied. This is a test of the proposed geometry at one site, not a design
withheld from CFD/model development.

[Table 5](https://pmc.ncbi.nlm.nih.gov/articles/PMC13306756/#sensors-26-03853-t005)
uses the same field dataset for the before/after comparison. Errors are relative
to the aspirated reference, not known free-air truth. Section 5.3 reports a
predicted-versus-observed radiation-error correlation of 0.92.

| Field error metric | Before correction [°C] | After correction [°C] |
| --- | ---: | ---: |
| Mean bias | 0.104 | 0.041 |
| RMSE | 0.127 | 0.052 |
| MAE | 0.104 | 0.042 |
| Maximum absolute error | 0.425 | 0.171 |
| 95th percentile absolute error | 0.248 | 0.067 |

## Uncertainty, effort and limits

Section 5.3 acknowledges uncertainty from the empirical radiation estimate and
fixed environmental inputs. It does not supply a propagated uncertainty budget,
confidence intervals for the reported errors, or reference/replicate uncertainty.
The percentile in Table 5 is an empirical absolute-error percentile, not a
confidence limit. Self-heating, support/lead conduction and humidity effects
were not independently quantified. Section 6 leaves response time, long-term
operation and wider environmental generalization for later work.

The study uses detailed CFD, probe calibration, a reference comparison and
auxiliary measurements/estimates. It does not compare their total acquisition,
modeling and deployment effort against alternative co-location budgets. The
Data Availability Statement offers data on request; the full text does not
provide the dataset, fitted weights or split indices for reproduction. No data
request was sent as part of this review.

## Effect on this project's claim

| Claim | Support and gap | Assessment |
| --- | --- | --- |
| Physics-derived correction can be evaluated outdoors without fitting to the field outcomes | Sections 4 and 5 explicitly separate CFD training from field evaluation, for the proposed geometry | Directly relevant prior; reported single-site experiment (grade B with the above qualification limits) |
| A new enclosure geometry can avoid target-design fitting | Geometry/material are fixed during correction training; no held-out design is evaluated | Not established by this paper; also not disproved |
| Physics saves total measurement/calibration effort at comparable error | No comparison across calibration budgets or total effort accounting | Remains an evaluation question, not an established saving or a global novelty claim |

The earlier statement that physics-based prediction is generally “established”
was too broad. The supported result is a geometry-specific CFD-trained surrogate
with an independent outdoor comparison as reported by the authors. A generic
physics-before-field-fit claim is insufficient novelty. The adopted
[roadmap](../ROADMAP.md) instead asks about held-out designs and total effort.
This paper does not determine that comparison's likely winner or justify
requiring all corrections to refit on field data. An independent held-out-design
and effort study would change that assessment.

Source inspected on 2026-10-11 via PMC HTML (CC BY 4.0); DOI and six-author identity
match the existing bibliography. Retrieved HTML SHA-256:
`18b73c10c51c7730804f0f0640c7f9fd90c84acf6bfdbf9c76cd9d0be3f319df`.

[Earlier abstract-only assessment](https://github.com/500ft/sensor-enclosure-bias-prediction/blob/0546497bea250dec203aa4dc1a3f6a59f2dfb7d5/ProConsList/jin2026sensors.md) is preserved for review history.
