#!/usr/bin/env python3
"""Single-node thermal sensitivity calculation on preserved hourly weather.

C dT/dt = absorbed solar + effective coupled heat - convection - long-wave loss.
The initial state is stored at its timestamp. Each actual interval uses midpoint
instantaneous forcing and its preceding-hour solar mean, held piecewise constant.
A locally linearized exponential step is exact for a constant-coefficient RC
system. This is an assumed-input sensitivity study, without thermal measurements.
See docs/results.md for the review status and acquisition/sky limitations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
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


SKY_SOURCE = "https://energyplus.readthedocs.io/en/stable/auxiliary-programs/auxiliary-programs.html#field-horizontal-infrared-radiation-intensity"
WEATHER_SOURCE = "https://open-meteo.com/en/docs/historical-weather-api"


def sky_temperature_c(t_air_c, t_dew_c, opaque_fraction):
    """Clark & Allen clear sky, Walton opaque-cloud correction per EnergyPlus.

    Dewpoint is in kelvin inside the logarithm, opaque cover in tenths.
    Total cloud fraction is not a substitute for opaque cover. The caller must
    supply measured opaque cover or label it as a scenario assumption.
    """
    td = np.asarray(t_dew_c, float) + 273.15
    opaque = np.asarray(opaque_fraction, float)
    if np.any(td <= 0) or np.any((opaque < 0) | (opaque > 1)):
        raise ValueError("invalid dewpoint or opaque-cloud fraction")
    clear = 0.787 + 0.764 * np.log(td / 273.0)
    n = 10.0 * opaque
    emissivity = clear * (1 + 0.0224*n - 0.0035*n**2 + 0.00028*n**3)
    if np.any(~np.isfinite(emissivity)) or np.any((emissivity <= 0) | (emissivity > 1)):
        raise ValueError("sky correlation outside physical emissivity range")
    return emissivity**0.25 * (np.asarray(t_air_c, float) + 273.15) - 273.15


def load_weather(path=WEATHER, dt_s=DT_S, opaque_fraction=0.0):
    """Node samples plus interval GHI: ghi[k] applies on (t[k-1], t[k]].

    Begin at the first instantaneous record; discard the preceding solar hour
    lacking other forcing. Stop at the final timestamp, without extending it.
    Include every hourly boundary even when dt_s does not divide an hour.
    """
    if not np.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("dt_s must be positive and finite")
    path = Path(path)
    raw = json.loads(path.read_text())
    h = raw["hourly"]
    expected = {"time": "iso8601", "temperature_2m": "°C", "dew_point_2m": "°C",
                "wind_speed_10m": "m/s", "shortwave_radiation": "W/m²", "cloud_cover": "%"}
    if any(raw["hourly_units"].get(k) != v for k, v in expected.items()):
        raise ValueError("weather units differ from the supported source convention")
    zone = ZoneInfo(raw["timezone"])
    offset = timedelta(seconds=raw["utc_offset_seconds"])
    dates = [datetime.fromisoformat(x).replace(tzinfo=zone) for x in h["time"]]
    if any(d.utcoffset() != offset for d in dates):
        raise ValueError("timestamp offset differs from file metadata; DST needs explicit offsets")
    dates = [d.astimezone(timezone.utc) for d in dates]
    seconds = np.array([(d-dates[0]).total_seconds() for d in dates])
    if len(seconds) < 2 or not np.all(np.diff(seconds) == 3600):
        raise ValueError("expected consecutive hourly timestamps")
    vals = {k: np.asarray(h[k], float) for k in expected if k != "time"}
    if any(v.shape != seconds.shape or not np.all(np.isfinite(v)) for v in vals.values()):
        raise ValueError("missing, nonfinite or mismatched hourly forcing")
    if np.any(vals["wind_speed_10m"] < 0) or np.any(vals["shortwave_radiation"] < 0):
        raise ValueError("negative wind or radiation")
    if np.any((vals["cloud_cover"] < 0) | (vals["cloud_cover"] > 100)):
        raise ValueError("cloud cover outside percent range")
    t = np.unique(np.r_[np.arange(0, seconds[-1], dt_s), seconds])
    interp = lambda key: np.interp(t, seconds, vals[key])
    # The next hourly endpoint labels the mean for each supported subinterval.
    ghi = vals["shortwave_radiation"][np.searchsorted(seconds, t, side="left")]
    ghi[0] = 0.0  # no interval precedes the initial state in this calculation
    w = {
        "t_s": t, "start_utc": dates[0].isoformat(),
        "time_labels": [d.isoformat() for d in dates],
        "t_air": interp("temperature_2m"), "t_dew": interp("dew_point_2m"),
        "wind10": interp("wind_speed_10m"), "ghi": ghi,
        "opaque_fraction_assumed": opaque_fraction,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "lat": raw["latitude"], "lon": raw["longitude"],
        "timezone": raw["timezone"], "utc_offset_seconds": raw["utc_offset_seconds"],
        "source_energy_j_m2": float(np.sum(vals["shortwave_radiation"][1:]) * 3600),
    }
    w["t_sky"] = sky_temperature_c(w["t_air"], w["t_dew"], opaque_fraction)
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


def simulate(vid, weather, p):
    """Sensor temperature over time for one variant. ``p`` values may be scalars
    or 1-D arrays (one per Monte Carlo sample). Returns (n_steps, n_samples)."""
    q = _params_for(vid, p)
    times = np.asarray(weather["t_s"], float)
    if len(times) < 2 or not np.all(np.isfinite(times)) or np.any(np.diff(times) <= 0):
        raise ValueError("simulation timestamps must strictly increase")
    if np.any(np.asarray(q["c"]) <= 0):
        raise ValueError("thermal capacity must be positive")
    n_steps = len(times)
    shape = np.broadcast(*[np.asarray(val) for val in p.values()]).shape or (1,)
    t = np.full(shape, weather["t_air"][0] + 273.15)
    out = np.empty((n_steps,) + shape)
    out[0] = t - 273.15
    for k in range(1, n_steps):
        dt_s = times[k] - times[k-1]
        midpoint = lambda key: (weather[key][k-1] + weather[key][k]) / 2
        t_air = midpoint("t_air") + 273.15
        if "opaque_fraction_assumed" in weather:
            t_sky = sky_temperature_c(t_air-273.15, midpoint("t_dew"),
                                     weather["opaque_fraction_assumed"]) + 273.15
        else:
            t_sky = midpoint("t_sky") + 273.15
        g = weather["ghi"][k]
        if q["forced_h"] is not None:
            h_eff = q["forced_h"]
            wind_eff = FORCED_EQUIV_WIND
        else:
            wind_eff = midpoint("wind10") * p["wind_height_factor"]
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
        # Exact integration of the local tangent ODE, including the zero-loss limit.
        rate = -dnet / q["c"]
        gain = np.full_like(np.asarray(rate, float), dt_s)
        np.divide(-np.expm1(-rate * dt_s), rate, out=gain, where=rate != 0)
        t = t + net / q["c"] * gain
        out[k] = t - 273.15
    return out


def draw(n, seed=SEED):
    rng = np.random.default_rng(seed)
    return {k: rng.uniform(lo, hi, n) for k, (lo, hi, *_rest) in PRIORS.items()}


def i1_sensitivity(wind_values=(0.5, 1.0, 2.0, 3.0), t_air_c=20.0):
    """Finite 1 W secant in effective sensor-coupled heat under steady shade.

    This uses the steady model's sky assumption, not the weather-driven sky.
    Electrical supply power needs an identified heat path before comparison.
    """
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
            rows.append({"wind_m_s": w, "finite_secant_c_per_effective_w": round(t1 - t0, 6)})
        out[v.vid] = rows
    return out


def summarise(weather, runs, spin_up_h=SPIN_UP_H, bias_inputs=False):
    """Duration-weighted interval means; peaks only for complete retained days.

    Day bins start at the file's initial timestamp (local midnight for this file).
    Retain partial-day intervals in means but exclude their peaks from daily means.
    """
    t = weather["t_s"]
    cut = spin_up_h * 3600
    keep = t[:-1] >= cut
    if not np.any(keep):
        raise ValueError("no intervals remain after spin-up")
    duration = np.diff(t)[keep]
    g = weather["ghi"][1:][keep]
    masks = {"daytime": g > 50.0, "night": g == 0.0}
    days = []
    for left in np.arange(cut, t[-1], 86400):
        if left + 86400 <= t[-1]:
            days.append((t >= left) & (t <= left + 86400))
    pct = lambda a: [float(x) for x in np.percentile(a, [5, 50, 95])]
    summary = {}
    for vid, temp in runs.items():
        bias = temp if bias_inputs else temp - weather["t_air"][:, None]
        midpoint_bias = ((bias[:-1] + bias[1:]) / 2)[keep]
        row = {}
        for name, mask in masks.items():
            row[name + "_mean_bias_c_p05_p50_p95"] = (
                pct(np.average(midpoint_bias[mask], axis=0, weights=duration[mask]))
                if np.any(mask) else None)
        row["complete_day_mean_peak_bias_c_p05_p50_p95"] = (
            pct(np.mean([bias[mask].max(axis=0) for mask in days], axis=0)) if days else None)
        summary[vid] = row
    return summary


def make_figure(weather, runs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter, DayLocator
    start = np.searchsorted(weather["t_s"], SPIN_UP_H * 3600)
    dates = [datetime.fromisoformat(weather["start_utc"]) + timedelta(seconds=float(t))
             for t in weather["t_s"][start:]]
    fig, (solar_ax, wind_ax, bias_ax) = plt.subplots(
        3, 1, figsize=(11, 8.5), sharex=True,
        gridspec_kw={"height_ratios": [1, 1, 2.4]})
    solar_ax.step(dates, weather["ghi"][start:], where="pre", color="#d08c00", lw=1.2)
    wind_ax.plot(dates, weather["wind10"][start:], color="#4a6fa5", lw=1.2)
    solar_ax.set_ylabel("Solar [W/m²]")
    wind_ax.set_ylabel("Wind, 10 m [m/s]")
    solar_ax.set_title("A  Global horizontal irradiance | preceding-hour means", fontsize=11, loc="left")
    wind_ax.set_title("B  Wind speed | instantaneous forcing", fontsize=11, loc="left")
    # Variant colours and markers match the steady figure; lines add redundancy.
    colors = {"V0": "#c0392b", "V0P": "#7d3c98", "V1": "#2980b9", "V2": "#27ae60"}
    markers = {"V0": "o", "V0P": "s", "V1": "^", "V2": "D"}
    styles = {"V0": "-", "V0P": "--", "V1": "-.", "V2": ":"}
    names = {v.vid: v.name for v in build_variants()}
    for i, (vid, temp) in enumerate(runs.items()):
        bias = temp[start:] - weather["t_air"][start:, None]
        lo, mid, hi = np.percentile(bias, [5, 50, 95], axis=1)
        bias_ax.fill_between(dates, lo, hi, color=colors[vid], alpha=0.16, lw=0)
        bias_ax.plot(dates, mid, color=colors[vid], lw=1.2, ls=styles[vid],
                     marker=markers[vid], markersize=3, markevery=(i * 180, 720),
                     label=f"{vid} {names[vid]}")
    for ax in (solar_ax, wind_ax, bias_ax):
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#e5e7eb", lw=0.7)
        ax.spines[["top", "right"]].set_visible(False)
    solar_ax.set_ylim(bottom=0)
    wind_ax.set_ylim(bottom=0)
    bias_ax.axhline(0, color="#555555", lw=0.8)
    bias_ax.set_ylabel("Sensor minus air [°C]")
    bias_ax.set_xlabel("Timestamp [UTC]; final day incomplete")
    bias_ax.xaxis.set_major_locator(DayLocator(interval=2, tz=timezone.utc))
    bias_ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d", tz=timezone.utc))
    bias_ax.set_title("C  SIMULATION | Clear-sky assumption, median and 5–95% input sensitivity",
                      fontsize=11, loc="left", pad=49)
    bias_ax.legend(fontsize=9, ncol=2, loc="lower left", bbox_to_anchor=(0, 1.015),
                   borderaxespad=0, frameon=False, handlelength=3)
    fig.suptitle("Preserved hourly Open-Meteo forcing and thermal response", fontsize=13, y=0.985)
    fig.text(0.5, 0.95, "Acquisition request, product and retrieval date unknown; sky forcing unmeasured.",
             ha="center", fontsize=10)
    fig.text(0.5, 0.015, "Bands: assumed-input sensitivity, not confidence intervals. No measured comparison.",
             ha="center", fontsize=10)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.88, hspace=0.75)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, facecolor="white")
    if out.suffix.lower() != ".svg":
        fig.savefig(out.with_suffix(".svg"), facecolor="white", metadata={"Date": None})
    svg = out.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", type=int, default=N_SAMPLES)
    ap.add_argument("--json", default=str(OUT_JSON))
    ap.add_argument("--figure", default=str(OUT_FIG))
    ap.add_argument("--no-figure", action="store_true")
    args = ap.parse_args()
    if args.samples < 1:
        ap.error("--samples must be positive")

    weather = load_weather()
    p = draw(args.samples)
    vids = ("V0", "V0P", "V1", "V2")
    runs = {vid: simulate(vid, weather, p) for vid in vids}
    nominal = {vid: simulate(vid, weather, {k: np.array([v]) for k, v in NOMINAL.items()}) for vid in vids}

    opaque_weather = load_weather(opaque_fraction=1.0)
    opaque_runs = {vid: simulate(vid, opaque_weather, NOMINAL) for vid in vids}
    duration = float(weather["t_s"][-1] - SPIN_UP_H * 3600)
    # Shared draws define a paired contrast, without a population probability claim.
    paired = {"V1_minus_V0P_signed_bias": runs["V1"] - runs["V0P"]}
    result = {
        "status": "CORRECTED SENSITIVITY CALCULATION; parent review HOLD; no thermal co-location data",
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "model_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": "analysis/thermal_transient.py (steady balance of thermal_bias.py plus one thermal mass per variant)",
        "weather": {
            "file": str(WEATHER.relative_to(ROOT)), "sha256": weather["sha256"],
            "provider": "Open-Meteo historical weather archive (CC BY 4.0)",
            "grid_point_lat_lon": [weather["lat"], weather["lon"]],
            "period_utc": [weather["time_labels"][0], weather["time_labels"][-1]],
            "source_timezone": weather["timezone"],
            "acquisition_request": None, "retrieved_at": None, "product_version": None,
            "provenance_status": "Unavailable in preserved files; no reconstruction from current API defaults",
            "definitions_source": WEATHER_SOURCE,
            "license_source": "https://open-meteo.com/en/terms",
            "radiation_rule": "ghi[k] held on preceding interval; first source solar hour excluded",
            "source_energy_j_m2": weather["source_energy_j_m2"],
            "integrated_energy_j_m2": float(np.dot(weather["ghi"][1:], np.diff(weather["t_s"]))),
        },
        "integration": {"dt_s": DT_S, "spin_up_h": SPIN_UP_H, "method": "local exponential tangent step; midpoint instantaneous forcing; actual intervals"},
        "sky": {"source": SKY_SOURCE, "equation": "Clark & Allen clear sky with Walton opaque correction",
                "opaque_fraction_in_primary_run": 0.0,
                "alternative_nominal_opaque_fraction": 1.0,
                "interpretation": "two assumed sky scenarios; total cloud is not opaque cloud; neither is measured sky forcing or a guaranteed bound"},
        "time_support": {"retained_duration_h": duration/3600,
                         "complete_days_for_peaks": int(duration//86400),
                         "partial_day_h_in_means_only": (duration % 86400)/3600,
                         "mean_rule": "trapezoidal node bias weighted by interval duration; daytime GHI>50 W/m2, night GHI=0; twilight excluded from both",
                         "peak_rule": "mean of node-sampled signed peaks over complete retained days; bins start at source local midnight",
                         "instantaneous_forcing": "linear interpolation between hourly records, evaluated at interval midpoint"},
        "monte_carlo": {"samples": args.samples, "seed": SEED, "distribution": "independent uniform parameters, shared draws across variants; sensitivity only"},
        "priors": {k: {"low": lo, "high": hi, "applies_to": list(app), "note": note}
                   for k, (lo, hi, app, note) in PRIORS.items()},
        "nominal": NOMINAL,
        "bias_summary": summarise(weather, runs),
        "nominal_summary": summarise(weather, nominal),
        "nominal_opaque_sky_scenario": summarise(opaque_weather, opaque_runs),
        "paired_signed_contrast": summarise(weather, paired, bias_inputs=True),
        "paired_contrast_definition": "V1 minus V0P signed bias in each shared draw; sign is not absolute-error superiority; quantiles are assumed-input sensitivity",
        "i1_finite_secant_shade": {"effective_heat_increment_w": 1.0,
                                   "sky_assumption_source": "analysis/thermal_bias.py:ASSUMPTIONS:T_sky_offset",
                                   "values": i1_sensitivity()},
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
    print("I1 (nominal, shade):", result["i1_finite_secant_shade"])


if __name__ == "__main__":
    main()
