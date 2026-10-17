"""The transient figure plots the stored weather and the draws behind the stored summary."""
import json
import unittest

import numpy as np

from analysis import figure_style as fs
from analysis import thermal_transient as tt
from analysis.tests.figure_checks import ROOT, axis_text, printed, squash

import matplotlib.pyplot as plt  # noqa: E402

VIDS = ("V0", "V0P", "V1", "V2")


class TransientFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The registered 400-draw run, about 10 s; the result JSON keeps only its summaries.
        cls.weather = tt.load_weather()
        draws = tt.draw(tt.N_SAMPLES)
        cls.runs = {vid: tt.simulate(vid, cls.weather, draws) for vid in VIDS}
        cls.fig = tt.build_figure(cls.weather, cls.runs)

    @classmethod
    def tearDownClass(cls):
        plt.close(cls.fig)

    def test_plotted_draws_reproduce_the_stored_summary(self):
        stored = json.loads((ROOT / "analysis/output/thermal_transient_prediction.json").read_text())
        self.assertEqual(stored["monte_carlo"]["samples"], tt.N_SAMPLES)
        self.assertEqual(stored["monte_carlo"]["seed"], tt.SEED)
        again = tt.summarise(self.weather, self.runs)
        for vid in VIDS:
            for key, values in stored["bias_summary"][vid].items():
                np.testing.assert_allclose(again[vid][key], values, rtol=1e-9, atol=1e-12)

    def test_panels_plot_weather_file_and_draw_medians(self):
        start = np.searchsorted(self.weather["t_s"], tt.SPIN_UP_H * 3600)
        solar, wind, *bias = self.fig.axes
        np.testing.assert_array_equal(solar.lines[0].get_ydata(), self.weather["ghi"][start:])
        np.testing.assert_array_equal(wind.lines[0].get_ydata(), self.weather["wind10"][start:])
        for ax, vid in zip(bias, VIDS):
            (median,) = [l for l in ax.lines if l.get_marker() == fs.VARIANT_MARKERS[vid]]
            expected = np.median(self.runs[vid][start:] - self.weather["t_air"][start:, None], axis=1)
            np.testing.assert_allclose(median.get_ydata(), expected, rtol=0, atol=1e-12)

    def test_canvas_holds_only_axes_text_panel_letters_and_legend(self):
        allowed = axis_text(self.fig) | {f"({c})" for c in fs.LETTERS[:6]}
        self.assertLessEqual(printed(self.fig), allowed, printed(self.fig) - allowed)

    def test_nothing_printed_touches_anything(self):
        self.assertEqual(fs.audit(self.fig), [])

    def test_caption_matches_file_and_documents(self):
        text = tt.figure_caption(self.weather, self.runs)
        self.assertEqual(
            text, (ROOT / "analysis/figures/thermal_transient_prediction.caption.md").read_text().strip())
        self.assertIn("400 input draws", text)
        for doc in ("README.md", "docs/results.md"):
            self.assertIn(squash(text), squash((ROOT / doc).read_text()), doc)
            self.assertIn("thermal_transient_prediction.caption.md", (ROOT / doc).read_text(), doc)


if __name__ == "__main__":
    unittest.main()
