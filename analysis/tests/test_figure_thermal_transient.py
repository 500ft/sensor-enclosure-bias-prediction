"""The transient plot data is the stored weather and the draws behind the stored summary."""
import csv
import json
import unittest

import numpy as np

from analysis import thermal_transient as tt
from analysis.tests.figure_checks import FIGURES, ROOT, check_matlab_outputs, squash

VIDS = ("V0", "V0P", "V1", "V2")


class TransientFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The registered 400-draw run, about 10 s; the result JSON keeps only its summaries.
        cls.weather = tt.load_weather()
        draws = tt.draw(tt.N_SAMPLES)
        cls.runs = {vid: tt.simulate(vid, cls.weather, draws) for vid in VIDS}
        cls.rows = list(csv.DictReader(tt.OUT_FIG_DATA.read_text().splitlines()))

    def test_plotted_draws_reproduce_the_stored_summary(self):
        stored = json.loads((ROOT / "analysis/output/thermal_transient_prediction.json").read_text())
        self.assertEqual(stored["monte_carlo"]["samples"], tt.N_SAMPLES)
        self.assertEqual(stored["monte_carlo"]["seed"], tt.SEED)
        again = tt.summarise(self.weather, self.runs)
        for vid in VIDS:
            for key, values in stored["bias_summary"][vid].items():
                np.testing.assert_allclose(again[vid][key], values, rtol=1e-9, atol=1e-12)

    def test_plot_data_is_weather_file_and_draw_percentiles(self):
        start = np.searchsorted(self.weather["t_s"], tt.SPIN_UP_H * 3600)
        keep = np.arange(start, len(self.weather["t_s"]), tt.EXPORT_EVERY)
        self.assertEqual(len(self.rows), len(keep))
        col = lambda name: np.array([float(r[name]) for r in self.rows])
        np.testing.assert_allclose(col("ghi_w_m2"), self.weather["ghi"][keep], rtol=0, atol=1e-4)
        np.testing.assert_allclose(col("wind10_m_s"), self.weather["wind10"][keep], rtol=0, atol=1e-4)
        for vid in VIDS:
            bias = self.runs[vid][keep] - self.weather["t_air"][keep, None]
            for name, q in (("p05", 5), ("p50", 50), ("p95", 95)):
                np.testing.assert_allclose(col(f"{vid}_{name}_degc"), np.percentile(bias, q, axis=1),
                                           rtol=0, atol=1e-4)
        # every whole hour of the retained period is a kept row, so the solar steps are exact
        hours = {r["utc"] for r in self.rows if r["utc"].endswith(":00")}
        self.assertEqual(len(hours), (len(self.weather["t_s"]) - 1 - start) // 60 + 1)

    def test_matlab_figure_files(self):
        check_matlab_outputs(self, "thermal_transient_prediction", "make_thermal_transient.m",
                             ["thermal_transient_series.csv"])

    def test_caption_matches_file_and_documents(self):
        text = tt.figure_caption(self.weather, self.runs)
        self.assertEqual(
            text, (FIGURES / "thermal_transient_prediction.caption.md").read_text().strip())
        self.assertIn("400 input draws", text)
        for doc in ("README.md", "docs/results.md"):
            self.assertIn(squash(text), squash((ROOT / doc).read_text()), doc)
            self.assertIn("thermal_transient_prediction.caption.md", (ROOT / doc).read_text(), doc)


if __name__ == "__main__":
    unittest.main()
