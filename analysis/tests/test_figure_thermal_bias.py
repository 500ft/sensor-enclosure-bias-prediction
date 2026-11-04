"""The steady figure's plot data is the swept model; MATLAB draws it and its words live in the caption."""
import csv
import unittest

import numpy as np

from analysis import thermal_bias as tb
from analysis.tests.figure_checks import FIGURES, ROOT, check_matlab_outputs, squash

DATA = ROOT / tb.FIGURE_DATA


def sweep():
    """The sweep that main() plots, with its default arguments."""
    t_air, rh = float(tb._a("T_air")), float(tb._a("RH_air"))
    variants = tb.build_variants()
    res = tb.run_sweep(variants, np.linspace(0.0, 5.0, 51), [800.0, 1000.0], t_air, rh,
                       t_air - float(tb._a("T_sky_offset")), float(tb._a("h_free_floor")),
                       float(tb._a("h_wind_slope")))
    return res, variants, t_air, rh


class SteadyFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res, cls.variants, cls.t_air, cls.rh = sweep()
        cls.rows = list(csv.DictReader(DATA.read_text().splitlines()))

    def test_plot_data_is_the_default_sweep(self):
        self.assertEqual(len(self.rows), 2 * 51 * 4)
        expected = list(tb.figure_rows(self.res, self.variants))
        for row, want in zip(self.rows, expected):
            self.assertEqual(list(row.values())[:4], want[:4])
            np.testing.assert_allclose([float(row["delta_t_degc"]), float(row["rh_err_pct"])],
                                       [float(want[4]), float(want[5])], rtol=0, atol=2e-6)

    def test_plot_data_carries_the_committed_table_values(self):
        table = list(csv.DictReader(
            (ROOT / "analysis/output/thermal_bias_table.csv").read_text().splitlines()[1:]))
        self.assertEqual(len(table), 40)
        index = {(r["g_w_m2"], float(r["wind_m_s"]), r["variant_id"]): r for r in self.rows}
        for row in table:
            plotted = index[row["g_w_m2"], float(row["wind_m_s"]), row["variant_id"]]
            for key in ("delta_t_degc", "rh_err_pct"):
                self.assertEqual(f"{float(plotted[key]):.4f}", row[key])

    def test_matlab_figure_files(self):
        check_matlab_outputs(self, "thermal_bias", "make_thermal_bias.m",
                             ["thermal_bias_sweep.csv", "thermal_bias_table.csv"])

    def test_caption_matches_file_and_documents(self):
        text = tb.figure_caption(self.res, self.variants, self.t_air, self.rh)
        self.assertEqual(text, (FIGURES / "thermal_bias.caption.md").read_text().strip())
        self.assertIn("6 to 23 °C warm", text)
        for doc in ("README.md", "docs/results.md"):
            self.assertIn(squash(text), squash((ROOT / doc).read_text()), doc)
            self.assertIn("thermal_bias.caption.md", (ROOT / doc).read_text(), doc)


if __name__ == "__main__":
    unittest.main()
