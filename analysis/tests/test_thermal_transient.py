import unittest

import numpy as np

from analysis import thermal_transient as tt
from analysis.thermal_bias import _a, build_variants, h_external, solve_surface_temperature


def constant_weather(t_air, t_sky, wind10, ghi, hours=12):
    t = np.arange(0.0, hours * 3600.0, tt.DT_S)
    n = len(t)
    return {"t_s": t, "t_air": np.full(n, t_air), "t_sky": np.full(n, t_sky),
            "wind10": np.full(n, wind10), "ghi": np.full(n, ghi)}


class TransientMatchesSteady(unittest.TestCase):
    """With constant inputs the transient model must settle on the steady solver's answer."""

    def check(self, vid, ghi, wind10):
        p = {k: np.array([v]) for k, v in tt.NOMINAL.items()}
        # steady model uses wind at the sensor; give the transient model the same wind
        p["wind_height_factor"] = np.array([1.0])
        t_air, t_sky = 25.0, 5.0
        w = constant_weather(t_air, t_sky, wind10, ghi)
        final = tt.simulate(vid, w, p)[-1, 0]
        v = {x.vid: x for x in build_variants()}[vid]
        preheat = 0.0
        if v.solar_factor < 1.0:
            wind_eff = tt.FORCED_EQUIV_WIND if v.forced_h is not None else wind10
            preheat = 1.2 * 2.0 ** (-wind_eff / float(_a("preheat_wind_halflife"))) * (ghi / 1000.0)
        h = h_external(wind10, float(_a("h_free_floor")), float(_a("h_wind_slope")))
        steady = solve_surface_temperature(v, ghi, t_air, t_sky, h, air_preheat_k=preheat)
        self.assertAlmostEqual(final, steady, delta=1e-3, msg=f"{vid} G={ghi} wind={wind10}")

    def test_all_variants_day_and_night(self):
        for vid in ("V0", "V0P", "V1", "V2"):
            for ghi, wind in ((900.0, 0.5), (400.0, 2.0), (0.0, 1.0)):
                self.check(vid, ghi, wind)


class StableForSmallThermalMass(unittest.TestCase):
    def test_no_blow_up_with_time_step_longer_than_time_constant(self):
        p = {k: np.array([v]) for k, v in tt.NOMINAL.items()}
        p["c_shield_j_per_k"] = np.array([1.0])  # time constant of a few seconds, step is 60 s
        w = constant_weather(25.0, 5.0, 1.0, 900.0, hours=2)
        out = tt.simulate("V1", w, p)
        self.assertTrue(np.all(np.isfinite(out)))
        self.assertLess(np.ptp(out[-10:]), 1e-6)


class Reproducible(unittest.TestCase):
    def test_same_seed_same_draws(self):
        a, b = tt.draw(50), tt.draw(50)
        for k in a:
            np.testing.assert_array_equal(a[k], b[k])


class SkyTemperature(unittest.TestCase):
    def test_clear_sky_colder_than_overcast(self):
        clear = tt.sky_temperature_c(20.0, 10.0, 0.0)
        overcast = tt.sky_temperature_c(20.0, 10.0, 1.0)
        self.assertLess(clear, overcast)
        self.assertLess(overcast, 20.0 + 1e-9)

class TimeAndEnergyTests(unittest.TestCase):
    def test_initial_state_at_actual_first_timestamp(self):
        w = constant_weather(20, 20, 1, 0)
        for key in w:
            w[key] = w[key][:2]
        w['t_s'] = np.array([125., 185.])
        out = tt.simulate('V0', w, tt.NOMINAL)
        self.assertEqual(out[0, 0], 20.)
        self.assertGreater(out[1, 0], 20.)

    def test_exact_rc_power_equivalent_solar_step_on_irregular_intervals(self):
        # eps=0 removes radiation: C*d(theta)/dt + conductance*theta = Q.
        # Solar at the absorbing node supplies a known step in effective heat.
        times = np.array([0., 7., 31., 80., 81., 135., 300., 901.])
        w = {'t_s': times, 't_air': np.full(len(times), 20.),
             't_sky': np.full(len(times), 20.), 'wind10': np.ones(len(times)),
             'ghi': np.where(times > 80, 500., 0.)}
        p = dict(tt.NOMINAL, eps=0., q_int_box_w=0.)
        v = build_variants()[0]
        conductance = (p['h_floor'] + p['h_slope']*p['wind_height_factor'])*v.a_conv
        heat = p['alpha_dark']*500*v.a_proj
        exact = 20 + heat/conductance * (1-np.exp(-conductance*np.maximum(times-80, 0)/p['c_box_j_per_k']))
        np.testing.assert_allclose(tt.simulate('V0', w, p)[:, 0], exact, atol=2e-12, rtol=0)

    def test_zero_loss_limit_and_nonzero_start(self):
        times = np.array([90., 91., 108., 120.])
        w = {'t_s': times, 't_air': np.full(4, 20.), 't_sky': np.full(4, 20.),
             'wind10': np.zeros(4), 'ghi': np.zeros(4)}
        p = dict(tt.NOMINAL, eps=0., h_floor=0., h_slope=0.)
        exact = 20 + p['q_int_box_w']*(times-times[0])/p['c_box_j_per_k']
        np.testing.assert_allclose(tt.simulate('V0', w, p)[:, 0], exact, atol=2e-12, rtol=0)

    def test_real_hourly_energy_and_unaligned_steps(self):
        import json
        raw = json.loads(tt.WEATHER.read_text())
        expected = sum(raw['hourly']['shortwave_radiation'][1:])*3600
        for step in (60., 137.):
            w = tt.load_weather(dt_s=step)
            self.assertAlmostEqual(np.dot(w['ghi'][1:], np.diff(w['t_s'])), expected, places=5)
            self.assertEqual(w['t_s'][0], 0)
            self.assertEqual(w['t_s'][-1], (len(raw['hourly']['time'])-1)*3600)
            self.assertEqual(w['time_labels'][0], '2026-09-01T04:00:00+00:00')
        # The first radiation hour is unsupported by instantaneous inputs.
        # Give it nonzero energy to make accidental inclusion observable.
        import tempfile
        raw['hourly']['shortwave_radiation'][0] = 9999.
        with tempfile.TemporaryDirectory() as d:
            path = tt.Path(d)/'weather.json'
            path.write_text(json.dumps(raw))
            boundary = tt.load_weather(path, dt_s=137.)
            self.assertAlmostEqual(np.dot(boundary['ghi'][1:], np.diff(boundary['t_s'])), expected, places=5)
        # A ramp source must stay a constant mean within each preceding hour.
        w = tt.load_weather(dt_s=137.)
        endpoints = np.searchsorted(np.arange(len(raw['hourly']['time']))*3600, w['t_s'][1:])
        np.testing.assert_array_equal(w['ghi'][1:], np.array(raw['hourly']['shortwave_radiation'])[endpoints])

    def test_bad_timestamps_and_units_rejected(self):
        import json
        import tempfile
        raw = json.loads(tt.WEATHER.read_text())
        with tempfile.TemporaryDirectory() as d:
            path = tt.Path(d)/'weather.json'
            raw['hourly_units']['wind_speed_10m'] = 'km/h'
            path.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, 'units'):
                tt.load_weather(path)
            raw['hourly_units']['wind_speed_10m'] = 'm/s'
            raw['hourly']['time'][1] = raw['hourly']['time'][0]
            path.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, 'consecutive'):
                tt.load_weather(path)
        w = constant_weather(20, 20, 1, 0)
        w['t_s'][1] = w['t_s'][0]
        with self.assertRaisesRegex(ValueError, 'strictly increase'):
            tt.simulate('V0', w, tt.NOMINAL)

    def test_duration_weighted_summary_and_partial_day(self):
        t = np.array([0., 1., 24., 30., 47.])*3600
        w = {'t_s': t, 't_air': np.zeros(5), 'ghi': np.ones(5)*100}
        bias = (t/3600)[:, None]
        row = tt.summarise(w, {'ramp': bias}, spin_up_h=0)['ramp']
        np.testing.assert_allclose(row['daytime_mean_bias_c_p05_p50_p95'], [23.5]*3)
        # Only the complete first day contributes a daily peak.
        np.testing.assert_allclose(row['complete_day_mean_peak_bias_c_p05_p50_p95'], [24.]*3)
        self.assertIsNone(row['night_mean_bias_c_p05_p50_p95'])

    def test_paired_signed_contrast_uses_shared_samples(self):
        t = np.array([0., 12., 24.])*3600
        w = {'t_s': t, 't_air': np.array([20., 21., 20.]), 'ghi': np.ones(3)*100}
        white = np.array([[22., 25.], [23., 26.], [22., 25.]])
        shield = white + np.array([-1., 2.])
        row = tt.summarise(w, {'contrast': shield-white}, spin_up_h=0, bias_inputs=True)['contrast']
        np.testing.assert_allclose(row['daytime_mean_bias_c_p05_p50_p95'], [-0.85, 0.5, 1.85])

    def test_nonlinear_step_converges_under_refinement(self):
        errors = []
        def solve(step):
            times = np.arange(0, 600+step/2, step)
            w = {'t_s': times, 't_air': np.full(len(times), 20.),
                 't_sky': np.full(len(times), 0.), 'wind10': np.ones(len(times)),
                 'ghi': np.full(len(times), 1000.)}
            return tt.simulate('V0', w, tt.NOMINAL)
        reference = solve(0.25)
        for step in (60., 30., 15.):
            result = solve(step)
            errors.append(np.max(np.abs(result-reference[::int(step/0.25)])))
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])

    def test_sky_reference_example(self):
        # EnergyPlus's published example: air20C, dew10C, N=0 gives eps about .815.
        sky = tt.sky_temperature_c(20., 10., 0.)
        emissivity = ((sky+273.15)/293.15)**4
        self.assertAlmostEqual(emissivity, 0.815, delta=0.0005)
        self.assertAlmostEqual(emissivity*5.6697e-8*293.15**4, 341.2, delta=0.1)


if __name__ == "__main__":
    unittest.main()
