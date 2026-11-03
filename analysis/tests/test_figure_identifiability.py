"""The synthetic I1 plot data equals the committed profiles; words live in captions."""
import csv
import json
import unittest

import numpy as np

from analysis import render_identifiability as ri
from analysis import synthetic_identifiability as study
from analysis.tests.figure_checks import FIGURES, MATLAB, ROOT, check_matlab_outputs, squash

OUT = ROOT / "analysis/output"


class IdentifiabilityFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((OUT / "synthetic_identifiability.json").read_text())
        cls.cfg = json.loads(study.CONFIG.read_text())
        cls.profiles = np.load(OUT / cls.result["profile_file"])
        cls.rows = list(csv.DictReader((FIGURES / "data" / ri.PROFILE_DATA).read_text().splitlines()))

    def test_profile_columns_equal_the_stored_arrays(self):
        cells = ri.profile_cells(self.result, self.cfg)
        columns = ri.profile_columns(self.cfg)
        self.assertEqual(list(self.rows[0]), ["candidate_cg_min"] + [name for _, _, name in columns])
        for scenario, duration, name in columns:
            idx = cells[scenario, duration]
            self.assertEqual(self.result["cells"][idx]["schedule"], "repeated_steps")
            np.testing.assert_allclose([float(r["candidate_cg_min"]) for r in self.rows],
                                       self.profiles[f"cell{idx}_tau_s"] / 60, rtol=1e-7)
            np.testing.assert_allclose([float(r[name]) for r in self.rows],
                                       self.profiles[f"cell{idx}_delta_sse"], rtol=1e-7, atol=1e-12)

    def test_matlab_scripts_match_the_caption_encodings(self):
        self.assertEqual(list(self.cfg["schedules"]), ["single_step", "repeated_steps"])
        self.assertEqual(len(ri.SCHEDULE_STYLES), len(self.cfg["schedules"]))
        self.assertEqual(len(ri.PROFILE_STYLES), len(self.cfg["duration_s"]))
        source = (MATLAB / "make_identifiability_profiles.m").read_text()
        self.assertIn(f"PROFILE_YMAX = {ri.PROFILE_YMAX};", source)
        check_matlab_outputs(self, "synthetic_identifiability_profiles", "make_identifiability_profiles.m",
                             [ri.PROFILE_DATA, "identifiability_design.json"])
        check_matlab_outputs(self, "synthetic_identifiability_tradeoffs", "make_identifiability_tradeoffs.m",
                             ["synthetic_identifiability.csv", "gain_open_fraction", "gain_coverage"])

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
