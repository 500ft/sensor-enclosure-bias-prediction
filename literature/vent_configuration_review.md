# Vent configuration for the existing enclosure: literature review

The PI asked for the range of vent configurations for the lab's existing box:
how many holes, where and how large, plus internal layout. The goals are the
most air through the box, no water inside, and room for all the parts. The
owner relayed this request on 2026-10-26. The
[owner record](../docs/COLOCATION_OWNER_SESSION.md#current-blocker) holds the
request.

## Result

Most of the literature gives the direction of an effect, not a number for a
10 to 30 cm plastic box. No source tests hole patterns on a box this size in
outdoor wind and rain. The configurations in this note are candidates to
measure on the box. They are not a ranking.

Five rules have measured support:

1. Wind drives the flow. Wind pressure on a small box is in the pascal
   range. Buoyancy across 10 cm at a 2 K difference is about 0.008 Pa (own
   estimate, ρgHΔT/T). Air speed inside a louvred screen averaged 7% of the
   10 m wind, and the air inside was nearly still (below 0.025 m/s) 10.6% of
   the time [burt2022]. A design that only works in calm air will rarely see
   calm air, and a design that relies on buoyancy will rarely get it.
2. The smaller vent group limits the flow. Making one group bigger than
   the other adds little [linden1990]. Equal inlet and outlet area gave the
   lowest temperature rise in a heated cabinet [misale1997]. For buoyancy-driven
   flow, the height between the inlet and outlet group centres sets the driving
   pressure [linden1990; misale1997].
3. Water enters where the pressure difference across an opening is high and
   the opening faces the wind. One louver rejected 98.2% of wind-driven rain
   with no air drawn through. It rejected 79.0% at 1.5 m/s and 17.7% at
   3.5 m/s face velocity [freeth2015bsria]. A gooseneck vent took the most
   water when its opening faced the wind [ganchowdhury2009vents]. The top
   windward edges and corners of a body get wettest; an overhang shelters the
   area right under it [blocken2004].
4. A second stage behind the opening cuts water entry more than open area
   does. An insect screen behind a downward-facing soffit vent cut water entry
   by 79 to 86%, and deflectors by 69 to 79%. Open area did not predict
   which vent let in more water [masters2006soffit].
5. A fan-driven PM sensor has almost no pressure margin. The PMS5003 fan
   makes about 3.5 Pa. A 1.0 Pa restriction at its inlet cut the reported
   particle count by 30% and a 2.5 Pa restriction by 83% [ouimette2024]. Small
   holes or mesh directly in front of the PM inlet change the measurement.

Board heat inside a small housing can bias the temperature reading by several
degrees. PurpleAir units read 3.77 °C warm on average against shielded
loggers, with the largest error at night [tse2025].

## Design variables

| Variable | What the literature supports | Strength | Conflict |
|---|---|---|---|
| Total open area | Inlet and outlet groups of equal area; the smaller group limits flow [linden1990; misale1997]. Openings at least as large as the sensor's own inlet and outlet [plantower2016; sensirion2021sen5x]; one node made its venting larger than the sensor vent to cut resistance [bainomugisha2023]. | Measured for buoyancy in tanks and cabinets; manufacturer rule for sensors | More area lets in more water and dust; rain-rated louvers give up free area and add pressure drop [smardo2018amca] |
| Inlet and outlet height | Low inlet, high outlet. Buoyancy flow rises with the square root of their vertical separation [linden1990]. | Measured, still air only | A high outlet is the opening most exposed to rain [blocken2004] |
| Number of holes against hole size | For openings above about 10 mm the orifice model applies, and only total area counts [karava2004]. Holes of a few mm at pascal-range pressures fall outside that model. | No direct test found | Small holes resist water and insects but add flow loss |
| Face and orientation | Discharge coefficient falls as wind swings along the face: 0.58 to 0.1 from 0° to 90° in one data set [karava2004]. Inflow coefficients were lower for low openings [ohba2006]. Openings on opposite faces give cross-flow. | Measured at building model scale | The windward face also takes the rain |
| Downward-facing openings | Common for AQ nodes [ouimette2024; johnston2019]. For water, results disagree: 0.3 to 8.6% of incident rain entered downward soffits in one study [masters2006soffit] and none in another [ganchowdhury2009vents]. | Common practice; mixed data | Recent sensor guidance warns against pointing a PM sensor's own openings straight down [sensirion2021sen5x, SEN6x note] |
| Hood, overhang or drip edge | Sheltered zone directly under an overhang stays driest; protection weakens at its edges and in high wind [blocken2004]. | Building scale, field and CFD | Adds size; can trap warm air |
| Screen or mesh | Greenhouse insect mesh pressure loss grows as open-area ratio falls, with the densest meshes at 3 to 4 times the loss of the most open ones [valera2006]. A screen behind a vent cut water entry [masters2006soffit]. | Measured in forced flow above 0.1 m/s | At buoyancy speeds a mesh may stop most of the flow (own estimate: about 0.16 Pa at 0.05 m/s against 0.008 Pa available) |
| Membrane vent (ePTFE) | Airflow and water-entry pressure trade: about 4 times the water resistance for 12 times less air in one vendor's line [porexvirtek]. At passive pressures a membrane passes hours per air change for a 1 L box (own estimate from [porexvirtek] data). Membranes equalize pressure during temperature swings [gore2011cycling]. Humidity inside lags outside by a time constant set by opening length and area [staliulionis2016]. | Manufacturer data | Fits the sealed electronics section, not sensor ventilation |
| Drain hole | IEC 60529 water tests accept some entry as long as water does not collect and drains away harmlessly. A drain at the low point is part of that design (test clause 14.3, as reproduced by third-party labs). | Standard practice | A drain is also a leak path for air and insects |
| Internal partition | Sensor section sealed from electronics section; PM sensor inlet sealed from its outlet [johnston2019; sensirion2021sen5x; plantower2016]. T/RH sensor walled into a small volume with its own opening, PCB slots around it, heat sources above it [sensirion2024design; bosch2018bme280]. | Manufacturer guidance and one node's design history; no published effect size | Partitions use space |
| Sun | Shade the sensor from direct sun [sensirion2021sen5x]. Covered by the repo's earlier shield review. | Supported | |

## Candidate configurations for the existing box

The deployed box has no measured geometry in this repo yet. A lab member shared
an Onshape model on 2026-10-26 that has not been reviewed. Sizes below are set
relative to the box and its sensors. They become dimensions once the box is
measured. C0 is the PI's first-stage configuration; C1 to C5 are options for
the one model-suggested modification.

| ID | Configuration | Expected gain | Main risk |
|---|---|---|---|
| C0 | As deployed | Reference | Unknown |
| C1 | Inlet holes on the bottom face only, total area at least the PM sensor's own inlet plus outlet; no top or side holes | Lowest water entry | Little flow in calm air; flow depends on wind under the box |
| C2 | Bottom inlet group plus an outlet group high on a side face under a hood or drip lip; equal areas | Buoyancy path plus wind cross-flow | Hooded outlet still exposed in oblique wind |
| C3 | Side vents on two opposite faces, low and high, each under an overhang | Most wind-driven exchange | Windward face takes rain; needs a second stage |
| C4 | C2 or C3 with insect mesh or a baffle behind each opening | Water and insect protection | Mesh flow loss at low speed; one baffle in [masters2006soffit] performed worst |
| C5 | Any of C1 to C4 with a partition: sealed electronics section with a membrane vent and drain, separate ventilated sensor section with heat sources above it | Smaller self-heating bias | Less usable volume |

## Measurements that decide between them

Each test can overturn a rule above for this box.

1. Air exchange per configuration by CO₂ tracer decay. Use the CCI fit method
   (at least 20 points, R² above 0.990, mixing fan off after the first minutes)
   with a test length set by the fast exchange of a vented box
   [tetreault2023cci].
2. The same test with an external fan at several wind speeds and at 0°, 45°
   and 90° to the vent face, plus one calm case with lamp heating.
3. Water entry: wind plus spray at the same three angles, water collected by
   weight. Also an IPX3 or IPX4 style spray, judged by whether water collects
   and drains, and a hot-box spray to check for water drawn in on cooling.
4. Temperature and RH offset and step-response time inside the box against a
   shielded reference, with electronics on and off and with and without the
   partition.
5. PM count with the sensor in open air against inside each configuration, to
   catch inlet restriction and recirculation. Closed boxes read PM10 differently
   from an open one in one field check [schilt2023].

Results 1, 2 and 4 also feed the repo's thermal model. The model's airflow
coefficient is the quantity that changes between configurations.

## Gaps

- No source measured air exchange against hole count and size on a small box
  outdoors.
- No source tested hoods, drip lips or downward holes on a box this size in
  wind-driven rain.
- Mesh pressure loss below 0.1 m/s is an extrapolation.
- The SEN6x note (2026) and older Sensirion and IQAir guidance disagree on
  facing sensor openings down.

## Sources

Full citations are in [references.bib](../paper/references.bib); per-source
notes are in [ProConsList](../ProConsList/README.md). Access level matters:
[karava2004] was read as the authors' conference version, the IEC 60529 text
was not accessed, and items marked UNVERIFIED in the source notes are not used
above.
