"""T1 -- campaign manifest validation and cross-variant pairing.

    python -m analysis.campaign_manifest MANIFEST.json --out PAIRING_REPORT.json

Spec: docs/specs/implementation-tickets-2026-09-24.md (T1) and
docs/specs/pilot-readiness/pilot-design-2026-09-24.md (R2.2-R2.3). Every arm's CSV is the existing
single-pair intake schema (analysis.colocation_intake.FIELDS) and is NOT modified or re-validated
here; this module only checks the manifest, verifies the raw bytes, and counts which timestamps are
finite in which arms.

Refuses loudly (exit 2, nothing written): hash mismatch; arms whose cadence or window differ;
timestamps off the declared grid, outside the window, or duplicated within an arm; a duplicate
variant_id; a missing required arm; a protocol reference that cannot be checked; an existing report.
Degrades and reports instead: a missing OPTIONAL arm (only its contrasts disappear) and slots absent
or empty in some arm (dropped from that contrast and counted, never filled or interpolated).

Scope limits, stated so they are not mistaken for guarantees:
  * campaign_id uniqueness is checked WITHIN this manifest only -- there is no registry of past
    campaigns, so reuse across manifests is not detectable here.
  * Coverage numbers are reported per arm and per contrast; no pass/fail against the protocol's
    readiness criteria is applied (that judgement stays with the owner and the intake).
  * Missingness keyed by temperature and power state is NOT produced: power state comes from the
    auxiliary channels (T3), which do not exist yet. Missingness is keyed by channel instead.
  * Hashes are compared to values in the manifest; the manifest itself is not authenticated.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math, re, subprocess, sys
from datetime import timezone
from pathlib import Path

from analysis.colocation_intake import FIELDS
from analysis.compute_metrics import parse_float, parse_timestamp, scheduled_slots

ARM_KEYS = ("variant_id", "csv_path", "metadata_path", "sensor_id", "reference_id",
            "csv_sha256", "metadata_sha256")
MAX_SLOTS = 1_000_000
HEX = re.compile(r"[0-9a-f]+")


class ManifestError(ValueError):
    """Input that must stop the run; never degraded into a partial result."""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc(value, name):
    if not isinstance(value, str):
        raise ManifestError(f"{name} must be an ISO-8601 string")
    try:
        t = parse_timestamp(value)
    except ValueError:
        raise ManifestError(f"{name} is not an ISO-8601 timestamp: {value!r}") from None
    if t.utcoffset() is None or t.utcoffset().total_seconds() != 0:
        raise ManifestError(f"{name} must be UTC (Z or +00:00): {value!r}")
    return t.astimezone(timezone.utc)


def _cadence(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ManifestError(f"{name} must be a finite positive number of seconds")
    return float(value)


def check_protocol(manifest: dict, base: Path) -> dict:
    """A commit is meaningful only relative to a named repository; an offline archive may supply a
    raw-byte hash instead. Neither supplied -> refuse."""
    commit = manifest.get("protocol_commit")
    if commit is not None:
        if not isinstance(commit, str) or not (7 <= len(commit) <= 64) or not HEX.fullmatch(commit):
            raise ManifestError("protocol_commit must be a lowercase hex git SHA")
        repo = manifest.get("protocol_repo")
        if not isinstance(repo, str) or not repo:
            raise ManifestError("protocol_commit needs protocol_repo: a SHA means nothing without a named repository")
        r = subprocess.run(["git", "-C", str(base / repo), "cat-file", "-e", commit + "^{commit}"],
                           capture_output=True)
        if r.returncode:
            raise ManifestError(f"protocol_commit {commit} does not resolve in {repo}")
        return {"kind": "git", "commit": commit, "repo": repo}
    archive = manifest.get("protocol_archive_sha256")
    if isinstance(archive, str) and len(archive) == 64 and HEX.fullmatch(archive):
        return {"kind": "archive_sha256", "sha256": archive}
    raise ManifestError("no protocol reference: supply protocol_commit + protocol_repo, "
                        "or protocol_archive_sha256 for an offline archive")


def _load_arm(arm: dict, base: Path, start, end, cadence_s):
    vid = arm["variant_id"]
    csv_path, meta_path = base / arm["csv_path"], base / arm["metadata_path"]
    if not csv_path.is_file():
        if arm.get("optional", False) is True:
            return None
        raise ManifestError(f"arm {vid}: csv_path {arm['csv_path']} is missing and the arm is not optional")
    if not meta_path.is_file():
        raise ManifestError(f"arm {vid}: metadata_path {arm['metadata_path']} is missing")
    if _sha(csv_path) != arm["csv_sha256"]:
        raise ManifestError(f"arm {vid}: csv_sha256 does not match the file on disk")
    if _sha(meta_path) != arm["metadata_sha256"]:
        raise ManifestError(f"arm {vid}: metadata_sha256 does not match the file on disk")
    try:
        meta = json.loads(meta_path.read_text())
    except ValueError as e:
        raise ManifestError(f"arm {vid}: metadata is not JSON: {e}") from None
    if not isinstance(meta, dict):
        raise ManifestError(f"arm {vid}: metadata must be a JSON object")
    for key in ("sensor_id", "reference_id", "csv_sha256"):
        if key in meta and meta[key] != arm[key]:
            raise ManifestError(f"arm {vid}: {key} differs between manifest and metadata")
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) \
                or set(reader.fieldnames) != FIELDS:
            raise ManifestError(f"arm {vid}: CSV fields differ from the intake schema")
        rows = list(reader)
    for n, row in enumerate(rows, start=2):
        if None in row or None in row.values():
            raise ManifestError(f"arm {vid}: CSV row {n} has the wrong number of fields")
    times = [_utc(r["timestamp"], f"arm {vid} timestamp") for r in rows]
    expected, slots, inside = scheduled_slots(times, start, end, cadence_s / 60, 0)
    if not all(inside) or any(s is None for s in slots):
        raise ManifestError(f"arm {vid}: records outside the window or off the declared {cadence_s:g}-second grid")
    if len(set(slots)) != len(slots):
        raise ManifestError(f"arm {vid}: duplicate sampling slot; reconcile raw logger records first")
    valid, no_sensor, no_ref = set(), 0, 0
    for slot, row in zip(slots, rows):
        s, r = parse_float(row["sensor_temperature"]), parse_float(row["reference_temperature"])
        no_sensor += s is None
        no_ref += r is None
        if s is not None and r is not None:
            valid.add(slot)
    return dict(expected=expected, valid=valid, rows=len(rows), no_sensor=no_sensor, no_ref=no_ref,
                evidence_kind=meta.get("evidence_kind"))


def pair(manifest: dict, base: Path) -> dict:
    """Validate the manifest and return the pairing report. Raises ManifestError before any output."""
    if not isinstance(manifest, dict):
        raise ManifestError("manifest must be a JSON object")
    cid = manifest.get("campaign_id")
    if not isinstance(cid, str) or not cid.strip():
        raise ManifestError("campaign_id must be a non-empty string")
    protocol = check_protocol(manifest, base)
    start = _utc(manifest.get("intended_window_start_utc"), "intended_window_start_utc")
    end = _utc(manifest.get("intended_window_end_utc"), "intended_window_end_utc")
    cadence_s = _cadence(manifest.get("cadence_s"), "cadence_s")
    if end <= start:
        raise ManifestError("intended window must end after it starts (end is exclusive)")
    if (end - start).total_seconds() / cadence_s > MAX_SLOTS:
        raise ManifestError(f"window/cadence implies more than {MAX_SLOTS} slots")
    arms = manifest.get("arms")
    if not isinstance(arms, list) or not arms:
        raise ManifestError("arms must be a non-empty list")
    ids = []
    for a in arms:
        if not isinstance(a, dict) or any(not isinstance(a.get(k), str) or not a[k] for k in ARM_KEYS):
            raise ManifestError("every arm needs non-empty string fields: " + ", ".join(ARM_KEYS))
        if type(a.get("optional", False)) is not bool:
            raise ManifestError(f"arm {a['variant_id']}: optional must be true or false")
        ids.append(a["variant_id"])
        # A per-arm declaration is allowed only if it agrees with the campaign's.
        for key, want in (("cadence_s", cadence_s), ("intended_window_start_utc", start),
                          ("intended_window_end_utc", end)):
            if key in a:
                got = _cadence(a[key], f"arm {a['variant_id']} {key}") if key == "cadence_s" \
                    else _utc(a[key], f"arm {a['variant_id']} {key}")
                if got != want:
                    raise ManifestError(f"arm {a['variant_id']}: {key} differs from the campaign's; "
                                        "arms in one contrast must share cadence and window")
    if len(set(ids)) != len(ids):
        raise ManifestError("duplicate variant_id in manifest")

    loaded = {a["variant_id"]: _load_arm(a, base, start, end, cadence_s) for a in arms}
    present = [v for v in ids if loaded[v] is not None]
    absent = [v for v in ids if loaded[v] is None]
    expected = next(loaded[v]["expected"] for v in present) if present else 0
    if not present:
        raise ManifestError("no arm has data on disk")

    def frac(n):
        return n / expected if expected else None

    contrasts = {}
    for a, b in itertools.combinations(present, 2):
        va, vb = loaded[a]["valid"], loaded[b]["valid"]
        contrasts[f"{a}|{b}"] = dict(paired_slots=len(va & vb), paired_fraction=frac(len(va & vb)),
                                    dropped_valid_only_in_first=len(va - vb),
                                    dropped_valid_only_in_second=len(vb - va))
    complete = set.intersection(*(loaded[v]["valid"] for v in present))
    refs = {}
    for a in arms:
        refs.setdefault(a["reference_id"], []).append(a["variant_id"])
    kinds = {v: loaded[v]["evidence_kind"] for v in present}
    return dict(
        campaign_id=cid, campaign_id_uniqueness_scope="within this manifest only", protocol=protocol,
        expected_slots=expected, cadence_s=cadence_s,
        arms={v: dict(present=True, rows=loaded[v]["rows"], valid_slots=len(loaded[v]["valid"]),
                      valid_fraction=frac(len(loaded[v]["valid"])),
                      rows_absent=expected - loaded[v]["rows"],
                      rows_missing_sensor=loaded[v]["no_sensor"], rows_missing_reference=loaded[v]["no_ref"],
                      evidence_kind=kinds[v]) for v in present},
        absent_optional_arms=absent, contrasts=contrasts,
        all_arm_complete=dict(arms=present, slots=len(complete), fraction=frac(len(complete))),
        reference_sharing={r: v for r, v in refs.items() if len(v) > 1},
        reduced_coverage=bool(absent),
        synthetic_only=any(k == "synthetic" for k in kinds.values()), validates_thermal_model=False,
        limitation="Hashes are compared to the manifest's own claims; the manifest is not authenticated.")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("manifest", type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args(argv)
    try:
        if a.out.exists() or a.out.is_symlink():
            raise ManifestError(f"refusing to overwrite existing report {a.out}")
        try:
            manifest = json.loads(a.manifest.read_text())
        except (OSError, ValueError) as e:
            raise ManifestError(f"cannot read manifest: {e}") from None
        report = pair(manifest, a.manifest.resolve().parent)
        with a.out.open("x") as handle:     # "x": atomic refuse-before-write, also for dangling links
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write("\n")
    except (ManifestError, OSError) as e:
        print("REFUSED:", e, file=sys.stderr)
        return 2
    print(f"campaign {report['campaign_id']}: {len(report['arms'])} arms, "
          f"{report['all_arm_complete']['slots']}/{report['expected_slots']} all-arm complete slots"
          + (f", absent optional: {', '.join(report['absent_optional_arms'])}" if report["reduced_coverage"] else ""))
    return 3 if report["synthetic_only"] else 0


if __name__ == "__main__":
    sys.exit(main())
