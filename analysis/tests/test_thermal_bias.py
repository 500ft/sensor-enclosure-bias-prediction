"""Developer checks for the matched-finish control, not physical validation."""

import csv
from contextlib import redirect_stdout
from dataclasses import asdict
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from analysis.thermal_bias import build_variants, print_bias_table, run_sweep, write_bias_table


class MatchedFinishTests(unittest.TestCase):
    def setUp(self):
        self.variants = build_variants()
        self.by_id = {v.vid: v for v in self.variants}

    def sweep(self, solar):
        return run_sweep(self.variants, np.array([0.0, 0.5, 5.0]), solar,
                         30.0, 50.0, 10.0, 5.0, 4.0)

    def test_painted_control_changes_only_absorptance_and_labels(self):
        self.assertIn("V0P", self.by_id, "Primary painted control is absent from the main sweep")
        dark = asdict(self.by_id["V0"])
        painted = asdict(self.by_id["V0P"])
        for key in ("vid", "name", "note", "alpha"):
            dark.pop(key)
            painted.pop(key)
        self.assertEqual(dark, painted)
        self.assertEqual(self.by_id["V0P"].alpha, self.by_id["V1"].alpha)
        self.assertEqual(self.by_id["V0P"].eps, self.by_id["V1"].eps)

    def test_control_does_not_mutate_dark_box_and_keeps_existing_predictions(self):
        self.assertEqual(self.by_id["V0"].alpha, 0.9)
        result = self.sweep([1000.0])
        for vid, expected in (("V0", 19.4), ("V0P", 4.5), ("V1", 3.0), ("V2", 1.3)):
            self.assertIn(vid, result.dT)
            self.assertAlmostEqual(result.dT[vid][1000.0][1], expected, delta=0.1)

    def test_no_solar_means_absorptance_control_has_no_effect(self):
        result = self.sweep([0.0])
        self.assertIn("V0P", result.dT)
        np.testing.assert_array_equal(result.dT["V0"][0.0], result.dT["V0P"][0.0])
        np.testing.assert_array_equal(result.rh_err["V0"][0.0], result.rh_err["V0P"][0.0])

    def test_csv_contains_matched_control_at_every_operating_point(self):
        result = self.sweep([800.0, 1000.0])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bias.csv"
            write_bias_table(result, self.variants, [0.0, 0.5, 5.0], str(output))
            lines = output.read_text().splitlines()
        self.assertIn("SIMULATION", lines[0])
        rows = list(csv.DictReader(io.StringIO("\n".join(lines[1:]))))
        self.assertEqual(len(rows), 24)
        for g in ("800", "1000"):
            for wind in ("0.0", "0.5", "5.0"):
                self.assertEqual({r["variant_id"] for r in rows
                                  if r["g_w_m2"] == g and r["wind_m_s"] == wind},
                                 {"V0", "V0P", "V1", "V2"})

    def test_consumer_cli_exports_control_and_figure_data_outside_checkout(self):
        script = Path(__file__).resolve().parents[1] / "thermal_bias.py"
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(script), "--table", "bias.csv", "--night-table", "night.csv",
                 "--figure-data", "sweep.csv", "--caption", "bias.caption.md"],
                cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Painted closed-box control", result.stdout)
            self.assertIn("not an isolated shielding effect", result.stdout)
            self.assertIn(",V0P,", (Path(directory) / "bias.csv").read_text())
            self.assertIn(",V0P,", (Path(directory) / "sweep.csv").read_text())
            self.assertIn("Blue solid lines", (Path(directory) / "bias.caption.md").read_text())


class NightClearSkyTests(unittest.TestCase):
    """EN-D02: the zero-solar case is the same solver with G = 0, not a new model.

    Under the default loads and 20 K sky depression, radiative loss exceeds
    internal heating at ambient. This is conditional, not a universal night
    prediction; a weaker sky depression is an explicit opposite-sign control.
    """

    def setUp(self):
        self.variants = build_variants()
        self.by_id = {v.vid: v for v in self.variants}
        self.wind = np.array([0.0, 0.5, 2.0, 5.0])
        self.night = run_sweep(self.variants, self.wind, [0.0], 30.0, 50.0, 10.0, 5.0, 4.0)
        self.day = run_sweep(self.variants, self.wind, [1000.0], 30.0, 50.0, 10.0, 5.0, 4.0)

    def test_sky_exposed_box_reads_below_ambient_at_night(self):
        for vid in ("V0", "V0P"):
            self.assertGreater(self.by_id[vid].f_sky, 0.0)
            self.assertTrue(np.all(self.night.dT[vid][0.0] < 0.0),
                            f"{vid} should show a COLD bias with G = 0 and a clear sky")

    def test_night_bias_is_opposite_in_sign_to_day_bias_for_the_box(self):
        self.assertTrue(np.all(self.day.dT["V0"][1000.0] > 0.0))
        self.assertTrue(np.all(self.night.dT["V0"][0.0] < 0.0))

    def test_whole_shield_variant_has_smaller_night_bias_at_default_conditions(self):
        # V1 changes sky view, geometry, heat load and convection together;
        # this comparison does not isolate a causal sky-view effect.
        self.assertLess(self.by_id["V1"].f_sky, self.by_id["V0"].f_sky)
        self.assertTrue(np.all(np.abs(self.night.dT["V1"][0.0]) < np.abs(self.night.dT["V0"][0.0])))

    def test_painted_control_is_identical_to_dark_box_at_night(self):
        # Absorptance only enters through solar load; with G = 0 the finish cannot matter.
        np.testing.assert_allclose(self.night.dT["V0P"][0.0], self.night.dT["V0"][0.0], rtol=0, atol=1e-12)

    def test_wind_reduces_the_night_cold_bias_magnitude(self):
        mags = np.abs(self.night.dT["V0"][0.0])
        self.assertTrue(np.all(np.diff(mags) <= 0.0))

    def test_night_table_is_written_and_contains_every_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "night.csv"
            write_bias_table(self.night, self.variants, [0.0, 2.0], str(out))
            with out.open() as fh:
                rows = list(csv.reader(fh))
            body = [r for r in rows if r and r[0] == "0"]
            self.assertEqual(len(body), 2 * len(self.variants))
            self.assertTrue(all(float(r[4]) < 0.0 for r in body if r[2] in ("V0", "V0P")))

    def test_night_summary_labels_the_actual_wind_endpoints(self):
        for result, solar in ((self.night, 0.0), (self.day, 1000.0)):
            with self.subTest(solar=solar):
                output = io.StringIO()
                with redirect_stdout(output):
                    print_bias_table(result, self.variants, [0.0, 5.0])
                values = result.dT["V0"][solar]
                expected = f"dT = {values[0]:5.1f} (calm) .. {values[-1]:4.1f} (windy) degC"
                self.assertIn(expected, output.getvalue())

    def test_weaker_sky_depression_can_reverse_the_night_bias(self):
        # Counterexample to a sign-invariant claim: retain the same electronics
        # load and geometry; change ONLY sky temperature from 10 to 29 degC.
        weak_cooling = run_sweep(self.variants, self.wind, [0.0],
                                 30.0, 50.0, 29.0, 5.0, 4.0)
        self.assertTrue(np.all(self.night.dT["V0"][0.0] < 0.0))
        self.assertTrue(np.all(weak_cooling.dT["V0"][0.0] > 0.0))

    def test_consumer_cli_reproduces_both_committed_tables_without_overwriting_them(self):
        root = Path(__file__).resolve().parents[2]
        names = ("thermal_bias_table.csv", "thermal_bias_night_table.csv")
        committed = {name: (root / "analysis/output" / name).read_bytes() for name in names}
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(root / "analysis/thermal_bias.py"), "--no-figure",
                 "--table", names[0], "--night-table", names[1]],
                cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in names:
                self.assertEqual((Path(directory) / name).read_bytes(), committed[name])
                self.assertEqual((root / "analysis/output" / name).read_bytes(), committed[name])


if __name__ == "__main__":
    unittest.main()
