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


if __name__ == "__main__":
    unittest.main()
