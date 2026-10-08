# Enclosure — CAD item list

Prepared 2026-09-06 (America/New_York). **A list of planned parts and assemblies—not completed CAD, hardware or approval to fabricate/test.**

This is a retained parts/interface checklist. The [roadmap](../ROADMAP.md)
controls future work, and the [geometry reference](cad_geometry_reference.md)
links existing CAD checks. The earlier work-order IDs below are historical
cross-references, not active tasks, an actual rig inventory or fabrication approval.
Reuse inspected models and sourced vendor geometry where applicable.

## After inventory: baseline and passive shield

| Item to model or import | Existing work order | Purpose / boundary |
| --- | --- | --- |
| Existing enclosure body and lid | `EN-CAD-03` | Model the inspected baseline box, openings and internal component envelopes. |
| Painted-baseline configuration | `EN-CAD-03` | Reuse exactly the same geometry as the baseline; change only declared finish/coating metadata. This is not a second physical CAD design. |
| Passive radiation-shield plate stack and spacers | `EN-CAD-04` | Parameterize plate count, gaps and sensor stand-off using the existing design contract. |
| Sensor support and electronics mounting structure | `EN-CAD-04` | Separate the ventilated sensing zone from protected heat-producing electronics; preserve service access. |
| Cable-gland, lid/seal and drainage details | `EN-CAD-05` | Detail interfaces and routing without sealing off required sensing ventilation. |
| Co-location / comparison mounting bracket | `EN-CAD-05` | Define repeatable mounting datums for the enclosure and comparison sensor setup. |
| Complete enclosure/shield assembly and simplified analysis geometry | `EN-CAD-06`, `EN-CAD-07` | Release assembled/section views and a traceable defeatured export for later analysis; the latter is a derived model, not another manufactured part. |

## Optional later reference

| Item to model or import | Existing work order | Purpose / boundary |
| --- | --- | --- |
| Fan mount and active-aspiration flow-path configuration | `EN-CAD-08` | Only after documented low-wind/solar bias and an approved active-reference plan. |

## What to deliver for each applicable part or assembly

- Editable/source CAD or an authorized immutable CAD-document version; identify reused vendor geometry and its source.
- STEP export, with dimensions/units checked after reimport. Parameter-driven families also need the planned numerical geometry tests before model acceptance.
- A dimensioned drawing for custom fabricated parts, with material/process, critical fits and inspection datums; vendor hardware can use its sourced drawing.
- An assembly/section view showing how the part fits and which problem it addresses. Label all visuals CAD/design-only until corresponding evidence exists.

Geometry does not establish an IP rating, environmental qualification, ventilation performance or sensor accuracy. Same-geometry painted controls must remain separate from shield-geometry changes.

## Policy and scope

The owner authorized merging this inventory and the current PR documents to main on 2026-09-06 (America/New_York). No withheld details are restored, no model task is marked done and no hardware/fabrication/disclosure gate is closed by this placement decision.
