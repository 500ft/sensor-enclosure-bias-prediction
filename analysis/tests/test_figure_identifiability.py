"""The synthetic I1 figures plot the committed profiles and summary rows; words live in captions."""
import csv
import json
import unittest

import numpy as np

from analysis import figure_style as fs
from analysis import render_identifiability as ri
from analysis import synthetic_identifiability as study
from analysis.tests.figure_checks import ROOT, axis_text, printed, squash

import matplotlib.pyplot as plt  # noqa: E402

OUT = ROOT / "analysis/output"
FIGURES = ROOT / "analysis/figures"


class IdentifiabilityFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((OUT / "synthetic_identifiability.json").read_text())
        cls.cfg = json.loads(study.CONFIG.read_text())
        cls.profiles = np.load(OUT / cls.result["profile_file"])
        cls.figs = {"profiles": ri.profiles_figure(cls.result, cls.profiles, cls.cfg),
                    "tradeoffs": ri.tradeoffs_figure(cls.result, cls.cfg)}

    @classmethod
    def tearDownClass(cls):
        for fig in cls.figs.values():
            plt.close(fig)

    def test_profile_lines_equal_the_stored_arrays(self):
        cells = ri.profile_cells(self.result, self.cfg)
        for ax, (scenario, _) in zip(self.figs["profiles"].axes, ri.SCENARIOS):
            lines = [l for l in ax.lines if l.get_marker() in ri.MARKERS]
            self.assertEqual(len(lines), len(self.cfg["duration_s"]))
            for j, (line, duration) in enumerate(zip(lines, self.cfg["duration_s"])):
                idx = cells[scenario, duration]
                self.assertEqual(self.result["cells"][idx]["schedule"], "repeated_steps")
                self.assertEqual(line.get_marker(), ri.MARKERS[j])
                np.testing.assert_array_equal(line.get_xdata(), self.profiles[f"cell{idx}_tau_s"] / 60)
                np.testing.assert_array_equal(line.get_ydata(), self.profiles[f"cell{idx}_delta_sse"])

    def test_tradeoff_points_equal_the_csv(self):
        rows = list(csv.DictReader((OUT / "synthetic_identifiability.csv").read_text().splitlines()))
        axes = np.array(self.figs["tradeoffs"].axes).reshape(2, len(self.cfg["tau_s"]))
        for r, (scenario, field) in enumerate((("matched", "gain_open_fraction"),
                                               ("ambient_mismatch", "gain_coverage"))):
            for c, tau in enumerate(self.cfg["tau_s"]):
                lines = [l for l in axes[r, c].lines if l.get_marker() in ri.MARKERS]
                for j, (line, sch) in enumerate(zip(lines, self.cfg["schedules"])):
                    expected = sorted((int(x["duration_s"]), float(x[field])) for x in rows
                                      if x["scenario"] == scenario and int(x["tau_s"]) == tau
                                      and x["schedule"] == sch)
                    self.assertEqual(line.get_marker(), ri.MARKERS[j])
                    self.assertEqual(list(line.get_xdata()), [d / 3600 for d, _ in expected])
                    self.assertEqual(list(line.get_ydata()), [v for _, v in expected])

    def test_canvas_holds_only_axes_text_panel_letters_and_legend(self):
        for name, fig in self.figs.items():
            allowed = axis_text(fig) | {f"({c})" for c in fs.LETTERS}
            self.assertLessEqual(printed(fig), allowed, (name, printed(fig) - allowed))

    def test_nothing_printed_touches_anything(self):
        for name, fig in self.figs.items():
            self.assertEqual(fs.audit(fig), [], name)

    def test_captions_match_files_and_report(self):
        report = (OUT / "synthetic_identifiability_report.md").read_text()
        for name, caption in (("profiles", ri.profiles_caption), ("tradeoffs", ri.tradeoffs_caption)):
            text = caption(self.result, self.cfg)
            stem = f"synthetic_identifiability_{name}"
            self.assertEqual(text, (FIGURES / f"{stem}.caption.md").read_text().strip())
            self.assertIn(squash(text), squash(report))
            self.assertIn(f"{stem}.caption.md", report)


if __name__ == "__main__":
    unittest.main()
