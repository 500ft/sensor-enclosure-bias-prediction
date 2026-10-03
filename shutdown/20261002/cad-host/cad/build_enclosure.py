#!/usr/bin/env python
"""Author the V0 baseline enclosure in CadQuery, measure it, and REFUSE it on an oracle mismatch.

Non-interactive by construction: CadQuery is pure code, so there is no modal dialog to suppress and
no interactive session to own. Exit codes: 0 accepted, 3 mismatch (geometry wrong), 4 build error.
"""
import json
import os
import sys

import cadquery as cq

from oracle import expected

TOL_VOL_REL = 1e-6          # relative; CadQuery/OCP volumes are exact for prismatic + cylindrical
TOL_LEN_ABS = 1e-6          # mm


def build(g):
    L, W, H = g["outer_length"], g["outer_width"], g["outer_height"]
    t, ft = g["wall_thickness"], g["floor_thickness"]
    npw, vw, vh = g["vents_per_wall"], g["vent_width"], g["vent_height"]
    pitch, zc = g["vent_pitch"], g["vent_band_center_z"]
    d, sh = g["standoff_diameter"], g["standoff_height"]

    # open-top shell: outer block minus the internal cavity
    part = cq.Workplane("XY").box(L, W, H, centered=(True, True, False))
    part = part.cut(
        cq.Workplane("XY").workplane(offset=ft)
        .box(L - 2 * t, W - 2 * t, H - ft, centered=(True, True, False))
    )

    # vent slots through two opposite walls (+Y and -Y), a vertical stack centred on zc
    z0 = zc - (npw - 1) * pitch / 2.0
    cutters = []
    for i in range(npw):
        z = z0 + i * pitch
        for sign in (1, -1):
            cutters.append(
                cq.Workplane("XY")
                .box(vw, t * 3, vh, centered=(True, True, True))
                .translate((0, sign * (W / 2.0), z))
            )
    for c in cutters:
        part = part.cut(c)

    # sensor standoff boss on the floor
    part = part.union(
        cq.Workplane("XY").workplane(offset=ft).circle(d / 2.0).extrude(sh)
    )
    return part


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    g = json.load(open(os.path.join(here, "geometry.json")))
    exp = expected(g)
    out_dir = os.path.join(os.path.dirname(here), "out")
    os.makedirs(out_dir, exist_ok=True)

    try:
        part = build(g)
        solid = part.val()
        measured_vol = solid.Volume()
        bb = solid.BoundingBox()
        measured_bb = [bb.xlen, bb.ylen, bb.zlen]
        n_solids = len(part.solids().vals())
    except Exception as exc:                       # noqa: BLE001
        json.dump({"accepted": False, "stage": "build", "error": repr(exc)},
                  open(os.path.join(out_dir, "result.json"), "w"), indent=2)
        print("BUILD ERROR:", exc)
        return 4

    checks, ok = [], True

    def chk(name, got, want, tol, rel=False):
        nonlocal ok
        diff = abs(got - want)
        lim = tol * abs(want) if rel else tol
        passed = diff <= lim
        ok = ok and passed
        checks.append({"check": name, "measured": got, "expected": want,
                       "abs_diff": diff, "tolerance": lim, "pass": passed})

    chk("volume_mm3", measured_vol, exp["expected_volume_mm3"], TOL_VOL_REL, rel=True)
    for i, ax in enumerate("xyz"):
        chk(f"bbox_{ax}_mm", measured_bb[i], exp["bounding_box_mm"][i], TOL_LEN_ABS)
    chk("solid_count", n_solids, exp["solid_count"], 0)

    step_path = os.path.join(out_dir, "V0-baseline-enclosure.step")
    if ok:
        cq.exporters.export(part, step_path)
        # independent re-import check: read the STEP back and re-measure
        reimported = cq.importers.importStep(step_path).val()
        chk("reimported_volume_mm3", reimported.Volume(), exp["expected_volume_mm3"],
            1e-5, rel=True)

    result = {
        "accepted": bool(ok),
        "part_id": g["part_id"],
        "units": g["units"],
        "checks": checks,
        "expected": exp,
        "measured": {"volume_mm3": measured_vol, "bounding_box_mm": measured_bb,
                     "solid_count": n_solids},
        "step": step_path if ok else None,
        "evidence_note": ("Geometry accepted against an independent closed-form oracle. Every input "
                          "dimension is provisional_design, NOT a measurement of existing hardware. "
                          "This verifies the MODEL, not the physical enclosure."),
    }
    json.dump(result, open(os.path.join(out_dir, "result.json"), "w"), indent=2)
    print(json.dumps({"accepted": result["accepted"],
                      "volume_mm3": round(measured_vol, 4),
                      "expected_mm3": round(exp["expected_volume_mm3"], 4),
                      "bbox": measured_bb, "solids": n_solids}, indent=2))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
