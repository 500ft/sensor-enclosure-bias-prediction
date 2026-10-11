"""Numerical checks for the executed synthetic design study, no rig claims."""
import unittest
import numpy as np
from analysis import synthetic_identifiability as study


class SyntheticIdentifiabilityTests(unittest.TestCase):
    def test_independent_physics_checks(self):
        result = study.validation()
        self.assertLess(result['interval_energy_max_j'], 1e-10)

    def test_profile_matches_direct_gls_and_recovers_noiseless_ratios(self):
        t, p = study.schedule(3600, 15, [0, 1, 0, 1], .5)
        taus = np.array([300., 600., 1200.])
        slope = .2/3600
        y = study.generate(t, p, t*slope, 600, 3, .15)-t*slope+.1+.03*t/t[-1]
        bank = study.fit_bank(t, p, taus, .04, .8, slope)
        scores, gains, _ = study.profile(bank, y[:, None], .04, .8, [0, 15])
        for i, tau in enumerate(taus):
            e = np.exp(-t/tau)
            columns = np.column_stack([study.step_basis(t, p, [tau])[0], np.ones(len(t)), e, t/t[-1]])
            a = study.whiten(columns.T, .04, .8).T
            b = study.whiten(y+slope*tau*(1-e), .04, .8)
            coeff = np.linalg.lstsq(a, b, rcond=None)[0]
            direct = np.sum((a@coeff-b)**2)
            self.assertAlmostEqual(scores[i, 0], direct, places=7)
            self.assertAlmostEqual(gains[i, 0], coeff[0], places=8)
        self.assertEqual(int(np.argmin(scores)), 1)
        self.assertAlmostEqual(gains[1, 0], 3, places=10)

    def test_disconnected_and_open_sets_preserved(self):
        sets = study.segments(np.arange(1., 8.), np.array([0., 0., 8., 9., 8., 0., 0.]), 4)
        self.assertEqual(len(sets), 2)
        self.assertTrue(sets[0]['open_low'])
        self.assertTrue(sets[1]['open_high'])
        self.assertFalse(study.contains(sets, 4))

    def test_power_schedules_have_equal_energy(self):
        import json
        cfg = json.loads(study.CONFIG.read_text())
        for duration in cfg['duration_s']:
            energies = []
            for levels in cfg['schedules'].values():
                t, p = study.schedule(duration, cfg['dt_s'], levels, cfg['power_w'])
                self.assertTrue(np.allclose(np.diff(t), cfg['dt_s']))
                energies.append(np.sum(p*np.diff(t)))
            self.assertAlmostEqual(energies[0], energies[1])


if __name__ == '__main__':
    unittest.main()
