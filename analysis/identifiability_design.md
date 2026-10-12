# Synthetic I1 design study

## Structural result before simulation

In dark, fixed-airflow conditions, let `C dT/dt = eta P - G (T-Ta)`.
`C` is heat capacity [J/K], `G` is effective conductance [W/K], `eta` is
electrical-to-modeled-node heat coupling [dimensionless], and `P` is measured
electrical input [W]. Dividing by `G` gives
`tau dT/dt = beta P - (T-Ta)`, with `tau=C/G` [s] and `beta=eta/G` [K/W].
Multiplying `(C,G,eta)` by the same positive factor leaves every trajectory
unchanged, for any power waveform and the same initial and ambient temperatures.
The physical coupling bound restricts that family but does not select a member.
Power changes alone cannot identify the three original parameters.

An independently measured coupling gives `G=eta/beta` and `C=tau*eta/beta`.
Alternatively, independently known effective `C` or `G` fixes the scale under
this single-node model. Electrical V/I alone measures `P`, not `eta P`.
Calorimetry or a calibrated heat injection with demonstrated node coupling
could supply that missing input. A material heat-capacity lookup is insufficient
if participating mass or the single-node approximation is unknown. Extra
thermometers help only with a justified heat-path model and independent inputs.

## Registered development calculation

[The machine-readable registration](input/identifiability_design.json) is the
single source for assumed domains, seeds, counts, schedules, likelihood and
stopping rules. It is committed before the first synthetic result. Its values
are chosen to span short and long observations relative to assumed thermal
response times, not inferred from a rig or selected to achieve a desired result.
No source-backed instrument specification is assigned to unknown hardware.

Compare an isolated on/off block with repeated steps at equal total duration,
amplitude and integrated energy. The fitter knows the recorded ambient ramp;
an unobserved smooth ambient excursion tests ambient-record mismatch. A second
misspecification case adds probe lag: a negligible-loading sensor follows the
heated node through another first-order time constant. This is a plausible
separate probe/mount thermal storage mechanism, not an identified enclosure.
Both temperatures start at the same sampled initial offset. Its heater time
constant is recorded for reference; fitting one time constant cannot recover
the full two-state structure.

The generator uses exact state recurrences with piecewise constant power and
ambient slope; the fit uses independent closed-form sums of power steps.
An independent RK4 calculation and interval energy balance check the generator
before Monte Carlo. Measurements contain stationary correlated noise, a random
constant calibration offset and quantization. The fit also profiles an unknown
initial temperature and residual linear drift. Correlation is known only in
these scenarios; estimated covariance would add uncertainty in real use.

Profile likelihood uses Gaussian AR(1) whitening and variable projection of
linear gain and nuisance coefficients at each candidate time constant. The
registered likelihood-ratio cutoff is the asymptotic chi-square reference for
a marginal parameter ([NIST table](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3674.htm)).
Quantization and the alternate structures violate parts of that likelihood;
simulation checks coverage rather than calling the sets calibrated intervals.
Search-edge sets are explicitly open within the registered domain. Disconnected
sets must be retained rather than collapsed into an apparently precise interval.
Multiple starts and a refined profile grid check numerical search sensitivity.
The implemented grid also includes the generating time constant. This is a
synthetic benchmarking convenience and must not be mistaken for an available
input when fitting physical data.

This is an estimation-only design aid. Physical M1/M2, real I1 and held-out-design
transfer remain pending. Any useful schedule depends on actual response times,
measurement uncertainty, heat paths and fixed-airflow feasibility.
