"""T1 -- campaign manifest and cross-variant pairing. Synthetic three-arm campaigns only; nothing here
is environmental evidence. Known answers are derived by hand in the campaign() docstring, not copied
from the implementation."""
import copy
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analysis.campaign_manifest import ManifestError, main, pair

ROOT = Path(__file__).resolve().parents[2]
START = datetime(2026, 1, 1, tzinfo=timezone.utc)
FIELDS = ["timestamp", "sensor_temperature", "reference_temperature", "solar_w_m2", "wind_m_s"]
ARCHIVE = "a" * 64


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_arm(directory, vid, *, drop_rows=(), empty_sensor=(), ref="REF-1", kind="synthetic"):
    """1440 one-minute rows; rows in drop_rows are absent, rows in empty_sensor have an empty sensor value."""
    csv_path, meta_path = Path(directory) / f"{vid}.csv", Path(directory) / f"{vid}.json"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for i in range(1440):
            if i in drop_rows:
                continue
            w.writerow(dict(timestamp=(START + timedelta(minutes=i)).isoformat(),
                            sensor_temperature="" if i in empty_sensor else "20.0",
                            reference_temperature="19.5", solar_w_m2="0", wind_m_s="1"))
    meta = dict(sensor_id=f"S-{vid}", reference_id=ref, evidence_kind=kind, csv_sha256=sha(csv_path))
    meta_path.write_text(json.dumps(meta))
    return dict(variant_id=vid, csv_path=csv_path.name, metadata_path=meta_path.name,
                sensor_id=f"S-{vid}", reference_id=ref, csv_sha256=sha(csv_path),
                metadata_sha256=sha(meta_path))


def rehash(directory, manifest, index, vid):
    """Re-record hashes after a test edits an arm's CSV on disk."""
    d = Path(directory)
    meta = json.loads((d / f"{vid}.json").read_text())
    meta["csv_sha256"] = sha(d / f"{vid}.csv")
    (d / f"{vid}.json").write_text(json.dumps(meta))
    manifest["arms"][index]["csv_sha256"] = sha(d / f"{vid}.csv")
    manifest["arms"][index]["metadata_sha256"] = sha(d / f"{vid}.json")


def campaign(directory):
    """V0 lacks every 10th row (0,10,...,1430: 144 rows); V0P has an empty sensor value on every 15th
    row (96 rows); V1 is complete.  Multiples of 30 are in both sets (48).
      valid(V0)=1296  valid(V0P)=1344  valid(V1)=1440
      V0|V0P  paired = 1440-(144+96-48) = 1248; valid only in V0 = 96-48 = 48; only in V0P = 144-48 = 96
      V0|V1   paired = 1296;               only in V0 = 0;                    only in V1 = 144
      all-arm complete = 1248
    """
    arms = [write_arm(directory, "V0", drop_rows=set(range(0, 1440, 10))),
            write_arm(directory, "V0P", empty_sensor=set(range(0, 1440, 15))),
            write_arm(directory, "V1")]
    return dict(campaign_id="SYNTHETIC-CAMPAIGN", protocol_archive_sha256=ARCHIVE,
                intended_window_start_utc=START.isoformat(),
                intended_window_end_utc=(START + timedelta(days=1)).isoformat(), cadence_s=60, arms=arms)


class PairingTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.manifest = campaign(self.dir)

    def test_known_answers_for_a_three_arm_campaign(self):
        r = pair(self.manifest, self.dir)
        self.assertEqual(r["expected_slots"], 1440)
        self.assertEqual({v: a["valid_slots"] for v, a in r["arms"].items()}, {"V0": 1296, "V0P": 1344, "V1": 1440})
        self.assertEqual(r["arms"]["V0"]["rows_absent"], 144)
        self.assertEqual(r["arms"]["V0P"]["rows_missing_sensor"], 96)
        c = r["contrasts"]["V0|V0P"]
        self.assertEqual((c["paired_slots"], c["dropped_valid_only_in_first"], c["dropped_valid_only_in_second"]),
                         (1248, 48, 96))
        c = r["contrasts"]["V0|V1"]
        self.assertEqual((c["paired_slots"], c["dropped_valid_only_in_first"], c["dropped_valid_only_in_second"]),
                         (1296, 0, 144))
        self.assertEqual(r["all_arm_complete"]["slots"], 1248)
        self.assertLess(r["all_arm_complete"]["fraction"], r["arms"]["V0"]["valid_fraction"])  # cross-variant is lower
        self.assertEqual(r["reference_sharing"], {"REF-1": ["V0", "V0P", "V1"]})
        self.assertFalse(r["validates_thermal_model"])
        self.assertTrue(r["synthetic_only"])

    def test_1_hash_mismatch_refuses_for_csv_metadata_and_a_changed_byte(self):
        for key in ("csv_sha256", "metadata_sha256"):
            with self.subTest(key=key):
                m = copy.deepcopy(self.manifest)
                m["arms"][2][key] = "0" * 64
                with self.assertRaisesRegex(ManifestError, key):
                    pair(m, self.dir)
        (self.dir / "V1.csv").write_text((self.dir / "V1.csv").read_text() + "\n")   # edited after hashing
        with self.assertRaisesRegex(ManifestError, "csv_sha256"):
            pair(self.manifest, self.dir)

    def test_2_differing_cadence_or_window_refuses(self):
        for key, value in (("cadence_s", 300),
                           ("intended_window_end_utc", (START + timedelta(hours=12)).isoformat()),
                           ("intended_window_start_utc", (START + timedelta(minutes=1)).isoformat())):
            with self.subTest(key=key):
                m = copy.deepcopy(self.manifest)
                m["arms"][1][key] = value
                with self.assertRaisesRegex(ManifestError, f"V0P.*{key}.*differs"):
                    pair(m, self.dir)
        m = copy.deepcopy(self.manifest)
        m["arms"][1]["cadence_s"] = 60          # an agreeing per-arm declaration is fine
        pair(m, self.dir)

    def test_3_slot_absent_or_empty_in_one_arm_is_dropped_and_counted_never_filled(self):
        r = pair(self.manifest, self.dir)
        # minute 10: no V0 row, V0P valid -> valid only in the second arm, excluded from V0|V0P
        self.assertEqual(r["contrasts"]["V0|V0P"]["dropped_valid_only_in_second"], 96)
        self.assertEqual(r["arms"]["V0"]["rows"], 1296)     # nothing was back-filled

    def test_4_missing_optional_arm_degrades_but_missing_required_arm_refuses(self):
        m = copy.deepcopy(self.manifest)
        m["arms"].append(dict(variant_id="V0-U", csv_path="V0-U.csv", metadata_path="V0-U.json",
                              sensor_id="S", reference_id="REF-1", csv_sha256="0" * 64,
                              metadata_sha256="0" * 64, optional=True))
        r = pair(m, self.dir)
        self.assertEqual(r["absent_optional_arms"], ["V0-U"])
        self.assertTrue(r["reduced_coverage"])
        self.assertEqual(r["contrasts"]["V0|V0P"]["paired_slots"], 1248)      # surviving contrast intact
        self.assertFalse(any("V0-U" in k for k in r["contrasts"]))
        m["arms"][-1]["optional"] = False
        with self.assertRaisesRegex(ManifestError, "V0-U.*not optional"):
            pair(m, self.dir)
        m["arms"][-1]["optional"] = "yes"
        with self.assertRaisesRegex(ManifestError, "optional must be true or false"):
            pair(m, self.dir)

    def test_4b_optional_means_may_be_absent_not_may_be_corrupt(self):
        m = copy.deepcopy(self.manifest)
        m["arms"][2]["optional"] = True
        m["arms"][2]["csv_sha256"] = "0" * 64
        with self.assertRaisesRegex(ManifestError, "csv_sha256"):
            pair(m, self.dir)

    def test_5_duplicate_variant_id_refuses_and_uniqueness_scope_is_stated(self):
        m = copy.deepcopy(self.manifest)
        m["arms"][2]["variant_id"] = "V0"
        with self.assertRaisesRegex(ManifestError, "duplicate variant_id"):
            pair(m, self.dir)
        self.assertEqual(pair(self.manifest, self.dir)["campaign_id_uniqueness_scope"], "within this manifest only")

    def test_6_protocol_reference_absent_unresolvable_or_repo_less_refuses(self):
        m = copy.deepcopy(self.manifest)
        del m["protocol_archive_sha256"]
        with self.assertRaisesRegex(ManifestError, "no protocol reference"):
            pair(m, self.dir)
        m["protocol_commit"] = "deadbeef" * 5
        with self.assertRaisesRegex(ManifestError, "needs protocol_repo"):
            pair(m, self.dir)
        m["protocol_repo"] = str(ROOT)
        with self.assertRaisesRegex(ManifestError, "does not resolve"):
            pair(m, self.dir)
        m["protocol_commit"] = "--upload-pack=x"
        with self.assertRaisesRegex(ManifestError, "lowercase hex"):
            pair(m, self.dir)
        m["protocol_commit"], m["protocol_archive_sha256"] = None, "not-a-hash"
        with self.assertRaisesRegex(ManifestError, "no protocol reference"):
            pair(m, self.dir)

    @unittest.skipUnless((ROOT / ".git").exists(), "needs a git checkout to resolve a real commit")
    def test_6b_a_real_commit_in_the_named_repo_is_accepted(self):
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        m = copy.deepcopy(self.manifest)
        del m["protocol_archive_sha256"]
        m["protocol_commit"], m["protocol_repo"] = head, str(ROOT)
        self.assertEqual(pair(m, self.dir)["protocol"]["kind"], "git")

    def test_7_existing_report_is_refused_before_any_write(self):
        (self.dir / "manifest.json").write_text(json.dumps(self.manifest))
        out = self.dir / "pairing.json"
        out.write_text("previous run")
        self.assertEqual(main([str(self.dir / "manifest.json"), "--out", str(out)]), 2)
        self.assertEqual(out.read_text(), "previous run")
        link = self.dir / "dangling.json"
        link.symlink_to(self.dir / "nowhere.json")
        self.assertEqual(main([str(self.dir / "manifest.json"), "--out", str(link)]), 2)
        self.assertFalse((self.dir / "nowhere.json").exists())

    def test_a_refused_run_writes_nothing_and_a_good_run_writes_once(self):
        bad = copy.deepcopy(self.manifest)
        bad["arms"][0]["csv_sha256"] = "0" * 64
        (self.dir / "bad.json").write_text(json.dumps(bad))
        self.assertEqual(main([str(self.dir / "bad.json"), "--out", str(self.dir / "r.json")]), 2)
        self.assertFalse((self.dir / "r.json").exists())
        (self.dir / "good.json").write_text(json.dumps(self.manifest))
        self.assertEqual(main([str(self.dir / "good.json"), "--out", str(self.dir / "r.json")]), 3)  # synthetic
        self.assertEqual(json.loads((self.dir / "r.json").read_text())["all_arm_complete"]["slots"], 1248)

    def test_grid_violations_refuse_rather_than_round(self):
        for label, mutate in (("off-grid", lambda t: t + timedelta(seconds=1)),
                              ("outside window", lambda t: t + timedelta(days=1)),
                              ("naive clock", lambda t: t.replace(tzinfo=None))):
            with self.subTest(label):
                d = self.dir / label.replace(" ", "_")
                d.mkdir()
                m = campaign(d)
                p = d / "V1.csv"
                with p.open(newline="") as f:
                    rows = list(csv.DictReader(f))
                rows[5]["timestamp"] = mutate(datetime.fromisoformat(rows[5]["timestamp"])).isoformat()
                with p.open("w", newline="") as f:
                    w = csv.DictWriter(f, FIELDS)
                    w.writeheader()
                    w.writerows(rows)
                rehash(d, m, 2, "V1")
                with self.assertRaisesRegex(ManifestError, "V1"):
                    pair(m, d)

    def test_duplicate_row_within_an_arm_refuses(self):
        p = self.dir / "V1.csv"
        lines = p.read_text().splitlines()
        p.write_text("\n".join(lines + [lines[10]]) + "\n")
        rehash(self.dir, self.manifest, 2, "V1")
        with self.assertRaisesRegex(ManifestError, "duplicate sampling slot"):
            pair(self.manifest, self.dir)

    def test_manifest_vs_metadata_identity_disagreement_refuses(self):
        m = copy.deepcopy(self.manifest)
        m["arms"][0]["reference_id"] = "REF-2"
        with self.assertRaisesRegex(ManifestError, "reference_id differs"):
            pair(m, self.dir)

    def test_missing_field_and_empty_arm_list_refuse(self):
        m = copy.deepcopy(self.manifest)
        del m["arms"][0]["reference_id"]
        with self.assertRaisesRegex(ManifestError, "every arm needs"):
            pair(m, self.dir)
        with self.assertRaisesRegex(ManifestError, "non-empty list"):
            pair({**self.manifest, "arms": []}, self.dir)


class IntakeCompatibilityTests(unittest.TestCase):
    """The single-pair intake is untouched: an arm file this module accepts is still read by the
    existing intake CLI, with the same schema and hash handling as before."""

    def test_existing_intake_still_reads_an_arm_written_for_the_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            arm = write_arm(d, "V1")
            meta = json.loads((d / "V1.json").read_text())
            meta.update(window_start=START.isoformat(), window_end=(START + timedelta(days=1)).isoformat(),
                        site_id="X", firmware="fixture", clock_basis="UTC sample time",
                        calibration_reference="fixture", uncertainty_reference="fixture",
                        permission_reference="none", protocol_reference="fixture", paired_u95_c=0.2)
            (d / "V1.json").write_text(json.dumps(meta))
            r = subprocess.run([sys.executable, "-m", "analysis.colocation_intake", str(d / "V1.csv"),
                                "--metadata", str(d / "V1.json")], cwd=ROOT, capture_output=True, text=True)
            out = json.loads(r.stdout)
            # solar is 0 everywhere, so the intake's own verdict is INCOMPLETE; the point is that it
            # parses the same bytes with no schema/hash complaint and counts every slot.
            self.assertEqual(out["classification"], "INCOMPLETE")
            self.assertEqual((out["expected_slots"], out["paired_slots"]), (1440, 1440))
            self.assertEqual(out["csv_sha256"], arm["csv_sha256"])


if __name__ == "__main__":
    unittest.main()
