# Sensor-Enclosure-Thermal-Design — CAD

Parametric CAD for the enclosure study. Companion to the research repository
`500ft/sensor-enclosure-thermal-design`.

> **These are DESIGN dimensions, not measurements.** Every value in `cad/geometry.json` is
> `provisional_design` on the `design_then_inspect` route: the designer chooses, and the built part
> is inspected later. **Nothing here is an as-built dimension of existing hardware**, and none of it
> may be copied into the research repository's parameter register without inspection.

## What was built

`out/V0-baseline-enclosure.step` — V0 baseline enclosure: open-top shell, 170 × 170 × 170 mm,
3 mm walls, 16 vent slots through two opposite walls, one sensor standoff boss.

**Accepted 2026-09-26** against an independent oracle. All six checks passed:

| Check | Measured | Expected |
|---|---|---|
| volume | 416 515.43339 mm³ | 416 515.43339 mm³ |
| bbox x / y / z | 170 / 170 / 170 mm | 170 / 170 / 170 mm |
| solid count | 1 | 1 |
| **STEP re-import volume** | 416 515.43339 mm³ | 416 515.43339 mm³ |

## Method

`cad/oracle.py` computes the expected geometry **closed-form, without CadQuery**;
`cad/build_enclosure.py` authors the part and **refuses it on a mismatch** (exit 3). Both read the
same `geometry.json`, so they cannot disagree about *inputs* — only about *geometry*, which is the
point. A clean rebuild is not evidence; the number is.

**Parameter re-drive proved, not assumed.** Changing `vent_width` 40 → 55 mm moved the volume
416 515.4334 → 413 635.4334 mm³, a difference of exactly **2 880 mm³** = 16 slots × 15 × 4 × 3 mm,
with the oracle independently predicting the new value. Baseline restored and re-verified afterwards.

*An earlier re-drive attempt appeared to succeed while the volume did not move — a PowerShell quoting
error meant the parameter never reached the file. The oracle caught it. That is exactly the failure
mode this method exists to prevent.*

## Reproduce

```bash
python cad/oracle.py cad/geometry.json      # expected values, no CAD dependency
python cad/build_enclosure.py               # authors, measures, refuses on mismatch
```
Built on the CAD host (Windows, Python 3.12.10, CadQuery 2.8.0). **Fully non-interactive** — CadQuery
is pure code, so there is no modal dialog to suppress and no interactive session to own.

## What this does and does not establish

- **Does:** the model is parametric, its geometry matches an independent closed-form expectation, and
  it round-trips through STEP.
- **Does not:** say anything about the physical enclosure. The dimensions are design choices pending
  `EN-M01` inspection. The thermal model's `A_proj` / `A_conv` are **effective coupled** areas; the
  mapping from these geometric areas is **unresolved** and must be written down before any as-built
  prediction.
