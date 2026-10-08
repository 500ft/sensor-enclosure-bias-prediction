#!/usr/bin/env python3
"""Lumped steady-state radiative self-heating bias model for the sensor-box variants.

SIMULATION OUTPUT -- NOT A MEASUREMENT. Every number this script prints is a
first-order analytical prediction, pending lab and co-location data. It is the
analytical baseline retained for the calibration/effort comparison in ROADMAP.md.
Geometry inputs are described in ``docs/cad_geometry_reference.md``. It does not claim
regulatory-grade or certified performance (see ``README.md`` honesty constraints).

WHAT IT COMPUTES
----------------
The paper's central enclosure error mechanism is radiative self-heating: under a
solar load the enclosure/shield surface runs hot, the air the sensor sees runs
hot, and the temperature/relative-humidity (and gas) readings are biased. This
mechanism is *first order* and does not require FEA to bound: a lumped
steady-state energy balance on the sensor-coupled surface gives a defensible
delta-T-vs-variant estimate now.

For each variant we solve, per (wind speed, solar flux) operating point, the
steady-state surface/sensor temperature ``T_s`` from the energy balance

    Q_solar = Q_conv + Q_rad

        alpha * G * A_proj  +  Q_internal
            = h * A_conv * (T_s - T_air)
              + eps * sigma * A_rad * (T_s^4 - T_sky^4)

and report the sensor temperature rise above true ambient, ``dT = T_s - T_air``.
That delta-T is then mapped to the relative-humidity error the sensor would
report (warm air at fixed water-vapor content reads low RH).

VARIANTS (see ``docs/cad_geometry_reference.md``)
--------------------------------------------------
  V0  Baseline closed box. Sensor effectively coupled to a solar-loaded wall;
      light internal electronics/battery self-heating; modest natural
      convection. This is the "enclosure reads hot" baseline.
  V0P Painted closed-box control. V0 with only solar absorptance changed to
      match V1/V2; geometry, heat load, convection and emissivity stay fixed.
      V0P-to-V1 remains a system comparison, not an isolated shielding effect.
  V1  Passive multi-plate radiation shield (Stevenson-style). Stacked plates
      shade the sensor (large reduction in the solar flux that reaches it) and
      open inter-plate gaps boost natural convection. Two-zone layout keeps the
      electronics self-heating out of the sensor compartment.
  V2  Actively aspirated reference (optional). V1 shield plus a low-power fan
      that forces air past the sensor, raising the convection coefficient to a
      forced-convection value. Modeled as the upper-bound airflow benchmark.

All physical inputs are stated in ``ASSUMPTIONS`` below with a source/status and
are swept where uncertain. Run with ``--help`` for options.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field, replace

import numpy as np

SIGMA = 5.670374419e-8  # Stefan-Boltzmann constant [W m^-2 K^-4]


# ---------------------------------------------------------------------------
# Assumptions ledger (every model input, with source/status)
# ---------------------------------------------------------------------------
# status codes:
#   bounded   -> bounded engineering assumption, to be measured/refined
#   geometry  -> placeholder geometry, TODO-from-lab baseline_system_description
#   physics   -> standard physical constant / textbook correlation form
#   swept     -> varied across a range in the main sweep
# Canonical provenance and evidence status for every entry below live in
# docs/PARAMETER_REGISTER.csv (stable IDs P-*). The status strings here are the LOCAL shorthand;
# the register reconciles them with the literature, lab and claim taxonomies and records which
# values are contradicted by a source, uncited, or lab-required. Do not duplicate values there.
ASSUMPTIONS = [
    # name, value, units, source/status, note
    ("G_clear_sky", "800-1000", "W/m^2", "swept/bounded",
     "Clear-sky global horizontal irradiance on the projected area; sweep band."),
    ("T_air", 30.0, "degC", "bounded",
     "Ambient air temperature for the heat-soak case (warm clear day)."),
    ("RH_air", 50.0, "%", "bounded",
     "True ambient relative humidity used to anchor the RH-error mapping."),
    ("T_sky_offset", 20.0, "K", "bounded",
     "Clear-sky radiant sky temperature is taken as T_air - 20 K (clear-sky depression)."),
    ("alpha_V0", 0.90, "-", "bounded",
     "Solar absorptance of the baseline box surface (dark/unspecified finish, worst-ish case)."),
    ("alpha_shield", 0.30, "-", "bounded",
     "Solar absorptance of a light/white high-reflectance shield surface (framework rec.)."),
    ("eps_surface", 0.90, "-", "bounded",
     "Long-wave emissivity of painted plastic/printed surface (typical 0.85-0.95)."),
    ("f_sky_V0", 0.50, "-", "bounded",
     "Fraction of the baseline box outer area that radiates to the cold sky (upper/side faces); "
     "the rest exchanges long-wave with surroundings (ground/mast) at ~ambient."),
    ("f_sky_shield", 0.05, "-", "bounded",
     "Fraction of the shielded sensor element that sees the cold sky directly; the plates "
     "intentionally block the sky view, so the sensor exchanges long-wave mostly with the "
     "surrounding plates/air at ~ambient (this is why a shield does not over-cool below ambient)."),
    ("A_proj_V0", 0.030, "m^2", "geometry/TODO-from-lab",
     "Sun-facing projected area of the baseline box (~0.17 x 0.17 m face)."),
    ("A_conv_V0", 0.090, "m^2", "geometry/TODO-from-lab",
     "Convecting/radiating external area of the baseline box (~6 faces of ~0.17 m cube minus mount)."),
    ("A_proj_shield", 0.012, "m^2", "geometry/TODO-from-lab",
     "Effective sun-exposed projected area reaching the shielded sensor zone (plates shade most of it)."),
    ("A_conv_shield", 0.020, "m^2", "geometry/TODO-from-lab",
     "Convecting/radiating area of the small shielded sensor element wetted by inter-plate through-flow "
     "(a sensor PCB/probe is small; only the local element, not the whole shield, sets its balance)."),
    ("shield_solar_factor", 0.18, "-", "bounded",
     "Fraction of incident solar flux that still reaches the sensor through a multi-plate shield "
     "(view-factor/shading reduction; multi-plate shields cut direct load by roughly 80-90%, but "
     "diffuse/reflected sky and warm-plate re-radiation leak in, so this is deliberately not near-zero)."),
    ("Q_int_V0", 0.8, "W", "bounded/TODO-from-lab",
     "Internal electronics+battery dissipation coupled to the sensor in the single-zone baseline."),
    ("Q_int_shielded", 0.1, "W", "bounded/TODO-from-lab",
     "Residual self-heating reaching the sensor in the two-zone (electronics separated) layout."),
    ("h_free_floor", 5.0, "W/m^2K", "physics",
     "Free/low-wind convective coefficient floor used at ~0 m/s wind."),
    ("h_wind_slope", 4.0, "W/m^2K per (m/s)", "physics",
     "Linear wind term: h_ext ~= h_free_floor + slope * wind (flat-plate forced-convection scaling)."),
    ("shield_conv_boost", 1.4, "-", "bounded",
     "Natural-convection enhancement of the multi-plate shield (open inter-plate gaps chimney air)."),
    ("shield_air_preheat_calm", 1.2, "K", "bounded",
     "Solar-heated shield plates warm the through-flowing air slightly above true ambient before it "
     "reaches the sensor; this plate-to-air coupling is the dominant residual bias of a real passive "
     "screen at low wind. Modeled as a calm-wind air pre-heat that decays as wind/aspiration rises."),
    ("preheat_wind_halflife", 1.5, "m/s", "bounded",
     "Wind speed at which the shield air pre-heat is cut in half (ventilation flushes the warmed air)."),
    ("h_fan_V2", 25.0, "W/m^2K", "bounded",
     "Forced-convection coefficient at the sensor with the low-power aspiration fan running."),
    ("wind_sweep", "0.0-5.0", "m/s", "swept",
     "External wind speed sweep mapped to h_ext via the linear correlation above."),
]


@dataclass
class Variant:
    """One enclosure variant's lumped thermal parameters."""

    vid: str
    name: str
    alpha: float            # solar absorptance of the load-bearing surface [-]
    eps: float              # long-wave emissivity [-]
    a_proj: float           # projected sun-facing area feeding the sensor zone [m^2]
    a_conv: float           # convecting/radiating area of the sensor-coupled surface [m^2]
    q_internal: float       # internal self-heating reaching the sensor [W]
    f_sky: float            # fraction of A_conv radiating to the cold sky [-]
    solar_factor: float = 1.0   # fraction of incident solar that reaches the sensor zone [-]
    conv_boost: float = 1.0     # multiplier on the external convection coefficient [-]
    forced_h: float | None = None  # if set, fixed forced-convection coefficient [W/m^2K]
    note: str = ""


def h_external(wind_ms: float, h_floor: float, slope: float) -> float:
    """External convective coefficient from wind speed (linear flat-plate scaling)."""
    return h_floor + slope * max(wind_ms, 0.0)


def shield_air_preheat(wind_ms: float, preheat_calm: float, half_life: float, forced: bool) -> float:
    """Wind-dependent shield air pre-heat [K] above true ambient.

    Solar-warmed plates heat the through-flowing air; ventilation flushes it.
    Modeled as exponential decay with wind, ``dT = preheat_calm * 2^(-wind/half_life)``.
    Forced aspiration (V2) is treated as a strong, fixed flush (~3 m/s equivalent),
    so its residual pre-heat is small but nonzero.
    """
    if forced:
        eff_wind = 3.0
    else:
        eff_wind = max(wind_ms, 0.0)
    return preheat_calm * (2.0 ** (-eff_wind / max(half_life, 1e-6)))


def solve_surface_temperature(
    variant: Variant,
    g_solar: float,
    t_air_c: float,
    t_sky_c: float,
    h_ext: float,
    air_preheat_k: float = 0.0,
) -> float:
    """Solve the steady-state energy balance for the sensor-surface temperature.

    Balance (W):
        alpha * solar_factor * G * A_proj + Q_internal
            = h_eff * A_conv * (T_s - T_air)
              + eps * sigma * A_conv * [ f_sky * (T_s^4 - T_sky^4)
                                         + (1 - f_sky) * (T_s^4 - T_air^4) ]

    The long-wave term is split: a fraction ``f_sky`` of the surface radiates to
    the cold clear sky, the remainder exchanges with the surroundings (ground,
    mast, plates, internal air) at ambient temperature. This matters for the
    shield: by intentionally blocking the sky view (small ``f_sky``) the plates
    stop the sensor element from radiatively over-cooling below ambient, so the
    shielded reading converges to ~ambient rather than to an unphysical
    sub-ambient temperature. (A bare sky-facing plate with f_sky -> 1 *can*
    sit below ambient at night; here we model the daytime sensor, not a
    radiative cooler.)

    The convective sink and the (1 - f_sky) surroundings-radiation reference use
    the *local* air temperature, which for a shield is true ambient plus
    ``air_preheat_k`` (the plates warm the through-flowing air). The returned
    delta-T is still referenced to TRUE ambient, so this pre-heat shows up as
    residual shield bias -- the dominant real-world error of a passive screen at
    low wind.

    Returns T_s in degrees Celsius. Solved by bracketed bisection: the residual
    (heat in minus heat out) is strictly decreasing in T_s (both loss terms
    grow with T_s), so the root is unique. The bracket spans below and above
    ambient so a genuinely sub-ambient solution is reported honestly rather than
    clamped.
    """
    t_air = t_air_c + 273.15
    t_local = t_air + air_preheat_k  # local air the sensor exchanges with
    t_sky = t_sky_c + 273.15

    if variant.forced_h is not None:
        h_eff = variant.forced_h
    else:
        h_eff = h_ext * variant.conv_boost

    q_in = (
        variant.alpha * variant.solar_factor * g_solar * variant.a_proj
        + variant.q_internal
    )
    f_sky = variant.f_sky

    def residual(t_s: float) -> float:
        q_conv = h_eff * variant.a_conv * (t_s - t_local)
        q_rad = (
            variant.eps * SIGMA * variant.a_conv
            * (f_sky * (t_s**4 - t_sky**4) + (1.0 - f_sky) * (t_s**4 - t_local**4))
        )
        return q_in - (q_conv + q_rad)

    # Bracket the root. Residual is strictly decreasing in T_s. Lower bound is
    # below the sky temperature (residual > 0 there for any non-negative load),
    # upper bound is well above any realistic equilibrium.
    lo = t_sky - 20.0
    hi = t_air + 150.0
    r_lo, r_hi = residual(lo), residual(hi)
    if r_lo <= 0.0:  # input cannot even hold lo; degenerate, return lo
        return lo - 273.15
    if r_hi >= 0.0:  # load exceeds bracket; return hi
        return hi - 273.15
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if residual(mid) > 0.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-7:
            break
    return 0.5 * (lo + hi) - 273.15


# ---------------------------------------------------------------------------
# Psychrometrics: map a sensor temperature rise to reported RH error
# ---------------------------------------------------------------------------
def saturation_vapor_pressure_pa(t_c: float) -> float:
    """Saturation vapor pressure over water [Pa] (Tetens/Magnus form)."""
    return 610.94 * math.exp(17.625 * t_c / (t_c + 243.04))


def reported_rh_at_warm_sensor(rh_true_pct: float, t_air_c: float, t_sensor_c: float) -> float:
    """Reported RH when air at (T_air, RH_true) is heated to the sensor temperature.

    Physical assumption: the sensor sits in air whose absolute water-vapor
    content is the ambient value, but whose temperature has been raised to the
    sensor/surface temperature by self-heating. RH is the ratio of the (fixed)
    actual vapor pressure to the saturation pressure at the warmer temperature,
    so a warm sensor reports a *low* RH. The actual vapor pressure is held at
    the ambient partial pressure (constant absolute humidity).
    """
    e_actual = (rh_true_pct / 100.0) * saturation_vapor_pressure_pa(t_air_c)
    es_sensor = saturation_vapor_pressure_pa(t_sensor_c)
    return 100.0 * e_actual / es_sensor


# ---------------------------------------------------------------------------
# Variant construction from the assumptions ledger
# ---------------------------------------------------------------------------
def _a(name: str):
    for n, v, *_ in ASSUMPTIONS:
        if n == name:
            return v
    raise KeyError(name)


def build_variants() -> list[Variant]:
    eps = float(_a("eps_surface"))
    variants = [
        Variant(
            vid="V0",
            name="Baseline closed box",
            alpha=float(_a("alpha_V0")),
            eps=eps,
            a_proj=float(_a("A_proj_V0")),
            a_conv=float(_a("A_conv_V0")),
            q_internal=float(_a("Q_int_V0")),
            f_sky=float(_a("f_sky_V0")),
            solar_factor=1.0,
            conv_boost=1.0,
            note="Single-zone; sensor coupled to solar-loaded wall + electronics self-heating.",
        ),
        Variant(
            vid="V1",
            name="Passive multi-plate shield",
            alpha=float(_a("alpha_shield")),
            eps=eps,
            a_proj=float(_a("A_proj_shield")),
            a_conv=float(_a("A_conv_shield")),
            q_internal=float(_a("Q_int_shielded")),
            f_sky=float(_a("f_sky_shield")),
            solar_factor=float(_a("shield_solar_factor")),
            conv_boost=float(_a("shield_conv_boost")),
            note="Stacked plates shade sensor + chimney natural convection; two-zone layout.",
        ),
        Variant(
            vid="V2",
            name="Actively aspirated reference",
            alpha=float(_a("alpha_shield")),
            eps=eps,
            a_proj=float(_a("A_proj_shield")),
            a_conv=float(_a("A_conv_shield")),
            q_internal=float(_a("Q_int_shielded")),
            f_sky=float(_a("f_sky_shield")),
            solar_factor=float(_a("shield_solar_factor")),
            conv_boost=1.0,
            forced_h=float(_a("h_fan_V2")),
            note="V1 shield + low-power fan; forced convection at the sensor (upper-bound airflow).",
        ),
    ]
    # Preserve the legacy V0/V1/V2 order used by sensitivity callers. Copy the
    # dark box rather than reconstructing it: painting must not change geometry,
    # ventilation, sky view or coupled electronics load accidentally.
    variants.append(replace(
        variants[0], vid="V0P", name="Painted closed-box control",
        alpha=float(_a("alpha_shield")),
        note="V0 with only absorptance matched to V1/V2; all other physics unchanged.",
    ))
    return variants


# ---------------------------------------------------------------------------
# Sweeps
# ---------------------------------------------------------------------------
@dataclass
class SweepResult:
    wind: np.ndarray
    g_values: list[float]
    # dT[vid][g] -> array over wind
    dT: dict = field(default_factory=dict)
    rh_err: dict = field(default_factory=dict)


def run_sweep(
    variants: list[Variant],
    wind: np.ndarray,
    g_values: list[float],
    t_air_c: float,
    rh_true_pct: float,
    t_sky_c: float,
    h_floor: float,
    h_slope: float,
) -> SweepResult:
    preheat_calm = float(_a("shield_air_preheat_calm"))
    half_life = float(_a("preheat_wind_halflife"))
    res = SweepResult(wind=wind, g_values=g_values)
    for var in variants:
        res.dT[var.vid] = {}
        res.rh_err[var.vid] = {}
        shielded = var.solar_factor < 1.0  # V1/V2 see plate-warmed air
        for g in g_values:
            d = np.zeros_like(wind, dtype=float)
            rerr = np.zeros_like(wind, dtype=float)
            for i, w in enumerate(wind):
                h_ext = h_external(float(w), h_floor, h_slope)
                preheat = 0.0
                if shielded:
                    # solar pre-heat scales with the available solar relative to a 1000 W/m^2 ref
                    preheat = shield_air_preheat(
                        float(w), preheat_calm, half_life, forced=var.forced_h is not None
                    ) * (g / 1000.0)
                t_s = solve_surface_temperature(var, g, t_air_c, t_sky_c, h_ext, air_preheat_k=preheat)
                d[i] = t_s - t_air_c
                rh_reported = reported_rh_at_warm_sensor(rh_true_pct, t_air_c, t_s)
                rerr[i] = rh_reported - rh_true_pct  # negative = reads low
            res.dT[var.vid][g] = d
            res.rh_err[var.vid][g] = rerr
    return res


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def print_assumptions() -> None:
    print("=" * 78)
    print("ASSUMPTIONS LEDGER (every input; SIMULATION, pending lab data)")
    print("=" * 78)
    print(f"{'input':<22}{'value':>12}  {'units':<14}{'status':<22}")
    print("-" * 78)
    for name, value, units, status, _note in ASSUMPTIONS:
        print(f"{name:<22}{str(value):>12}  {units:<14}{status:<22}")
    print("-" * 78)
    print("Notes:")
    for name, _value, _units, _status, note in ASSUMPTIONS:
        print(f"  {name}: {note}")
    print()


def print_bias_table(res: SweepResult, variants: list[Variant], wind_marks: list[float]) -> None:
    """Print the headline bias-vs-variant table.

    Columns: each variant; rows: (G, wind) operating points. Values are
    sensor delta-T [degC] and the corresponding RH error [%RH] (reads low).
    """
    vid_order = [v.vid for v in variants]
    name_by_id = {v.vid: v.name for v in variants}

    print("=" * 78)
    print("BIAS-VS-VARIANT TABLE  (SIMULATION -- pending lab co-location data)")
    print("delta-T = sensor temperature rise above true ambient [degC]")
    print("RH_err  = reported-minus-true relative humidity [%RH] (negative = reads dry)")
    print("V0P holds V0 geometry/load/airflow fixed; only absorptance matches the shield.")
    print("V0P versus V1 is a system comparison, not an isolated shielding effect.")
    print("=" * 78)
    header = f"{'G[W/m2]':>8}{'wind[m/s]':>11}  " + "".join(
        f"{name_by_id[v]+' dT/RHerr':>26}" for v in vid_order
    )
    print(header)
    print("-" * len(header))
    for g in res.g_values:
        for wmark in wind_marks:
            idx = int(np.argmin(np.abs(res.wind - wmark)))
            row = f"{g:>8.0f}{res.wind[idx]:>11.1f}  "
            for vid in vid_order:
                dt = res.dT[vid][g][idx]
                rh = res.rh_err[vid][g][idx]
                row += f"{dt:>13.1f}{rh:>13.1f}"
            print(row)
        print("-" * len(header))

    # Compact summary band across the full sweep at the high-solar case.
    g_hi = max(res.g_values)
    print()
    print(f"Range across wind {res.wind.min():.1f}-{res.wind.max():.1f} m/s at G={g_hi:.0f} W/m^2:")
    for vid in vid_order:
        d = res.dT[vid][g_hi]
        r = res.rh_err[vid][g_hi]
        print(
            f"  {name_by_id[vid]:<30} dT = {d[np.argmin(res.wind)]:5.1f} (calm) .. "
            f"{d[np.argmax(res.wind)]:4.1f} (windy) degC,"
            f"  RH_err = {r.min():6.1f} .. {r.max():5.1f} %RH"
        )
    print()


def write_bias_table(res: SweepResult, variants: list[Variant], wind_marks: list[float],
                     out_path: str) -> None:
    """Write the bias-vs-variant table as CSV -- the artifact of record for this model.

    The figure is deliberately NOT the comparable artifact: its layout depends on text
    extents, so a different font build shifts the axes by a few pixels and rescales the
    y-mapping, which moves every curve. That makes a committed-vs-fresh PNG diff report
    drift when the numbers are identical. These values are the thing to compare.
    """
    import csv as _csv
    import os as _os

    _os.makedirs(_os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        w = _csv.writer(fh, lineterminator="\n")
        w.writerow(["# SIMULATION -- pending lab co-location data; see docs/results.md"])
        w.writerow(["g_w_m2", "wind_m_s", "variant_id", "variant_name",
                    "delta_t_degc", "rh_err_pct"])
        for g in res.g_values:
            for wmark in wind_marks:
                idx = int(np.argmin(np.abs(res.wind - wmark)))
                for v in variants:
                    w.writerow([f"{g:.0f}", f"{res.wind[idx]:.1f}", v.vid, v.name,
                                f"{res.dT[v.vid][g][idx]:.4f}",
                                f"{res.rh_err[v.vid][g][idx]:.4f}"])
    print(f"[table] wrote {out_path}")


def make_figure(res: SweepResult, variants: list[Variant], out_path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    g_hi = max(res.g_values)
    g_lo = min(res.g_values)
    colors = {"V0": "#c0392b", "V0P": "#7d3c98", "V1": "#2980b9", "V2": "#27ae60"}
    markers = {"V0": "o", "V0P": "s", "V1": "^", "V2": "D"}
    name_by_id = {v.vid: v.name for v in variants}

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))

    ax = axes[0]
    for v in variants:
        ax.plot(
            res.wind, res.dT[v.vid][g_hi],
            color=colors[v.vid], lw=2.2,
            marker=markers[v.vid], markevery=10, markersize=3,
            label=f"{v.vid} {name_by_id[v.vid]} (G={g_hi:.0f})",
        )
        ax.plot(
            res.wind, res.dT[v.vid][g_lo],
            color=colors[v.vid], lw=1.2, ls="--", alpha=0.7,
        )
    ax.set_xlabel("External wind speed [m/s]")
    ax.set_ylabel("Sensor $\\Delta T$ above ambient [$^\\circ$C]")
    ax.set_title("Solar self-heating bias vs variant")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, loc="upper right")
    ax.axhline(0, color="k", lw=0.6)

    ax = axes[1]
    for v in variants:
        ax.plot(
            res.wind, res.rh_err[v.vid][g_hi],
            color=colors[v.vid], lw=2.2,
            marker=markers[v.vid], markevery=10, markersize=3,
            label=f"{v.vid} {name_by_id[v.vid]}",
        )
        ax.plot(
            res.wind, res.rh_err[v.vid][g_lo],
            color=colors[v.vid], lw=1.2, ls="--", alpha=0.7,
        )
    ax.set_xlabel("External wind speed [m/s]")
    ax.set_ylabel("Reported RH error [%RH] (negative = reads dry)")
    ax.set_title("RH bias from self-heating vs variant")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, loc="lower right")
    ax.axhline(0, color="k", lw=0.6)

    fig.suptitle(
        f"SIMULATION (pending lab data): solid = G={g_hi:.0f} W/m$^2$, "
        f"dashed = G={g_lo:.0f} W/m$^2$",
        fontsize=9, y=1.02,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[figure] wrote {out_path}")


def sensitivity_block(
    variants: list[Variant],
    t_air_c: float,
    rh_true_pct: float,
    t_sky_c: float,
    h_floor: float,
    h_slope: float,
) -> None:
    """One-at-a-time sensitivity of V0 and V1 delta-T to the uncertain inputs.

    Reported at a fixed reference point (G=1000 W/m^2, low wind 0.5 m/s) so the
    reader sees which assumption moves the bias most -- the inputs the plan says
    must be measured rather than guessed.
    """
    g_ref = 1000.0
    w_ref = 0.5
    h_ref = h_external(w_ref, h_floor, h_slope)
    preheat_calm = float(_a("shield_air_preheat_calm"))
    half_life = float(_a("preheat_wind_halflife"))

    base = {v.vid: v for v in build_variants()}

    print("=" * 78)
    print("SENSITIVITY (one-at-a-time), reference point G=1000 W/m^2, wind=0.5 m/s")
    print("delta-T [degC]; shows which uncertain input dominates the bias")
    print("=" * 78)

    def dt_of(v: Variant) -> float:
        preheat = 0.0
        if v.solar_factor < 1.0:
            preheat = shield_air_preheat(
                w_ref, preheat_calm, half_life, forced=v.forced_h is not None
            ) * (g_ref / 1000.0)
        return solve_surface_temperature(v, g_ref, t_air_c, t_sky_c, h_ref, air_preheat_k=preheat) - t_air_c

    print(f"{'perturbation':<46}{'V0 dT':>10}{'V1 dT':>10}")
    print("-" * 66)
    print(f"{'baseline':<46}{dt_of(base['V0']):>10.1f}{dt_of(base['V1']):>10.1f}")

    # alpha (baseline surface darkness): light vs dark
    v0_light = base["V0P"]
    print(f"{'V0 surface painted white (alpha 0.90 -> 0.30)':<46}"
          f"{dt_of(v0_light):>10.1f}{'-':>10}")

    # shield solar factor: better/worse shading
    v1_leaky2 = build_variants()[1]
    v1_leaky2.solar_factor = 0.30
    print(f"{'V1 shading worse (solar_factor 0.18 -> 0.30)':<46}"
          f"{'-':>10}{dt_of(v1_leaky2):>10.1f}")

    # convection boost off
    v1_noboost = build_variants()[1]
    v1_noboost.conv_boost = 1.0
    print(f"{'V1 no convection boost (1.4 -> 1.0)':<46}"
          f"{'-':>10}{dt_of(v1_noboost):>10.1f}")

    # shield air pre-heat doubled (worse plate-to-air coupling / weak vent)
    # applied via the air_preheat path, so perturb at the call site
    v1_hotair = build_variants()[1]
    preheat2 = shield_air_preheat(w_ref, 2.0 * preheat_calm, half_life, forced=False) * (g_ref / 1000.0)
    dt_hotair = solve_surface_temperature(v1_hotair, g_ref, t_air_c, t_sky_c, h_ref,
                                          air_preheat_k=preheat2) - t_air_c
    print(f"{'V1 plate air pre-heat doubled (1.2 -> 2.4 K calm)':<46}"
          f"{'-':>10}{dt_hotair:>10.1f}")

    # internal self-heating doubled (V0 single-zone)
    v0_hot = build_variants()[0]
    v0_hot.q_internal = 1.6
    print(f"{'V0 internal load doubled (0.8 -> 1.6 W)':<46}"
          f"{dt_of(v0_hot):>10.1f}{'-':>10}")

    # emissivity low (poor IR emitter, e.g. bare/foil)
    v0_lowe = build_variants()[0]
    v0_lowe.eps = 0.50
    print(f"{'V0 low emissivity (0.90 -> 0.50)':<46}"
          f"{dt_of(v0_lowe):>10.1f}{'-':>10}")
    print("-" * 66)
    print()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--t-air", type=float, default=float(_a("T_air")),
                   help="Ambient air temperature [degC]")
    p.add_argument("--rh-air", type=float, default=float(_a("RH_air")),
                   help="True ambient relative humidity [%%]")
    p.add_argument("--g-values", type=float, nargs="+", default=[800.0, 1000.0],
                   help="Clear-sky solar flux values to sweep [W/m^2]")
    p.add_argument("--wind-max", type=float, default=5.0, help="Max wind speed [m/s]")
    p.add_argument("--wind-points", type=int, default=51, help="Number of wind samples")
    p.add_argument("--wind-marks", type=float, nargs="+", default=[0.0, 0.5, 1.0, 2.0, 5.0],
                   help="Wind speeds to print in the table [m/s]")
    p.add_argument("--figure", default="analysis/figures/thermal_bias.png",
                   help="Output figure path (PNG). Set empty to skip.")
    p.add_argument("--no-figure", action="store_true", help="Skip figure generation")
    p.add_argument("--night-table", default="analysis/output/thermal_bias_night_table.csv",
                   help="Write the zero-solar (night, clear-sky) bias table here. Same solver, same "
                        "assumptions, G = 0: reports the bias without solar heating. "
                        "The sign depends on the energy balance. Set to '' to skip.")
    p.add_argument("--table", default="analysis/output/thermal_bias_table.csv",
                   help="Write the bias-vs-variant table here (the artifact of record; "
                        "compare this, not the PNG). Set to '' to skip.")
    args = p.parse_args()

    t_sky_c = args.t_air - float(_a("T_sky_offset"))
    h_floor = float(_a("h_free_floor"))
    h_slope = float(_a("h_wind_slope"))

    variants = build_variants()
    wind = np.linspace(0.0, args.wind_max, args.wind_points)

    print_assumptions()
    print(f"Operating ambient: T_air = {args.t_air:.1f} degC, RH_true = {args.rh_air:.1f} %, "
          f"T_sky = {t_sky_c:.1f} degC (clear-sky depression {float(_a('T_sky_offset')):.0f} K)\n")

    res = run_sweep(
        variants, wind, args.g_values,
        t_air_c=args.t_air, rh_true_pct=args.rh_air, t_sky_c=t_sky_c,
        h_floor=h_floor, h_slope=h_slope,
    )

    print_bias_table(res, variants, args.wind_marks)
    if args.table:
        write_bias_table(res, variants, args.wind_marks, args.table)
    if args.night_table:
        # Night, clear sky: the same energy balance with no solar load. Long-wave loss
        # dominates at the default operating point, not for every possible input. Kept as a
        # separate table so the daytime table and figure are byte-unchanged.
        night = run_sweep(
            variants, wind, [0.0],
            t_air_c=args.t_air, rh_true_pct=args.rh_air, t_sky_c=t_sky_c,
            h_floor=h_floor, h_slope=h_slope,
        )
        print("\nNIGHT CLEAR-SKY CASE (G = 0, same T_sky depression): signed delta-T under these assumptions")
        print_bias_table(night, variants, args.wind_marks)
        write_bias_table(night, variants, args.wind_marks, args.night_table)
    sensitivity_block(variants, args.t_air, args.rh_air, t_sky_c, h_floor, h_slope)

    if not args.no_figure and args.figure:
        import os
        os.makedirs(os.path.dirname(args.figure) or ".", exist_ok=True)
        make_figure(res, variants, args.figure)

    print("NOTE: All values above are SIMULATION outputs and are the analytical")
    print("baseline for the comparisons in ROADMAP.md. They remain predictions")
    print("pending lab and co-location data; no")
    print("regulatory-grade or certified-performance claim is implied.")


if __name__ == "__main__":
    main()
