"""Reproduce PR #56 numerical checks on the actual preserved weather file.

This checks numerical consistency, not model accuracy at the rig. The reported
refinement is nominal plus two joint range corners, not exhaustive uncertainty.
Run: python -m analysis.verify_thermal_transient --out <fresh-path>.json
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from analysis import thermal_transient as tt
from analysis.thermal_bias import build_variants, reported_rh_at_warm_sensor


def verify():
    times = np.array([0., 7., 31., 80., 81., 135., 300., 901.])
    w = {'t_s': times, 't_air': np.full(len(times), 20.),
         't_sky': np.full(len(times), 20.), 'wind10': np.ones(len(times)),
         'ghi': np.where(times > 80, 500., 0.)}
    p = dict(tt.NOMINAL, eps=0., q_int_box_w=0.)
    v = build_variants()[0]
    conductance = (p['h_floor'] + p['h_slope']*p['wind_height_factor'])*v.a_conv
    heat = p['alpha_dark']*500*v.a_proj
    exact = 20 + heat/conductance * (1-np.exp(-conductance*np.maximum(times-80, 0)/p['c_box_j_per_k']))
    rc_error = float(np.max(np.abs(tt.simulate('V0', w, p)[:, 0]-exact)))
    params = {k: np.array([tt.NOMINAL[k], lo, hi]) for k, (lo, hi, *_rest) in tt.PRIORS.items()}
    comparisons = {}
    energies = {}
    for opaque in (0., 1.):
        results = {}
        for step in (60., 30., 15., 7.5):
            weather = tt.load_weather(dt_s=step, opaque_fraction=opaque)
            runs = {vid: tt.simulate(vid, weather, params) for vid in ('V0', 'V0P', 'V1', 'V2')}
            results[step] = tt.summarise(weather, runs)
            energies[str(step)] = float(np.dot(weather['ghi'][1:], np.diff(weather['t_s']))
                                        - weather['source_energy_j_m2'])
        comparisons[str(opaque)] = {}
        for step in (60., 30., 15.):
            per_variant = {}
            for vid, summary in results[step].items():
                per_variant[vid] = max(abs(a-b) for metric, row in summary.items()
                                      for a,b in zip(row, results[7.5][vid][metric]))
            comparisons[str(opaque)][str(step)] = per_variant
    worst = max(max(row.values()) for scenario in comparisons.values() for step,row in scenario.items()
                if step == str(tt.DT_S))
    # A software reporting-resolution check, not an application acceptance limit.
    numerical_budget_c = 0.01
    assert rc_error < 1e-10
    assert max(abs(v) for v in energies.values()) < 1e-5
    assert worst < numerical_budget_c, (worst, numerical_budget_c)
    return {
        'status': 'executed numerical consistency checks; no physical validation',
        'model_sha256': hashlib.sha256(Path(tt.__file__).read_bytes()).hexdigest(),
        'weather_sha256': hashlib.sha256(tt.WEATHER.read_bytes()).hexdigest(),
        'rc_step': {'equation': 'C*dtheta/dt + G*theta = effective_heat_step',
                    'conductance_w_per_k': conductance, 'capacity_j_per_k': p['c_box_j_per_k'],
                    'heat_step_w': heat, 'times_s': times.tolist(), 'max_abs_error_c': rc_error},
        'radiation_energy_error_j_m2_by_step_s': energies,
        'refinement': {'reference_step_s': 7.5, 'cases': 'nominal and joint all-low/all-high input corners, both opaque-sky assumptions',
                       'metric': 'maximum difference across reported mean/peak quantiles for these three deterministic cases',
                       'differences_c_by_opaque_fraction_and_step_s': comparisons,
                       'selected_step_s': tt.DT_S, 'max_selected_difference_c': worst,
                       'numerical_reporting_budget_c': numerical_budget_c,
                       'limit': 'finite refinement against a finer discretization, not an exact nonlinear reference or exhaustive parameter-space proof'},
        'rh_sensitivity': {'assumption': 'fixed water-vapor partial pressure; no moisture source, sink or condensation',
                           'formula': 'RH_sensor = RH_air * e_sat(T_air) / e_sat(T_sensor)',
                           'source': 'analysis/thermal_bias.py:reported_rh_at_warm_sensor',
                           'rows': [{'air_c': 20., 'true_rh_pct': rh, 'warming_k': delta,
                                     'rh_error_percentage_points': reported_rh_at_warm_sensor(rh, 20., 20.+delta)-rh}
                                    for rh in (50., 80.) for delta in (0.5, 1.)],
                           'interpretation': 'thermal sensitivity only; no application tolerance or universal PM correction benefit'},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = verify()
    Path(args.out).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'rc_error_c': result['rc_step']['max_abs_error_c'],
                      'selected_step_summary_difference_c': result['refinement']['max_selected_difference_c']}))


if __name__ == '__main__':
    main()
