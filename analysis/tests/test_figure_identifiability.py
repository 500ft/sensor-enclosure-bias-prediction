"""The synthetic I1 plot data equals the committed profiles; words live in captions."""
import csv
import json
import unittest

import numpy as np

from analysis import render_identifiability as ri
from analysis.tests.figure_checks import FIGURES, MATLAB, ROOT, check_matlab_outputs, squash

OUT = ROOT / "analysis/output"
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
            rows = list(csv.DictReader((FIGURES / "data" / ri.profile_data(result)).read_text().splitlines()))
            cls.runs[stem] = (result, cfg, profiles, rows)

    def test_stems_and_configs_are_consistent(self):
        for stem, (result, cfg, _, _) in self.runs.items():
            self.assertEqual(ri.stem_of(result), stem)
            self.assertEqual(cfg["dt_s"], 60 if stem.endswith("_60s") else 15)
        self.assertEqual(ri.profile_data(self.runs[STEMS[0]][0]), ri.PROFILE_DATA)

    def test_profile_columns_equal_the_stored_arrays(self):
        for stem, (result, cfg, profiles, rows) in self.runs.items():
            cells = ri.profile_cells(result, cfg)
            columns = ri.profile_columns(cfg)
            self.assertEqual(list(rows[0]), ["candidate_cg_min"] + [name for _, _, name in columns], stem)
            for scenario, duration, name in columns:
                idx = cells[scenario, duration]
                self.assertEqual(result["cells"][idx]["schedule"], "repeated_steps")
                np.testing.assert_allclose([float(r["candidate_cg_min"]) for r in rows],
                                           profiles[f"cell{idx}_tau_s"] / 60, rtol=1e-7)
                np.testing.assert_allclose([float(r[name]) for r in rows],
                                           profiles[f"cell{idx}_delta_sse"], rtol=1e-7, atol=1e-12)

    def test_matlab_scripts_match_the_caption_encodings(self):
        source = (MATLAB / "make_identifiability_profiles.m").read_text()
        self.assertIn(f"PROFILE_YMAX = {ri.PROFILE_YMAX};", source)
        driver = (MATLAB / "render_figures.m").read_text()
        for stem, (result, cfg, _, _) in self.runs.items():
            self.assertEqual(list(cfg["schedules"]), ["single_step", "repeated_steps"])
            self.assertEqual(len(ri.SCHEDULE_STYLES), len(cfg["schedules"]))
            self.assertEqual(len(ri.PROFILE_STYLES), len(cfg["duration_s"]))
            self.assertIn(f"'{stem}'", driver)
            self.assertIn(f"'{result['config_file'].split('/')[-1]}'", driver)
            check_matlab_outputs(self, f"{stem}_profiles", "make_identifiability_profiles.m",
                                 ["_profiles.csv", "identifiability_design.json"])
            check_matlab_outputs(self, f"{stem}_tradeoffs", "make_identifiability_tradeoffs.m",
                                 ["synthetic_identifiability", "gain_open_fraction", "gain_coverage"])

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
