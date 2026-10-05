#!/usr/bin/env python3
"""Transient prediction of enclosure temperature bias from a weather time series.

Extends the steady energy balance in ``thermal_bias.py`` with a thermal mass, so
the bias can be predicted hour by hour from real weather and later compared with
the co-location rig. Same balance, same variants; one added state per variant:

    C dT/dt = alpha * solar_factor * G * A_proj + Q_int
              - h_eff * A_conv * (T - T_local)
              - eps * sigma * A_conv * [f_sky (T^4 - T_sky^4) + (1 - f_sky)(T^4 - T_local^4)]

Integrated with a linearised implicit Euler step, which stays stable when the
time step is longer than a small shield's time constant. With constant inputs it
converges to ``thermal_bias.solve_surface_temperature``; the tests check that.

Inputs it needs that the steady model did not:
  * hourly air temperature, dew point, wind at 10 m, global horizontal irradiance
    and cloud cover (here from the Open-Meteo archive, CC BY 4.0);
  * a sky temperature, from the Berdahl–Martin clear-sky emissivity with the
    Clark–Allen cloud correction;
  * a heat capacity per variant and a factor taking 10 m wind to sensor height.

Uncertainty: every bounded input is drawn from the range in ``PRIORS`` and the
run is repeated. The bands show the spread those declared ranges produce. They
are not measured uncertainty. The rig's step-response test (protocol item 6)
and I1 load test are what pin the heat capacity and the internal-power term.

Run: python -m analysis.thermal_transient
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from analysis.thermal_bias import SIGMA, _a, build_variants, h_external, solve_surface_temperature

ROOT = Path(__file__).resolve().parents[1]
WEATHER = ROOT / "analysis/input/openmeteo_brooklyn_20260901_20260914.json"
OUT_JSON = ROOT / "analysis/output/thermal_transient_prediction.json"
OUT_FIG = ROOT / "analysis/figures/thermal_transient_prediction.png"

DT_S = 60.0          # integration step [s]
SPIN_UP_H = 24       # first day discarded: the initial state is a guess
N_SAMPLES = 400
SEED = 20261004
FORCED_EQUIV_WIND = 3.0   # same fixed flush the steady model uses for the aspirated variant

# Declared ranges for the bounded inputs. Uniform draws. Where the repository
# already states a range it is reused (noted); the rest are declared here and are
# assumptions to be pinned by the rig, not measurements.
PRIORS = {
    # name: (low, high, applies_to, note)
    "alpha_dark": (0.80, 0.95, ("V0",), "dark or unspecified finish; nominal 0.90"),
    "alpha_light": (0.20, 0.40, ("V0P", "V1", "V2"), "white or light finish; nominal 0.30"),
    "eps": (0.85, 0.95, ("V0", "V0P", "V1", "V2"), "range stated in the eps_surface note"),
    "solar_factor": (0.18, 0.30, ("V1", "V2"), "repo sensitivity range for shield shading"),
    "conv_boost": (1.0, 1.4, ("V1",), "repo sensitivity range for the shield chimney boost"),
    "preheat_calm_k": (1.2, 2.4, ("V1", "V2"), "repo sensitivity range for plate air pre-heat"),
    "q_int_box_w": (0.4, 1.6, ("V0", "V0P"), "half to double the nominal 0.8 W"),
    "q_int_shield_w": (0.05, 0.2, ("V1", "V2"), "half to double the nominal 0.1 W"),
    "f_sky_box": (0.3, 0.7, ("V0", "V0P"), "declared; nominal 0.50"),
    "f_sky_shield": (0.0, 0.1, ("V1", "V2"), "declared; nominal 0.05"),
    "h_floor": (3.5, 6.5, ("V0", "V0P", "V1"), "declared; nominal 5.0 W/m^2K"),
    "h_slope": (3.0, 5.0, ("V0", "V0P", "V1"), "declared; nominal 4.0 W/m^2K per m/s"),
    "wind_height_factor": (0.4, 0.9, ("V0", "V0P", "V1"), "declared; 10 m reanalysis wind to sensor height at an urban site"),
    "c_box_j_per_k": (150.0, 600.0, ("V0", "V0P"), "declared; 0.1-0.4 kg of plastic wall at ~1500 J/kgK"),
    "c_shield_j_per_k": (5.0, 40.0, ("V1", "V2"), "declared; small sensor element and its mount"),
}

NOMINAL = {
    "alpha_dark": 0.90, "alpha_light": 0.30, "eps": 0.90, "solar_factor": 0.18,
    "conv_boost": 1.4, "preheat_calm_k": 1.2, "q_int_box_w": 0.8, "q_int_shield_w": 0.1,
    "f_sky_box": 0.50, "f_sky_shield": 0.05, "h_floor": 5.0, "h_slope": 4.0,
    "wind_height_factor": 0.65, "c_box_j_per_k": 300.0, "c_shield_j_per_k": 15.0,
}


def sky_temperature_c(t_air_c, t_dew_c, cloud_frac):
    """Effective sky temperature from Berdahl–Martin clear-sky emissivity and the
    Clark–Allen cloud correction (cloud cover in tenths)."""
    td = np.asarray(t_dew_c, float) / 100.0
    eps_clear = 0.711 + 0.56 * td + 0.73 * td**2
    n = 10.0 * np.clip(np.asarray(cloud_frac, float), 0.0, 1.0)
    eps_sky = np.clip(eps_clear * (1.0 + 0.0224 * n - 0.0035 * n**2 + 0.00028 * n**3), 0.0, 1.0)
    t_air_k = np.asarray(t_air_c, float) + 273.15
    return eps_sky**0.25 * t_air_k - 273.15


def load_weather(path=WEATHER, dt_s=DT_S):
    raw = json.loads(Path(path).read_text())
    h = raw["hourly"]
    hours = np.arange(len(h["time"]), dtype=float)
    t = np.arange(0.0, hours[-1] * 3600.0 + dt_s / 2, dt_s)
    interp = lambda key: np.interp(t / 3600.0, hours, np.asarray(h[key], float))
    w = {
        "t_s": t,
        "time_labels": h["time"],
        "t_air": interp("temperature_2m"),
        "t_dew": interp("dew_point_2m"),
        "wind10": np.maximum(interp("wind_speed_10m"), 0.0),
        "ghi": np.maximum(interp("shortwave_radiation"), 0.0),
        "cloud": interp("cloud_cover") / 100.0,
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "source": raw.get("source", "Open-Meteo historical weather archive"),
        "lat": raw["latitude"], "lon": raw["longitude"],
    }
    w["t_sky"] = sky_temperature_c(w["t_air"], w["t_dew"], w["cloud"])
    return w


def _params_for(vid, p):
    """Map drawn parameters onto one variant. Arrays broadcast over samples."""
    v = {x.vid: x for x in build_variants()}[vid]
    light = vid in ("V0P", "V1", "V2")
    box = vid in ("V0", "V0P")
    return {
        "alpha": p["alpha_light"] if light else p["alpha_dark"],
        "eps": p["eps"],
        "a_proj": v.a_proj,
        "a_conv": v.a_conv,
        "q_int": p["q_int_box_w"] if box else p["q_int_shield_w"],
        "f_sky": p["f_sky_box"] if box else p["f_sky_shield"],
        "solar_factor": 1.0 if box else p["solar_factor"],
        "conv_boost": p["conv_boost"] if vid == "V1" else 1.0,
        "forced_h": v.forced_h,
        "shielded": not box,
        "preheat_calm": p["preheat_calm_k"],
        "half_life": float(_a("preheat_wind_halflife")),
        "c": p["c_box_j_per_k"] if box else p["c_shield_j_per_k"],
    }


def simulate(vid, weather, p, dt_s=DT_S):
    """Sensor temperature over time for one variant. ``p`` values may be scalars
    or 1-D arrays (one per Monte Carlo sample). Returns (n_steps, n_samples)."""
    q = _params_for(vid, p)
    n_steps = len(weather["t_s"])
    shape = np.broadcast(*[np.asarray(val) for val in p.values()]).shape or (1,)
    t = np.full(shape, weather["t_air"][0] + 273.15)
    out = np.empty((n_steps,) + shape)
    for k in range(n_steps):
        t_air = weather["t_air"][k] + 273.15
        t_sky = weather["t_sky"][k] + 273.15
        g = weather["ghi"][k]
        if q["forced_h"] is not None:
            h_eff = q["forced_h"]
            wind_eff = FORCED_EQUIV_WIND
        else:
            wind_eff = weather["wind10"][k] * p["wind_height_factor"]
            h_eff = (p["h_floor"] + p["h_slope"] * wind_eff) * q["conv_boost"]
        preheat = 0.0
        if q["shielded"]:
            preheat = q["preheat_calm"] * 2.0 ** (-wind_eff / max(q["half_life"], 1e-6)) * (g / 1000.0)
        t_loc = t_air + preheat
        q_in = q["alpha"] * q["solar_factor"] * g * q["a_proj"] + q["q_int"]
        rad = q["eps"] * SIGMA * q["a_conv"]
        net = (q_in - h_eff * q["a_conv"] * (t - t_loc)
               - rad * (q["f_sky"] * (t**4 - t_sky**4) + (1.0 - q["f_sky"]) * (t**4 - t_loc**4)))
        dnet = -h_eff * q["a_conv"] - 4.0 * rad * t**3
        t = t + dt_s * net / (q["c"] - dt_s * dnet)
        out[k] = t - 273.15
    return out


def draw(n, seed=SEED):
    rng = np.random.default_rng(seed)
    return {k: rng.uniform(lo, hi, n) for k, (lo, hi, *_rest) in PRIORS.items()}


def i1_sensitivity(wind_values=(0.5, 1.0, 2.0, 3.0), t_air_c=20.0):
    """Predicted bias change per watt of added internal power, in shade (G = 0),
    for the closed box and the shield, from the steady solver. This is the
    quantity the rig's first experiment (I1) measures."""
    t_sky = t_air_c - float(_a("T_sky_offset"))
    h_floor, h_slope = float(_a("h_free_floor")), float(_a("h_wind_slope"))
    out = {}
    for v in build_variants():
        if v.vid not in ("V0", "V1"):
            continue
        rows = []
        for w in wind_values:
            h = h_external(w, h_floor, h_slope)
            t0 = solve_surface_temperature(v, 0.0, t_air_c, t_sky, h)
            t1 = solve_surface_temperature(replace(v, q_internal=v.q_internal + 1.0), 0.0, t_air_c, t_sky, h)
            rows.append({"wind_m_s": w, "degc_per_w": round(t1 - t0, 3)})
        out[v.vid] = rows
    return out


def summarise(weather, runs):
    """Daytime, night and daily-peak bias per variant: median and 5-95% band
    across samples, after the spin-up day."""
    start = int(SPIN_UP_H * 3600 / DT_S)
    day = weather["ghi"][start:] > 50.0
    night = weather["ghi"][start:] <= 0.0
    steps_per_day = int(86400 / DT_S)
    summary = {}
    for vid, temp in runs.items():
        bias = temp[start:] - weather["t_air"][start:, None]
        n_days = bias.shape[0] // steps_per_day
        peaks = bias[: n_days * steps_per_day].reshape(n_days, steps_per_day, -1).max(axis=1)
        pct = lambda a: [round(float(x), 2) for x in np.percentile(a, [5, 50, 95])]
        summary[vid] = {
            "daytime_mean_bias_c_p05_p50_p95": pct(bias[day].mean(axis=0)),
            "night_mean_bias_c_p05_p50_p95": pct(bias[night].mean(axis=0)),
            "daily_peak_bias_c_p05_p50_p95": pct(peaks.mean(axis=0)),
        }
    return summary


def make_figure(weather, runs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    start = int(SPIN_UP_H * 3600 / DT_S)
    hours = weather["t_s"][start:] / 3600.0
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 2]})
    ax0.plot(hours, weather["ghi"][start:], color="#d08c00", lw=1, label="Solar, global horizontal [W/m²]")
    ax0b = ax0.twinx()
    ax0b.plot(hours, weather["wind10"][start:], color="#4a6fa5", lw=1, label="Wind at 10 m [m/s]")
    ax0.set_ylabel("Solar [W/m²]", color="#d08c00"); ax0b.set_ylabel("Wind, 10 m [m/s]", color="#4a6fa5")
    ax0.set_title("Inputs: Brooklyn, 2026-09-02 to 09-14 (Open-Meteo archive)", fontsize=10, loc="left")
    colors = {"V0": "#3b3b3b", "V0P": "#8a6d3b", "V1": "#2e7d32", "V2": "#1565c0"}
    names = {v.vid: v.name for v in build_variants()}
    for vid, temp in runs.items():
        bias = temp[start:] - weather["t_air"][start:, None]
        lo, mid, hi = np.percentile(bias, [5, 50, 95], axis=1)
        ax1.fill_between(hours, lo, hi, color=colors[vid], alpha=0.18, lw=0)
        ax1.plot(hours, mid, color=colors[vid], lw=1.1, label=f"{vid} {names[vid]}")
    ax1.axhline(0, color="#999", lw=0.6)
    ax1.set_ylabel("Predicted sensor minus air [°C]")
    ax1.set_xlabel("Hours from 2026-09-01 00:00 local")
    ax1.set_title("Model prediction: median and 5–95% band from declared parameter ranges (not measured)",
                  fontsize=10, loc="left")
    ax1.legend(fontsize=8, ncol=2, loc="upper left")
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", type=int, default=N_SAMPLES)
    ap.add_argument("--json", default=str(OUT_JSON))
    ap.add_argument("--figure", default=str(OUT_FIG))
    ap.add_argument("--no-figure", action="store_true")
    args = ap.parse_args()

    weather = load_weather()
    p = draw(args.samples)
    vids = ("V0", "V0P", "V1", "V2")
    runs = {vid: simulate(vid, weather, p) for vid in vids}
    nominal = {vid: simulate(vid, weather, {k: np.array([v]) for k, v in NOMINAL.items()}) for vid in vids}

    result = {
        "status": "MODEL PREDICTION; no co-location data exists",
        "model": "analysis/thermal_transient.py (steady balance of thermal_bias.py plus one thermal mass per variant)",
        "weather": {
            "file": str(WEATHER.relative_to(ROOT)), "sha256": weather["sha256"],
            "provider": "Open-Meteo historical weather archive (CC BY 4.0)",
            "grid_point_lat_lon": [weather["lat"], weather["lon"]],
            "period_local": [weather["time_labels"][0], weather["time_labels"][-1]],
        },
        "integration": {"dt_s": DT_S, "spin_up_h": SPIN_UP_H, "method": "linearised implicit Euler"},
        "monte_carlo": {"samples": args.samples, "seed": SEED, "distribution": "uniform within declared ranges"},
        "priors": {k: {"low": lo, "high": hi, "applies_to": list(app), "note": note}
                   for k, (lo, hi, app, note) in PRIORS.items()},
        "nominal": NOMINAL,
        "bias_summary": summarise(weather, runs),
        "nominal_summary": summarise(weather, nominal),
        "i1_prediction_shade_degc_per_w_nominal": i1_sensitivity(),
        "limits": [
            "Weather comes from a reanalysis grid point, not the rig site; the registered comparison uses on-site measured inputs.",
            "Global horizontal irradiance is applied to the projected area, as in the steady model.",
            "Bands come from declared ranges, not measured uncertainty; heat capacity and the wind-height factor are unpinned until the rig's step-response and I1 tests.",
            "Absorptance and solar factor enter as a product, so temperature alone cannot separate them.",
            "One thermal node per variant; the register's wall Biot estimate (P-BI, 0.07-0.72) says a printed box wall may not be isothermal.",
        ],
    }
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(result, indent=2) + "\n")
    if not args.no_figure:
        make_figure(weather, runs, args.figure)
    for vid, s in result["bias_summary"].items():
        print(vid, s)
    print("I1 (nominal, shade):", result["i1_prediction_shade_degc_per_w_nominal"])


if __name__ == "__main__":
    main()
