"""The steady figure shows only the swept model values; its words live in the caption."""
import csv
import unittest

import numpy as np

from analysis import figure_style as fs
from analysis import thermal_bias as tb
from analysis.tests.figure_checks import ROOT, axis_text, printed, squash

import matplotlib.pyplot as plt  # noqa: E402  (figure_style selects the Agg backend)


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
        cls.fig = tb.build_figure(cls.res, cls.variants)

    @classmethod
    def tearDownClass(cls):
        plt.close(cls.fig)

    def test_lines_carry_the_committed_table_values(self):
        rows = list(csv.DictReader(
            (ROOT / "analysis/output/thermal_bias_table.csv").read_text().splitlines()[1:]))
        self.assertEqual(len(rows), 40)
        axes = np.array(self.fig.axes).reshape(2, len(fs.VARIANT_ORDER))
        for row in rows:
            col = fs.VARIANT_ORDER.index(row["variant_id"])
            ls = "-" if row["g_w_m2"] == "1000" else "--"
            for r, key in enumerate(("delta_t_degc", "rh_err_pct")):
                (line,) = [l for l in axes[r, col].lines if l.get_linestyle() == ls
                           and l.get_marker() == fs.VARIANT_MARKERS[row["variant_id"]]]
                i = int(np.flatnonzero(np.isclose(line.get_xdata(), float(row["wind_m_s"])))[0])
                self.assertEqual(f"{line.get_ydata()[i]:.4f}", row[key])

    def test_canvas_holds_only_axes_text_panel_letters_and_legend(self):
        allowed = axis_text(self.fig) | {f"({c})" for c in fs.LETTERS[:8]}
        self.assertLessEqual(printed(self.fig), allowed, printed(self.fig) - allowed)

    def test_nothing_printed_touches_anything(self):
        self.assertEqual(fs.audit(self.fig), [])

    def test_caption_matches_file_and_documents(self):
        text = tb.figure_caption(self.res, self.variants, self.t_air, self.rh)
        self.assertEqual(text, (ROOT / "analysis/figures/thermal_bias.caption.md").read_text().strip())
        self.assertIn("6 to 23 °C warm", text)
        for doc in ("README.md", "docs/results.md"):
            self.assertIn(squash(text), squash((ROOT / doc).read_text()), doc)
            self.assertIn("thermal_bias.caption.md", (ROOT / doc).read_text(), doc)


if __name__ == "__main__":
    unittest.main()
