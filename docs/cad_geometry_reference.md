# Geometry and thermal-input reference

[ROADMAP.md](../ROADMAP.md) is the only plan. This retains useful geometry and
input definitions from the retired CAD/FEA workstream, without its mandatory
solver, structural/modal, ruggedization or sealing campaigns. No design count,
fabrication or hardware inventory is approved here.

## Existing reproducible CAD

The [baseline source and checks](../cad/enclosure/v0/README.md) retain geometry,
independent oracle and acceptance evidence. Use [CAD_ITEMS.md](CAD_ITEMS.md) as
an interface/parts checklist and the [baseline template](../templates/baseline_system_description.md)
for actual specimen records. Geometry acceptance does not establish heat transfer,
reference quality, environmental qualification or permission to fabricate.

## Model variants and geometry inputs

These are model definitions and earlier candidate descriptions. V0P is the
same-geometry painted control; real paint may change emissivity as well as
absorptance. A V0P/V1 comparison changes a complete system, not just shielding.

| ID | Model definition | Use and limitation |
|---|---|---|
| V0 | Closed box with sensor coupling to the solar-loaded wall and internal heat sources. | Analytical baseline; actual specimen dimensions remain owner inputs. |
| V1 | Passive multi-plate shield around the sensor with a separate electronics compartment. | Candidate system comparison; multiple geometry and heat-coupling assumptions change together. |
| V2 | Aspirated sensor/shield model with an assumed airflow coefficient. | Numerical comparator; a calibrated, qualified physical reference is a separate requirement. |

Candidate geometry/input variables retained from the former proposal: shield color/surface finish (drives optical inputs), number of plates/cones, plate/cone spacing, vent opening area and orientation, passive vs. fan-driven airflow, sensor distance from electronics and battery, roof/overhang geometry, drain path and bottom openings, cable-gland and connector locations, enclosure internal volume, and internal heat-source magnitude.

The new rig inventory must identify its actual dimensions and construction. The existing accepted CAD has a separate geometry record; it is not evidence of which specimens will be used in the campaign.

## Reuse requirements

Record material, thickness, finish, optical properties, vents, sensor placement,
heat-source location and geometry uncertainty for the actual specimens. Identify
source geometry, units and revision; verify dimensions and STEP round-trip where
applicable. Keep missing dimensions unknown. Filament datasheets do not establish
surface optical properties, and supply power does not establish sensor-coupled heat.

A later higher-fidelity model requires an evidenced question and separate scope.
The [retained CHT methods reference](specs/study-b-cht/design.md) contains useful
verification and target-leakage corrections, not an active solver task.
[The former workstream](https://github.com/500ft/sensor-enclosure-thermal-design/blob/2beffdf412e57145062994e5626863de80438016/docs/cad_fea_plan.md) is preserved in git for provenance.
