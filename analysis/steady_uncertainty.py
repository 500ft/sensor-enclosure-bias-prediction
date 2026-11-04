#!/usr/bin/env python3
"""Propagate the declared input ranges through the steady bias model at the registered points.

Connects analysis/uncertainty.py (linear propagation, GUM 100:2008) to the steady
heat balance of analysis/thermal_bias.py. The input ranges are the ones the
repository already declares: the transient prediction's priors
(analysis/thermal_transient.py PRIORS, recorded in
analysis/output/thermal_transient_prediction.json) with their register rows in
docs/PARAMETER_REGISTER.csv. A declared range [low, high] is treated as a
rectangular distribution, so u = (high - low) / sqrt(12) (GUM 4.3.7).
Sensitivities are central finite differences of the bisection solver at the
nominal point. Inputs without a documented range (areas, fan coefficient,
pre-heat half-life) and the operating point (solar load, air temperature, RH,
wind, sky depression) are held fixed with u = 0 and listed as such.

Outputs:
  analysis/output/thermal_bias_uncertainty.csv   one row per committed day and night table row
  analysis/output/thermal_bias_uncertainty.json  input budget, per-point budgets at the headline
                                                 point and the V0P minus V1 contrast at each day point
The committed nominal tables are not rewritten; this script checks that its
nominal values equal them. SIMULATION OUTPUT, not a measurement: the intervals
describe sensitivity to declared ranges, not measured uncertainty, and the
k = 2 interval carries no coverage probability.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import replace
from pathlib import Path

from analysis import thermal_bias as tb
from analysis.thermal_transient import NOMINAL, PRIORS
from analysis.uncertainty import Input, combine

ROOT = Path(__file__).resolve().parents[1]
DAY_TABLE = ROOT / "analysis/output/thermal_bias_table.csv"
NIGHT_TABLE = ROOT / "analysis/output/thermal_bias_night_table.csv"
OUT_CSV = ROOT / "analysis/output/thermal_bias_uncertainty.csv"
OUT_JSON = ROOT / "analysis/output/thermal_bias_uncertainty.json"
K = 2.0                       # coverage factor; no coverage probability is claimed
STEP_FRACTION = 0.1           # finite-difference half step as a fraction of u
HEADLINE = (1000.0, 0.5)      # the README's operating point

# Register row for each declared range; the steady-model name it feeds.
REGISTER = {
    "alpha_dark": ("P-ALPHA-V0", "alpha_V0"), "alpha_light": ("P-ALPHA-SH", "alpha_shield"),
    "eps": ("P-EPS", "eps_surface"), "solar_factor": ("P-PHI", "shield_solar_factor"),
    "conv_boost": ("P-CBOOST", "shield_conv_boost"), "preheat_calm_k": ("P-PREHEAT", "shield_air_preheat_calm"),
    "q_int_box_w": ("P-QINT-V0", "Q_int_V0"), "q_int_shield_w": ("P-QINT-SH", "Q_int_shielded"),
    "f_sky_box": ("P-FSKY-V0", "f_sky_V0"), "f_sky_shield": ("P-FSKY-SH", "f_sky_shield"),
    "h_floor": ("P-HFLOOR", "h_free_floor"), "h_slope": ("P-HSLOPE", "h_wind_slope"),
}
TRANSIENT_ONLY = ("wind_height_factor", "c_box_j_per_k", "c_shield_j_per_k")
HELD_FIXED = [
    ("A_proj_V0", "P-APROJ-V0"), ("A_conv_V0", "P-ACONV-V0"), ("A_proj_shield", "P-APROJ-SH"),
    ("A_conv_shield", "P-ACONV-SH"), ("h_fan_V2", "P-HFAN"), ("preheat_wind_halflife", "P-PREHALF"),
    ("T_sky_offset", "P-TSKY"), ("T_air", "P-TAIR"), ("RH_air", "P-RHAIR"),
]
FIXED_REASON = {
    "P-APROJ-V0": "no documented range; lab-required geometry", "P-ACONV-V0": "no documented range; lab-required geometry",
    "P-APROJ-SH": "no documented range; lab-required geometry", "P-ACONV-SH": "no documented range; lab-required geometry",
    "P-HFAN": "no documented range", "P-PREHALF": "no documented range",
    "P-TSKY": "operating condition of the registered tables; the register's dewpoint-dependent 4 to 34 K range is a scenario choice, not an input interval at this point",
    "P-TAIR": "selected operating point", "P-RHAIR": "selected operating point",
}
VIDS = ("V0", "V0P", "V1", "V2")


def declared_inputs():
    """Input nodes from the declared ranges; shared names are one node across variants."""
    inputs, meta = [], []
    for name, (register_id, steady_name) in REGISTER.items():
        low, high, applies_to, note = PRIORS[name]
        nominal = NOMINAL[name]
        if nominal != float(tb._a(steady_name)):
            raise ValueError(f"{name}: transient nominal {nominal} differs from steady {steady_name}")
        if not low <= nominal <= high:
            raise ValueError(f"{name}: nominal outside its declared range")
        u = (high - low) / math.sqrt(12.0)
        inputs.append(Input(name=name, value=nominal, u=u, unit="mixed",
                            provenance=f"declared range {low} to {high} ({register_id}); rectangular", evaluation="B"))
        meta.append({"name": name, "register_id": register_id, "steady_name": steady_name, "nominal": nominal,
                     "low": low, "high": high, "u": u, "distribution": "rectangular",
                     "applies_to": list(applies_to), "note": note,
                     "one_sided_from_nominal": nominal in (low, high)})
    return inputs, meta


def steady_dt(vid, g, wind, p):
    """Sensor minus air [K] at one operating point, mirroring thermal_bias.run_sweep."""
    base = {v.vid: v for v in tb.build_variants()}[vid]
    box = vid in ("V0", "V0P")
    v = replace(base, alpha=p["alpha_dark"] if vid == "V0" else p["alpha_light"], eps=p["eps"],
                q_internal=p["q_int_box_w"] if box else p["q_int_shield_w"],
                f_sky=p["f_sky_box"] if box else p["f_sky_shield"],
                solar_factor=1.0 if box else p["solar_factor"],
                conv_boost=p["conv_boost"] if vid == "V1" else 1.0)
    t_air = float(tb._a("T_air"))
    t_sky = t_air - float(tb._a("T_sky_offset"))
    h = tb.h_external(wind, p["h_floor"], p["h_slope"])
    preheat = 0.0
    if not box:
        preheat = tb.shield_air_preheat(wind, p["preheat_calm_k"], float(tb._a("preheat_wind_halflife")),
                                        forced=v.forced_h is not None) * (g / 1000.0)
    return tb.solve_surface_temperature(v, g, t_air, t_sky, h, air_preheat_k=preheat) - t_air


def sensitivities(vid, g, wind, inputs):
    """Central finite differences dT/dx at the nominal point, for the inputs that apply to ``vid``."""
    nominal = {x.name: x.value for x in inputs}
    out = {}
    for x in inputs:
        if vid not in PRIORS[x.name][2]:
            continue
        step = STEP_FRACTION * x.u
        up, down = dict(nominal, **{x.name: x.value + step}), dict(nominal, **{x.name: x.value - step})
        out[x.name] = (steady_dt(vid, g, wind, up) - steady_dt(vid, g, wind, down)) / (2 * step)
    return out


def rh_slope(t_air, rh_true, t_sensor):
    """d(reported RH)/dT_sensor [pp per K] by central difference."""
    step = 1e-3
    return (tb.reported_rh_at_warm_sensor(rh_true, t_air, t_sensor + step)
            - tb.reported_rh_at_warm_sensor(rh_true, t_air, t_sensor - step)) / (2 * step)


def read_table(path):
    lines = path.read_text().splitlines()
    return list(csv.DictReader(lines[1:]))


def propagate():
    inputs, meta = declared_inputs()
    nominal = {x.name: x.value for x in inputs}
    t_air, rh_true = float(tb._a("T_air")), float(tb._a("RH_air"))
    rows, budgets, contrasts = [], {}, []
    for table, path in (("day", DAY_TABLE), ("night", NIGHT_TABLE)):
        committed = read_table(path)
        for r in committed:
            g, wind, vid = float(r["g_w_m2"]), float(r["wind_m_s"]), r["variant_id"]
            dt = steady_dt(vid, g, wind, nominal)
            if abs(dt - float(r["delta_t_degc"])) > 5e-5:
                raise ValueError(f"nominal mismatch at {table} {g} {wind} {vid}: {dt} vs {r['delta_t_degc']}")
            c = sensitivities(vid, g, wind, inputs)
            res = combine(inputs, c, unit="K", k=K)
            slope = rh_slope(t_air, rh_true, t_air + dt)
            rows.append({"table": table, "g_w_m2": r["g_w_m2"], "wind_m_s": r["wind_m_s"], "variant_id": vid,
                         "variant_name": r["variant_name"], "delta_t_degc": r["delta_t_degc"],
                         "u_c_degc": f"{res.u_c:.4f}", "low_k2_degc": f"{dt - res.U:.4f}",
                         "high_k2_degc": f"{dt + res.U:.4f}", "rh_err_pct": r["rh_err_pct"],
                         "u_c_rh_pct": f"{abs(slope) * res.u_c:.4f}"})
            if (g, wind) == HEADLINE:
                budgets[vid] = {"delta_t_degc": dt, "u_c_degc": res.u_c, "sensitivity_per_unit": c,
                                "variance_terms_k2": res.variance_terms, "rh_slope_pp_per_k": slope}
        if table == "day":
            points = sorted({(float(r["g_w_m2"]), float(r["wind_m_s"])) for r in committed})
            for g, wind in points:
                by = {vid: (steady_dt(vid, g, wind, nominal), sensitivities(vid, g, wind, inputs)) for vid in ("V0P", "V1")}
                diff = {x.name: by["V0P"][1].get(x.name, 0.0) - by["V1"][1].get(x.name, 0.0) for x in inputs}
                res = combine(inputs, {k: v for k, v in diff.items() if v}, unit="K", k=K)
                own = {vid: combine(inputs, by[vid][1], unit="K", k=K) for vid in by}
                nominal_diff = by["V0P"][0] - by["V1"][0]
                contrasts.append({
                    "g_w_m2": g, "wind_m_s": wind, "v0p_degc": by["V0P"][0], "v1_degc": by["V1"][0],
                    "v0p_minus_v1_degc": nominal_diff, "u_c_degc": res.u_c, "k": K,
                    "low_k2_degc": nominal_diff - res.U, "high_k2_degc": nominal_diff + res.U,
                    "includes_zero": nominal_diff - res.U <= 0.0 <= nominal_diff + res.U,
                    "v0p_interval_k2_degc": [by["V0P"][0] - own["V0P"].U, by["V0P"][0] + own["V0P"].U],
                    "v1_interval_k2_degc": [by["V1"][0] - own["V1"].U, by["V1"][0] + own["V1"].U],
                    "intervals_overlap": (by["V0P"][0] - own["V0P"].U <= by["V1"][0] + own["V1"].U
                                          and by["V1"][0] - own["V1"].U <= by["V0P"][0] + own["V0P"].U),
                    "variance_terms_k2": res.variance_terms})
    headline = next(c for c in contrasts if (c["g_w_m2"], c["wind_m_s"]) == HEADLINE)
    result = {
        "status": "SIMULATION; linear propagation of declared input ranges through the steady model; no measured uncertainty",
        "method": {"module": "analysis/uncertainty.py", "sensitivities": "central finite differences of the bisection solver "
                   f"at the nominal point, half step {STEP_FRACTION} u", "standard_uncertainty": "(high - low) / sqrt(12), rectangular",
                   "coverage_factor": K, "coverage_basis": None,
                   "coverage_note": "k = 2 without a demonstrated basis; the coverage probability is unspecified (GUM G.6.6 not shown)",
                   "contrast": "V0P minus V1 with shared inputs (alpha_light, eps, h_floor, h_slope) as one node each; "
                   "nonlinearity and one-sided ranges are not captured by the linear terms",
                   "nominal_check": "every nominal value equals the committed day and night tables within 5e-5 K"},
        "ranges_source": ["analysis/thermal_transient.py PRIORS", "analysis/output/thermal_transient_prediction.json priors",
                          "docs/PARAMETER_REGISTER.csv"],
        "inputs": meta,
        "not_steady_inputs": [{"name": n, "note": "transient-only range; no steady-model sensitivity"} for n in TRANSIENT_ONLY],
        "held_fixed": [{"name": n, "register_id": rid, "value": tb._a(n), "u": 0.0, "reason": FIXED_REASON[rid]} for n, rid in HELD_FIXED],
        "operating_point_fixed": {"G_clear_sky": "800, 1000 (day) and 0 (night) W/m^2", "wind": "0, 0.5, 1, 2, 5 m/s",
                                  "T_air_degc": t_air, "RH_air_pct": rh_true, "T_sky_offset_k": float(tb._a("T_sky_offset"))},
        "headline_point": {"g_w_m2": HEADLINE[0], "wind_m_s": HEADLINE[1], "budgets": budgets,
                           "v0p_minus_v1": headline},
        "contrasts_day": contrasts,
        "table_file": "analysis/output/thermal_bias_uncertainty.csv",
    }
    return rows, result


def write(rows, result, out_csv=OUT_CSV, out_json=OUT_JSON):
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["# SIMULATION -- linear propagation of declared input ranges; k = 2 interval with unspecified "
                    "coverage probability; see docs/results.md"])
        w.writerow(list(rows[0]))
        for r in rows:
            w.writerow(list(r.values()))
    Path(out_json).write_text(json.dumps(result, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=str(OUT_CSV))
    ap.add_argument("--json", default=str(OUT_JSON))
    args = ap.parse_args()
    rows, result = propagate()
    write(rows, result, args.csv, args.json)
    h = result["headline_point"]["v0p_minus_v1"]
    for vid, b in result["headline_point"]["budgets"].items():
        print(f"{vid}: {b['delta_t_degc']:.4f} K, u_c {b['u_c_degc']:.4f} K")
    print(f"V0P minus V1 at {HEADLINE}: {h['v0p_minus_v1_degc']:.4f} K, u_c {h['u_c_degc']:.4f} K, "
          f"k=2 interval [{h['low_k2_degc']:.4f}, {h['high_k2_degc']:.4f}], includes zero: {h['includes_zero']}, "
          f"intervals overlap: {h['intervals_overlap']}")
    print(f"[table] wrote {args.csv}\n[json] wrote {args.json}")


if __name__ == "__main__":
    main()
