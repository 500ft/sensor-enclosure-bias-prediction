"""The steady intervals regenerate byte-identically, match the committed tables and the declared ranges."""
import json
import tempfile
import unittest
from pathlib import Path

from analysis import steady_uncertainty as su
from analysis.thermal_transient import PRIORS

ROOT = Path(__file__).resolve().parents[2]


class SteadyUncertaintyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.result = su.propagate()

    def test_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as d:
            su.write(self.rows, self.result, Path(d) / "u.csv", Path(d) / "u.json")
            self.assertEqual((Path(d) / "u.csv").read_text(), su.OUT_CSV.read_text())
            self.assertEqual((Path(d) / "u.json").read_text(), su.OUT_JSON.read_text())

    def test_nominal_columns_equal_the_committed_tables(self):
        for table, path in (("day", su.DAY_TABLE), ("night", su.NIGHT_TABLE)):
            committed = su.read_table(path)
            mine = [r for r in self.rows if r["table"] == table]
            self.assertEqual(len(mine), len(committed))
            for a, b in zip(mine, committed):
                for key in ("g_w_m2", "wind_m_s", "variant_id", "delta_t_degc", "rh_err_pct"):
                    self.assertEqual(a[key], b[key], (table, key))

    def test_standard_uncertainty_is_rectangular_from_the_declared_range(self):
        for m in self.result["inputs"]:
            low, high, applies_to, _ = PRIORS[m["name"]]
            self.assertEqual((m["low"], m["high"], m["applies_to"]), (low, high, list(applies_to)))
            self.assertAlmostEqual(m["u"], (high - low) / 12 ** 0.5, places=12)
        self.assertEqual({m["name"] for m in self.result["inputs"]} | set(su.TRANSIENT_ONLY), set(PRIORS))

    def test_inputs_that_do_not_apply_have_no_sensitivity(self):
        inputs, _ = su.declared_inputs()
        for vid in su.VIDS:
            c = su.sensitivities(vid, 1000.0, 0.5, inputs)
            self.assertEqual(set(c), {x.name for x in inputs if vid in PRIORS[x.name][2]})
        night = su.sensitivities("V1", 0.0, 0.5, inputs)  # no sun: solar inputs cannot move the answer
        for name in ("solar_factor", "alpha_light", "preheat_calm_k"):
            self.assertAlmostEqual(night[name], 0.0, places=9, msg=name)

    def test_combined_uncertainty_is_the_quadrature_sum_and_the_contrast_cancels_shared_inputs(self):
        budgets = self.result["headline_point"]["budgets"]
        for budget in budgets.values():
            self.assertAlmostEqual(budget["u_c_degc"] ** 2, sum(budget["variance_terms_k2"].values()), places=10)
        inputs, _ = su.declared_inputs()
        u = {x.name: x.u for x in inputs}
        c0, c1 = budgets["V0P"]["sensitivity_per_unit"], budgets["V1"]["sensitivity_per_unit"]
        expected = sum(((c0.get(n, 0.0) - c1.get(n, 0.0)) * u[n]) ** 2 for n in u) ** 0.5
        contrast = self.result["headline_point"]["v0p_minus_v1"]
        self.assertAlmostEqual(contrast["u_c_degc"], expected, places=10)
        naive = (budgets["V0P"]["u_c_degc"] ** 2 + budgets["V1"]["u_c_degc"] ** 2) ** 0.5
        self.assertLess(contrast["u_c_degc"], naive)

    def test_recorded_finding_at_the_headline_point(self):
        contrast = self.result["headline_point"]["v0p_minus_v1"]
        self.assertEqual((contrast["g_w_m2"], contrast["wind_m_s"]), su.HEADLINE)
        self.assertTrue(contrast["intervals_overlap"])
        self.assertTrue(contrast["includes_zero"])
        self.assertTrue(all(c["includes_zero"] and c["intervals_overlap"] for c in self.result["contrasts_day"]))

    def test_results_table_repeats_the_files(self):
        text = (ROOT / "docs/results.md").read_text()
        by = {(r["g_w_m2"], r["wind_m_s"], r["variant_id"]): r for r in self.rows if r["table"] == "day"}
        contrasts = {c["wind_m_s"]: c for c in self.result["contrasts_day"] if c["g_w_m2"] == 1000.0}
        for wind in ("0.0", "0.5", "1.0", "2.0", "5.0"):
            cells = []
            for vid in ("V0", "V0P", "V1", "V2"):
                r = by["1000", wind, vid]
                cells.append(f"{float(r['delta_t_degc']):.2f} ({float(r['low_k2_degc']):.2f} to {float(r['high_k2_degc']):.2f})")
            c = contrasts[float(wind)]
            cells.append(f"{c['v0p_minus_v1_degc']:.2f} ({c['low_k2_degc']:.2f} to {c['high_k2_degc']:.2f})")
            row = f"| {wind} | " + " | ".join(cells) + " |"
            self.assertIn(row, text, row)
        self.assertIn("thermal_bias_uncertainty.csv", text)
        self.assertIn("thermal_bias_uncertainty.json", text)


if __name__ == "__main__":
    unittest.main()
