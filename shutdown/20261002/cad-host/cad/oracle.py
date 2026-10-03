#!/usr/bin/env python
"""Independent expected geometry for the V0 baseline enclosure.

Closed-form, computed from geometry.json WITHOUT using CadQuery. This is the oracle: the authoring
script's measured output is compared against these numbers and the part is REFUSED on a mismatch.
A clean rebuild is not evidence; the number is.

Both this file and build_enclosure.py read the same geometry.json, so they cannot disagree about
inputs -- only about geometry, which is the whole point.
"""
import json
import math
import sys


def expected(g):
    L, W, H = g["outer_length"], g["outer_width"], g["outer_height"]
    t, ft = g["wall_thickness"], g["floor_thickness"]
    nw, npw = g["vent_walls"], g["vents_per_wall"]
    vw, vh = g["vent_width"], g["vent_height"]
    d, sh = g["standoff_diameter"], g["standoff_height"]

    outer_vol = L * W * H
    cav_l, cav_w = L - 2 * t, W - 2 * t
    cav_h = H - ft                          # open top
    cavity_vol = cav_l * cav_w * cav_h
    shell_vol = outer_vol - cavity_vol

    n_vents = nw * npw
    vent_cut_vol = n_vents * vw * vh * t    # each slot cuts through one wall thickness
    vent_open_area = n_vents * vw * vh      # one face each, the through-opening

    standoff_vol = math.pi * (d / 2.0) ** 2 * sh

    return {
        "bounding_box_mm": [L, W, H],
        "solid_count": 1,
        "outer_volume_mm3": outer_vol,
        "cavity_volume_mm3": cavity_vol,
        "shell_volume_mm3": shell_vol,
        "vent_count": n_vents,
        "vent_cut_volume_mm3": vent_cut_vol,
        "vent_open_area_mm2": vent_open_area,
        "standoff_volume_mm3": standoff_vol,
        "expected_volume_mm3": shell_vol - vent_cut_vol + standoff_vol,
        "wall_thickness_mm": t,
        "sun_facing_projected_area_mm2": L * W,
        "_area_caveat": ("geometric only; the thermal model's A_proj/A_conv are EFFECTIVE coupled "
                         "areas and the mapping is UNRESOLVED"),
    }


if __name__ == "__main__":
    g = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "geometry.json"))
    print(json.dumps(expected(g), indent=2))
