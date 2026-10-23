"""The synthetic I1 figures plot the committed profiles and summary rows; words live in captions."""
import csv
import json
import unittest

import numpy as np

from analysis import figure_style as fs
from analysis import render_identifiability as ri
from analysis.tests.figure_checks import ROOT, axis_text, printed, squash

import matplotlib.pyplot as plt  # noqa: E402

OUT = ROOT / "analysis/output"
FIGURES = ROOT / "analysis/figures"
# The registered 15 s run and its registered 60 s cadence amendment.
STEMS = ("synthetic_identifiability", "synthetic_identifiability_60s")


class IdentifiabilityFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs = {}
        for stem in STEMS:
            result = json.loads((OUT / f"{stem}.json").read_text())
            cfg = ri.config_of(result)
            profiles = np.load(OUT / result["profile_file"])
            cls.runs[stem] = (result, cfg, profiles,
                              {"profiles": ri.profiles_figure(result, profiles, cfg),
                               "tradeoffs": ri.tradeoffs_figure(result, cfg)})

    @classmethod
    def tearDownClass(cls):
        for *_, figs in cls.runs.values():
            for fig in figs.values():
                plt.close(fig)

    def test_stems_and_configs_are_consistent(self):
        for stem, (result, cfg, _, _) in self.runs.items():
            self.assertEqual(ri.stem_of(result), stem)
            self.assertEqual(cfg["dt_s"], 60 if stem.endswith("_60s") else 15)

    def test_profile_lines_equal_the_stored_arrays(self):
        for stem, (result, cfg, profiles, figs) in self.runs.items():
            cells = ri.profile_cells(result, cfg)
            for ax, (scenario, _) in zip(figs["profiles"].axes, ri.SCENARIOS):
                lines = [l for l in ax.lines if l.get_marker() in ri.MARKERS]
                self.assertEqual(len(lines), len(cfg["duration_s"]), stem)
                for j, (line, duration) in enumerate(zip(lines, cfg["duration_s"])):
                    idx = cells[scenario, duration]
                    self.assertEqual(result["cells"][idx]["schedule"], "repeated_steps")
                    self.assertEqual(line.get_marker(), ri.MARKERS[j])
                    np.testing.assert_array_equal(line.get_xdata(), profiles[f"cell{idx}_tau_s"] / 60)
                    np.testing.assert_array_equal(line.get_ydata(), profiles[f"cell{idx}_delta_sse"])

    def test_tradeoff_points_equal_the_csv(self):
        for stem, (result, cfg, _, figs) in self.runs.items():
            rows = list(csv.DictReader((OUT / f"{stem}.csv").read_text().splitlines()))
            axes = np.array(figs["tradeoffs"].axes).reshape(2, len(cfg["tau_s"]))
            for r, (scenario, field) in enumerate((("matched", "gain_open_fraction"),
                                                   ("ambient_mismatch", "gain_coverage"))):
                for c, tau in enumerate(cfg["tau_s"]):
                    lines = [l for l in axes[r, c].lines if l.get_marker() in ri.MARKERS]
                    for j, (line, sch) in enumerate(zip(lines, cfg["schedules"])):
                        expected = sorted((int(x["duration_s"]), float(x[field])) for x in rows
                                          if x["scenario"] == scenario and int(x["tau_s"]) == tau
                                          and x["schedule"] == sch)
                        self.assertEqual(line.get_marker(), ri.MARKERS[j])
                        self.assertEqual(list(line.get_xdata()), [d / 3600 for d, _ in expected])
                        self.assertEqual(list(line.get_ydata()), [v for _, v in expected])

    def test_canvas_holds_only_axes_text_panel_letters_and_legend(self):
        for stem, (*_, figs) in self.runs.items():
            for name, fig in figs.items():
                allowed = axis_text(fig) | {f"({c})" for c in fs.LETTERS}
                self.assertLessEqual(printed(fig), allowed, (stem, name, printed(fig) - allowed))

    def test_nothing_printed_touches_anything(self):
        for stem, (*_, figs) in self.runs.items():
            for name, fig in figs.items():
                self.assertEqual(fs.audit(fig), [], (stem, name))

    def test_captions_match_files_and_report(self):
        for stem, (result, cfg, _, _) in self.runs.items():
            report = (OUT / f"{stem}_report.md").read_text()
            for name, caption in (("profiles", ri.profiles_caption), ("tradeoffs", ri.tradeoffs_caption)):
                text = caption(result, cfg)
                self.assertEqual(text, (FIGURES / f"{stem}_{name}.caption.md").read_text().strip())
                self.assertIn(squash(text), squash(report))
                self.assertIn(f"{stem}_{name}.caption.md", report)

    def test_cadence_comparison_rows_equal_both_csvs(self):
        result, cfg, _, _ = self.runs["synthetic_identifiability_60s"]
        own = {r["key"]: r for r in csv.DictReader((OUT / "synthetic_identifiability_60s.csv").read_text().splitlines())}
        parent = {r["key"]: r for r in csv.DictReader((OUT / "synthetic_identifiability.csv").read_text().splitlines())}
        rows = result["cadence_comparison"]["rows"]
        self.assertEqual(len(rows), len(own))
        self.assertEqual(result["cadence_comparison"]["parent_dt_s"], 15)
        for row in rows:
            self.assertEqual(row["duration_s"] == row["parent_duration_s"], row["duration_s"] != min(cfg["duration_s"]))
            for field in ri.COMPARED:
                self.assertEqual(row[field], float(own[row["key"]][field]))
                self.assertEqual(row["parent_" + field], float(parent[row["parent_key"]][field]))
                self.assertAlmostEqual(row[field + "_change"], row[field] - row["parent_" + field], places=12)


if __name__ == "__main__":
    unittest.main()
