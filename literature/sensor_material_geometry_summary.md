# Sensors, Materials, Geometries, and Experimental Setups in the Current Literature

This document separates information explicitly reported by each paper from information that the paper does not provide. A commercial sensor box should not be assigned a material unless the publication or its cited hardware documentation identifies that material.

## Literature-by-Literature Summary

### Theisen et al. (2020): 3D-Printed Automatic Weather Station

**Sensors**

- MCP9808: primary air-temperature sensor
- HTU21D: relative humidity and secondary temperature
- BMP280: atmospheric pressure and secondary temperature
- SI1145: ultraviolet, visible-light, and infrared-light counts
- Hall-effect sensor: 3D-printed cup anemometer
- Hall-effect rotary sensor: 3D-printed wind vane
- Hall-effect sensor: 3D-printed tipping-bucket rain gauge
- Secondary temperature sensor inside the Raspberry Pi box

**Materials**

- More than 100 off-white ASA 3D-printed parts
- Gray ASA rain-gauge funnel because off-white ASA was unavailable
- Polyurethane coating on the printed rain-gauge funnel
- Standard PVC pipe for the station frame
- Commercial electrical junction box for the Raspberry Pi
- Opaque plastic cut from a frozen-meal tray for the UV sensor cover
- PTFE filter over the HTU21D sensor
- Conformal coating on temperature, humidity, pressure, and UV sensor boards
- Silicone caulk used to repair the rain-gauge funnel

**Geometry and arrangement**

- Integrated 3D-PAWS weather station on a tripod-like PVC frame with three concrete footings
- Naturally aspirated radiation shield at 1.5 m for temperature, RH, and initially pressure
- Wind and UV sensors on a crossbar at approximately 2 m
- Tipping-bucket rain gauge at approximately 0.3 m
- Electrical junction box houses the Raspberry Pi; BMP280 was later moved into this box

**Experimental setup**

- Eight-month outdoor deployment beside an Oklahoma Mesonet station
- Measurements compared with maintained commercial reference instruments
- Main enclosure-related finding: naturally aspirated temperature measurements improved as wind speed increased, demonstrating the importance of airflow
- Main durability findings: corrosion, moisture degradation, loose printed fasteners, broken printed parts, yellowed adhesive, and intermittent connections

### Botero-Valencia et al. (2022): 3D-Printed Radiation Shields

**Sensors**

- Three identical SHT10 temperature and relative-humidity sensors with outdoor covers
- Vantage Pro station used as the reference
- Particle Argon Wi-Fi microcontroller used to acquire and upload data

**Materials**

- Orange PLA radiation shield
- White ASA radiation shield
- One-inch PVC pipe and PVC tees for the test structure
- M3 metal spacers and screws
- IP69 electronics box and PG7 enclosure gland

**Geometry and arrangement**

- Passive, naturally ventilated cone-stack radiation shield
- Six truncated cones: five perforated cones and one solid top cone acting as a roof
- Cones separated by 20 mm M3 metal spacers
- Central openings provide airflow and a wiring path
- Sensor support mounted on the second cone from the bottom
- One-inch PVC coupling at the base
- Modular geometry allows the number of cones and cone spacing to be changed

**Experimental setup**

- One exposed SHT10 sensor, one SHT10 inside a PLA shield, and one SHT10 inside an ASA shield
- All three mounted on a PVC structure and compared with the Vantage Pro reference
- Outdoor temperature/RH comparison plus 30-day and 90-day material-weathering tests
- Main finding: both shields greatly reduced solar-radiation error compared with the exposed sensor; ASA was preferred because of UV resistance and durability

### Tatsumi et al. (2021): Low-Cost Hydrometeorological Measurement System

**Sensors**

- LM60BIZ: air and soil temperature
- YL-69: soil moisture
- G2711-01 GaAsP photodiode: photosynthetic photon flux density proxy
- Arduino Uno, GPS module, and micro-SD storage

**Materials**

- The paper describes a 3D-printed "silicon case" protecting and insulating the board
- Its bill of materials lists 180 g of unspecified 3D-printer resin
- The exact polymer or resin chemistry is not reported
- A handmade cover was used for the GaAsP photodiode, but its material is not specified

**Geometry and arrangement**

- Compact 100 x 100 mm custom circuit board
- Rectangular protective case approximately 30 x 110 x 110 mm
- External sensors connected to detachable terminal blocks
- Solar panel, charge controller, and battery used for outdoor power

**Experimental setup**

- Grass-field deployment with one-minute sampling
- Air and soil temperatures measured for 30 days; soil moisture and PPFD measured for 19 days
- Compared against TR-72wb, TR-71wb, and LI-190R commercial reference instruments
- Separate PPFD tests compared uncovered and covered sensor response

### deSouza et al. (2022): Calibration of the Love My Air Network

**Sensors**

- 24 Canary-S commercial sensor boxes
- Plantower PMS5003 optical PM sensor
- Integrated temperature and relative-humidity sensing
- Cellular data upload

**Sensor-box material**

- Not reported in the paper

**Geometry and arrangement**

- Commercial Canary-S outdoor sensor-box geometry; detailed internal and external geometry is not reported

**Experimental setup**

- Sensors deployed outside public schools across Denver
- Seven sensor boxes co-located with five FEM reference-monitoring sites
- Minute-level measurements collected from January through September 2021 and aggregated to hourly values
- Calibration models evaluated for transferability across time and space

### Clements et al. (2017): Workshop Summary

**Sensors**

- No single sensor system was built or tested
- Discusses optical PM sensors, electrochemical gas sensors, metal-oxide gas sensors, and multi-sensor air-quality boxes generally

**Sensor-box material and geometry**

- No single enclosure material or geometry is specified

**Experimental setup**

- This is a workshop-summary and best-practices paper, not a single controlled experiment
- It synthesizes practitioner experience from laboratory tests, co-locations, community deployments, mobile deployments, and sensor networks
- Relevant design lesson: enclosure air-exchange rate and internal heat can alter measurements; temperature and RH should be measured close to the pollutant sensors and in the ambient air

### Giordano et al. (2021): Review of Low-Cost PM Sensors

**Sensors**

- No single sensor box or model is the subject of the paper
- Reviews low-cost optical particulate-matter sensors and their calibration challenges

**Sensor-box material and geometry**

- No single enclosure material or geometry is specified

**Experimental setup**

- Literature review and best-practices synthesis
- Examines results from laboratory evaluation, reference-monitor co-location, and network deployment studies
- Relevant design lesson: PM response depends on humidity, temperature, aerosol source/composition, and sensor age; packaging and airflow can affect performance

### Vajs et al. (2021): DunavNET ekoNET AQ10x Calibration Study

**Sensors**

- Alphasense CO-B4
- Alphasense NO2-B43F
- Alphasense SO2 sensor; exact model not identified in the article text
- Alphasense O3 sensor; exact model not identified in the article text
- Bosch BME280: temperature, relative humidity, and pressure
- Plantower PMS7003: PM1, PM2.5, and PM10

**Sensor-box material**

- Commercial DunavNET ekoNET AQ10x outdoor station; enclosure material is not reported

**Geometry and arrangement**

- Commercial outdoor air-quality station; detailed enclosure and airflow geometry is not reported

**Experimental setup**

- One low-cost station co-located with one Serbian public automatic monitoring station
- One-minute low-cost measurements averaged to match hourly reference data
- Linear regression, multiple linear regression, and machine-learning corrections evaluated using temperature and RH

### Grimsley et al. (2021): EnviSense Low-Power Hydrological Nodes

**Sensors**

- MaxBotix outdoor ultrasonic range sensor for non-contact stream level, depending on deployment
- SDI-12 vented pressure transducer for submerged water depth, depending on deployment
- Internal temperature, humidity, and barometric-pressure sensors for context and device health
- Battery voltage and current monitoring
- GPS module
- Semtech SX1276 LoRa radio

**Materials**

- All logger hardware is enclosed in a commercial IP67-rated enclosure
- Exact enclosure polymer or metal is not reported
- Four sealed ports are provided for the LoRa antenna, GPS antenna, external ultrasonic or SDI-12 sensor, and device management
- Device-management port has a clear removable cap

**Geometry and arrangement**

- Sealed rectangular field-logger enclosure connected to an external stream-level sensor
- Electronics remain protected while the ultrasonic sensor or pressure transducer interfaces with the environment
- Modular external ports support different sensor types

**Experimental setup**

- More than 12 nodes deployed at two Northern California locations
- Six months of continuous field measurement discussed
- LoRaWAN gateway and server infrastructure used for remote data and configuration
- Powered by a 6600 mAh LiPo battery; study evaluates power use, communication reliability, and sampling intervals

### Deployment and Evaluation of AirSensEUR Systems (2023)

**Sensors**

- Alphasense NO2-B43F
- Alphasense CO-A4
- Alphasense NO-B4
- ELT D-300 CO2 sensor
- Alphasense OX-A431 ozone sensor
- Alphasense OPC-N3 optical particle counter for PM1, PM2.5, PM10, and particle counts
- Air temperature, relative humidity, and atmospheric pressure sensors; exact models not stated

**Sensor-box material**

- AirSensEUR open sensor boxes were used, but the paper does not state the enclosure material

**Geometry and arrangement**

- Ten complete AirSensEUR boxes were mounted together on top of a roadside reference station for co-location
- Seven units were later distributed to roadside sites
- Detailed enclosure and airflow geometry is not reported in this paper

**Experimental setup**

- Approximately five-week pre-deployment co-location at Schancheholen, Norway
- Grimm EDM180 and Teledyne API T200 used as reference instruments
- Roadside network deployment from November 2019 through May 2020
- Post-deployment comparison used to identify drift, failures, and humidity effects

## Additional Literature Added in June 2026

| Paper | Sensors | Reported material / geometry | Experimental contribution |
|---|---|---|---|
| Tarara and Hoheisel (2007) | Same temperature-sensor type across shields | Reflective foil insulation; plate, stacked-plate, cone, tube, rocket, pagoda, and perforated variants | Isolates geometry effects; stacked plates outperform tubes; open bottoms and weak ventilation increase warm bias |
| Holden et al. (2013) | Low-cost temperature sensors, including LogTag units | Folded white corrugated-plastic Gill-style plates | Demonstrates a roughly USD 3 shield performing similarly to a commercial passive shield |
| Lazarescu (2015) | NTC temperature nodes, low-power radio, gateway health/power sensing | Protective resin, compact downward-vented package, sealed gateway package, divided wooden housing | Shows how heat, solder fatigue, RF layout, charging, and failed-node behavior limit autonomy |
| Daepp et al. (2022) | PM2.5, T, RH, pressure, optional O3/NO2/SO2/CO | Custom modular solar-powered urban box; exact material and airflow path not reported | 115-device deployment with more than 90% expected sensor-hours collected |
| Liu et al. (2023) | Pt100 | Silver-coated aluminum plates, black inner surfaces, white-resin annular plates, eight vents, truncated-cone reflector | Connects coating, reflected radiation, mixed materials, and vent geometry |
| García Izquierdo et al. (2024) | 41 calibrated Pt100 thermometers and complete manufacturer systems | Ten active/natural shield models, including multiplate and Stevenson-screen arrangements | Fourteen-month Arctic intercomparison with accuracy and operational-failure evidence |
| Diez et al. (2024) | 43 commercial systems containing 119 gas and 118 PM sensors | Proprietary commercial protective cases | Three-year comparison of stability, relocation, manufacturer corrections, and uncertainty |
| Deford et al. (2025) | Compact temperature sensor and 5 V fan | White PLA; double-wall 90-degree elbow, insect screen, central sensor support, fan diffuser | Directly tests the accuracy-versus-power tradeoff of low-cost aspiration |
| Winter et al. (2025) | Alphasense NO2-B43F, Ox-B431, NO-B4, CO-B4 | BEACO2N node packaging not described in detail | Shows calibrated sensing can remain stable for three years while mechanical/electrical failures occur first |
| Jin et al. (2026) | Thin-film Pt100 in copper spherical shell | Square plates, bowl-cover shrouds; CFD comparisons of plastic, wood, Fe-Ni alloy, and aluminum | Recent material-and-airflow geometry optimization with outdoor validation |


## Direction-A Competitor Sources Added September 2026 (full text read)

All six were read in full on 2026-09-22 (PDF/HTML; see `evidence/week-2026-09-21/day2.md`). None
predicts enclosure bias before fabrication; internal dissipation is absent from four and wall
conduction from all six. Two bibliographic corrections were made against the earlier abstract-level
scan: the direct competitor is **Bernard et al. 2019** (not "Barbaresco"), and the PurpleAir T/RH
paper is **Couzo, Valencia and Gittis 2024** (not "Cha"); Barkjohn et al. 2021 contains no own T/RH
bias measurement.

| Paper | Sensors | Reported material / geometry | Experimental contribution |
|---|---|---|---|
| Bernard et al. (2019) | PT100 in 12 naturally ventilated WMO shelters | Wood/plastic/steel/fiberglass/ABS-aluminum per type; per-type volume and surface tabulated; no thickness or optics | Two-coefficient energy-balance model (response time, radiation gain) fitted per built shelter; ~15 % (0.07 K) RMSE gain over empirical schemes |
| Nakamura and Mahrt (2005) | HOBO thermistor in a Davis 7714 vs aspirated RTD | Multiplate 0.188 x 0.213 m plates, 7 cm interior; material not reported | Single forcing ratio X = Rad/(rho Cp T U) explains 98 % of daytime error; independent-year check 0.29 -> 0.13 C RMSE |
| von Rohden et al. (2022) | Vaisala RS41 bare sensor + boom | Not reported | Lab dT(p, v) surface, u < 0.2 K (k=2); dT linear in irradiance, ~v^-b |
| Barkjohn et al. (2021) | PurpleAir PA-II under a PVC cap | PVC cap only | US-wide PM2.5 correction; T/RH bias quoted secondhand only |
| Couzo et al. (2024) | One PurpleAir PA-II vs Campbell 107 / Vaisala HMP45C | 85 x 85 x 125 mm white plastic shell, bottom open | +2.6 C / -17.4 % RH bias over 553 d; bias grows 1.8 -> 4.2 C with ambient temperature |
| Ishizuka et al. (2012) | Heated model electronics casing, 14 thermocouples | 220 x 230 x 310 mm, 10 mm plastic wall; bottom inlet, variable side outlet | Internal air rise vs vent porosity, outlet height and 6-40 W; chimney-balance parameter X = Re beta^2/(1-beta) |

## Additional Literature Added in July 2026 (field reliability and data yield)

| Paper | Sensors | Reported material / geometry | Experimental contribution |
|---|---|---|---|
| Szewczyk et al. (2004) | ~150 habitat-monitoring motes (temperature/humidity/light class) | Weatherproofed mote packaging; full packaging detail is in companion papers and was not re-verified here | Canonical analysis of a real 4-month deployment: lifetime, node mortality, and data yield reported as primary systems results |
| Barrenetxea et al. (2008) | SensorScope solar-powered environmental stations (meteorological suite) | Mast-mounted outdoor stations; packaging detail in project papers, not re-verified here | Deployment-practice guide from repeated campaigns: a functioning network does not guarantee meaningful data; pitfalls span development, packaging, power, and on-site validation |
| Feinberg et al. (2018) | Low-cost PM, O3, and NO2 sensors in triplicate | Sensor packages as shipped; enclosure detail not re-verified here | 7-month FEM collocation in Denver evaluating data completeness explicitly alongside correlation and trend reproduction |

## Consolidated Existing Material Options

The following materials are explicitly present in the current literature set.

| Material or component | Reported use | Main benefit | Main limitation or concern |
|---|---|---|---|
| ASA, preferably white/off-white | Printed shields, frame parts, rain gauge, complete station parts | Better UV and outdoor-weather resistance than PLA; light color reduces solar heating | Higher print temperature; warping; printed fasteners and low-infill parts can still fail |
| PLA | Printed radiation shield | Low cost, accessible, easy to print | UV and thermal degradation; can become brittle outdoors |
| Unspecified 3D-printer resin / paper-described silicon case | Compact electronics housing | Insulates and protects a custom board | Exact weatherability cannot be assessed because chemistry is not reported |
| PVC pipe and fittings | Structural frame, mounting pole, shield coupling | Low cost, easy assembly, weather-resistant structure | Not a precision enclosure; joints and mounting stiffness must be checked |
| Commercial IP67 enclosure | EnviSense electronics and battery protection | Strong protection against dust and water; suitable for remote deployment | Sealed boxes can trap heat and cannot expose ambient sensors without external probes or vents |
| Commercial IP69 box | Electronics box in radiation-shield experiment | High ingress protection | Material and internal thermal behavior not reported |
| Electrical junction box | Raspberry Pi/electronics housing | Readily available, serviceable, weather protection | Material and thermal behavior not reported; internal heating possible |
| Polyurethane coating | Seal imperfections in printed rain-gauge funnel | Improves water sealing | Coating aging and optical/thermal effects need checking |
| Conformal coating | Protect exposed sensor circuit boards | Reduces moisture-related degradation | Can affect sensor response if applied over the sensing element |
| PTFE filter or opaque PTFE/plastic cover | Sensor contamination and UV protection | Hydrophobic and protective | Dust accumulation and cover aging can still bias readings |
| Silicone caulk, cable glands, sealed ports | Repairs, wiring penetrations, ingress control | Improves water resistance | Repairs may age; poor placement can trap water or block airflow |
| Reflective foil insulation | Low-cost passive shield prototypes | High albedo and low emissivity; inexpensive and easy to shape | Durability and structural rigidity may be limited |
| White corrugated plastic sheet | Folded low-cost Gill-style shield | Very low cost, lightweight, easy construction | UV life and build repeatability need verification |
| Silver-coated aluminum with black inner finish | Multilayer naturally ventilated shield | Reflects external radiation while absorbing internal reflected radiation | Oxidation/coating degradation and mixed-surface heating require testing |
| White PLA aspirated housing | Double-wall fan-aspirated shield | Easy, low-cost FDM fabrication and low solar absorption | Long-term weatherability, glue, fan, and exposed circuits limit autonomy |

## Consolidated Existing Geometry Options

| Geometry | Literature example | Intended function | Important tradeoff |
|---|---|---|---|
| Six-layer truncated-cone radiation shield | Botero-Valencia et al. | Block direct solar radiation and rain while permitting passive airflow | Performance depends on cone spacing, color, and wind |
| Naturally aspirated multi-plate radiation shield | Theisen et al. | Protect temperature/RH sensors while allowing ambient airflow | Temperature error increased during low-wind conditions |
| Actively aspirated shield | Oklahoma Mesonet reference in Theisen et al. | Maintain controlled airflow around temperature/RH sensors | Better airflow but requires fan power and maintenance |
| Sealed electronics box plus external sensor region | EnviSense and partly Theisen et al. | Separate weather-sensitive electronics from exposed sensing | External ports/probes and cable seals add complexity |
| Compact rectangular 3D-printed logger case | Tatsumi et al. | Protect and insulate an Arduino data logger | Suitable for electronics, not necessarily for ambient-air sensors |
| Integrated 3D-printed weather station | Theisen et al. | Combine wind, rain, radiation, and atmospheric sensing | More printed moving parts and connectors increase failure modes |
| Commercial outdoor air-quality box | Canary-S, AQ10x, AirSensEUR | Package PM/gas sensors, power, communication, and ambient sensors | Material and airflow path often undocumented; calibration can hide design effects |
| External-probe modular logger | EnviSense | Allow sealed electronics to use ultrasonic or submerged sensors | Best for sensors that do not need air exchange inside the electronics box |
| Reflective stacked-plate shield | Tarara and Hoheisel; Holden et al. | Low-cost passive radiation blocking with crossflow | Plate overlap and spacing outperform open or weakly perforated tubes |
| Double-wall elbow aspirated shield | Deford et al. | Block direct radiation/rain and force air past sensor | Fan improves low-wind accuracy but consumes power and adds a failure mode |
| Multilayer mixed-finish shield with eight vents | Liu et al. | Block downward/upward radiation and promote natural ventilation | Complex mixed-material assembly and coating durability |
| Bowl-cover flow-guided shield | Jin et al. | Guide passive flow through a protected central cavity | Larger and more complex than conventional plate shields |

## Recommended Material and Geometry Shortlist for the Lab

Based on the current literature, the first comparison should avoid testing too many unrelated options. A useful shortlist is:

1. **Current lab box**, unchanged, as the baseline.
2. **White ASA passive radiation shield plus sealed electronics box**, representing the most directly supported outdoor printed design.
3. **Current enclosure material painted or coated white**, if changing only solar absorptance is feasible.
4. **Sealed IP-rated electronics compartment plus externally ventilated sensor compartment**, representing the modular EnviSense-style separation of electronics and sensing.
5. **Optional active aspiration variant**, only if baseline results show strong low-wind or solar-heating bias and the power budget can support a fan.

The key geometry variables to record or control are:

- shield color and surface finish;
- number of plates or cones;
- plate/cone spacing;
- vent opening area and orientation;
- passive versus fan-driven airflow;
- sensor distance from electronics and battery;
- roof/overhang geometry;
- drain path and bottom openings;
- cable-gland and connector locations;
- enclosure volume and internal heat sources.


## Model-Input, Printed-Material and Methodology Sources Added September 2026 (full text read)

Twenty-seven sources added 2026-09-22 to close gaps that breadth in the shield literature could not
fill: the **uncited physical constants in `thermal_bias.ASSUMPTIONS`**, the **measured properties of
printed polymers** underpinning the Biot claim, the **origin papers** behind the quoted PurpleAir
bias, and the **methodology** Study A and the pilot rely on. Twenty-five were read in full; two
(`churchill1975`, `barcohen1984`) are paywalled and are recorded as **full-read pending with no
content attributed**. See `literature/REVIEW_2026-09-22.md` for the thematic review and the
model-input provenance table.

| Paper | Sensors | Reported material / geometry | Experimental contribution |
|---|---|---|---|
| Berdahl and Martin (1984) | LBL spectral sky radiometer, pyrgeometer | n/a | Clear-sky emissivity as a function of dewpoint from 30,835 observations; **refutes a fixed sky-temperature depression** |
| Formetta et al. (2016) | Eppley pyrgeometers +/-3 W/m2 | n/a | 10 clear-sky parameterizations benchmarked at 24 US stations; best RMSE <= 39 W/m2; recalibration halves it |
| Defraeye et al. (2011) | CFD + review of measured correlations | Building facades, cube | **Provenance of `h = a + b*U`**: Juerges `4.0U + 5.6`, U <= 5 m/s, free-stream; U10-referenced slopes are 0.90-2.9 |
| Berdahl and Bretz (1997) | Spectrophotometer + integrating sphere; emissometer | Roof coatings, shingles, paints | Measured alpha: black 0.95, white coatings 0.15-0.26; `h_r = 5.5 W/m2K` at eps 0.9; h_c dominates uncertainty |
| Barreira et al. (2021) | Emissometer ASTM C1371 (+/-0.02) | Nine pigmented polymer films | Measured polymer emissivity **0.86-0.89**, below the usual 0.90-0.95 band; colour and gloss barely matter |
| Levinson et al. (2010) | Numerical; ASTM E903/C1549/E1918 | Roofs, pavements | Solar absorptance is spectrum-dependent; **0.6 K of surface temperature per 10 W/m2** |
| Tychanicz-Kwiecien et al. (2025) | Guarded heat flow, ASTM E1530 | PLA/PET-G/ABS, 40-100 % infill | Measured printed k and its ~30 % fall from 100 % to 40 % infill |
| Janek and Hardon (2026) | Custom transient pulse, GUM k=2 | FDM ABS, 1.5 mm, two directions | **Through-layer 0.1039 vs in-plane 0.1664 W/mK, anisotropy 1.60** |
| Baraboi et al. (2026) | Guarded hot plate, ASTM C177 | PLA, PLA Aero, PETG, PET-CF | Printed PLA **0.267**, PETG **0.290**, foaming PLA 0.114 W/mK with k=2 uncertainty |
| Lopes et al. (2023) | ISO 9869-1 in an ASTM C1363 hotbox | PET-G, 12 patterns at 25 % infill | Pattern alone moves effective k by 82 % at fixed density |
| Rodriguez et al. (2023) | DTC-25, ASTM E1530 | PLA, ABS, PEEK, TPU, ULTEM | Independent cross-lab check: printed PLA and ABS both 0.22 +/- 0.06 W/mK |
| Morgan et al. (2017) | Gier-Dunkle reflectometer (LANL report) | Printed ABS and PLA coupons | Only measured emissivity of printed polymer: ~0.88-0.92, unchanged by build orientation |
| Amendola et al. (2021) | Spectrophotometer 400-1300 nm | 25 PLA/ABS filaments, 0.23-0.58 mm | Thin printed walls are not optically opaque; brand/filler beats colour |
| Kocar et al. (2024) | QUV ISO 4892-3, CIELAB | PLA, 20/60/100 % infill | Colour drifts Delta-E* 3.0-6.1 in 432 h; low infill drifts more |
| Holder et al. (2020) | PurpleAir/AQY/RAMP vs FEM | PVC cap | **Origin of the 5.3 degC figure**: MBE +5.23 degC, RH -24.30 %, n = 5454 h |
| Malings et al. (2020) | PurpleAir, NPM, RAMP vs BAM | Plastic shell | **Origin of the 2.7 degC figure**, reported without n, RMSE or named reference |
| Shlipak et al. (2025) | Thermocouples + weather station | Al, FRP, ABS, PurpleAir PVC endcap | Measured PurpleAir enclosure **+1.88 degC mean, +6.48 degC daily max**; 1-5 W typical dissipation (estimated from rated input, not measured); night convergence constrains the combined heat balance but does NOT identify the solar/self-heating split (corrected 2026-09-24) |
| Jayaratne et al. (2018) | Plantower PMS1003 vs DustTrak/TEOM | Sealed field box | PM artefact flat below ~78 % RH then +80 % of reading by 89 % |
| Samad et al. (2020) | Alphasense B4 vs Horiba/MLU | Sensor chamber | Published RH+T correction polynomials in ppb; 10-25 degC usable window |
| Popoola et al. (2016) | Alphasense EC vs chemiluminescence | n/a | Temperature-driven NO baseline error ~250 ppb; effect is on baseline, not gain |
| Buckingham (1914) | n/a | n/a | Pi theorem, `i = n - k`, and the non-uniqueness of the group set |
| Sonin (2001) | n/a (MIT monograph, not peer-reviewed) | n/a | Modern Pi theorem; missing-variable and superfluous-variable cautions |
| Ostrach (1953) | n/a (NACA report) | Flat plate, infinite medium | Free convection reduces to Gr and Pr; quarter-power law is regime-limited |
| Churchill and Chu (1975) | **full-read pending** | vertical plate | Paywalled; identity verified, no content attributed |
| Bar-Cohen and Rohsenow (1984) | **full-read pending** | parallel-plate channel | Paywalled; abstract scope only, no content attributed |
| JCGM 100:2008 (GUM) | n/a (metrology guide) | n/a | Uncertainty budget incl. the shared-reference correlation case |
| Arlot and Celisse (2010) | n/a (statistics survey) | n/a | Hold-out estimator and complexity penalisation for the K2 benchmark |

## Prior-Work Source Added October 2026 (abstract level, full read pending)

One source from the 2026-10-09 literature review (abstract level, web search only, forward
citations not searched). Nothing beyond the title and the review's one-line description is
attributed. See `docs/PHD_SCOPE_AND_NOVELTY.md`, 2026-10-09 update.

| Paper | Sensors | Reported material / geometry | Experimental contribution |
|---|---|---|---|
| Jin et al. (2026, Sensors) | Naturally ventilated air temperature sensor; **full-read pending** | Not read | Radiation error correction trained on CFD of the shield's geometry and material; direct prior for physics-derived bias correction |

## Sources

- Theisen et al. (2020): https://doi.org/10.5194/amt-13-4699-2020
- Botero-Valencia et al. (2022): https://doi.org/10.1016/j.ohx.2022.e00267
- Tatsumi et al. (2021): https://doi.org/10.3390/technologies9040078
- deSouza et al. (2022): https://doi.org/10.5194/amt-15-6309-2022
- Clements et al. (2017): https://doi.org/10.3390/s17112478
- Giordano et al. (2021): https://doi.org/10.1016/j.jaerosci.2021.105833
- Vajs et al. (2021): https://doi.org/10.3390/s21103338
- Grimsley et al. (2021): https://doi.org/10.1145/3477085.3478988
- Deployment and Evaluation of AirSensEUR Systems (2023): https://doi.org/10.3390/atmos14030540
- Tarara and Hoheisel (2007): https://doi.org/10.21273/HORTSCI.42.6.1372
- Holden et al. (2013): https://doi.org/10.1016/j.agrformet.2013.06.011
- Lazarescu (2015): https://doi.org/10.3390/s150409481
- Daepp et al. (2022): https://doi.org/10.1109/IPSN54338.2022.00010
- Liu et al. (2023): https://doi.org/10.3390/atmos14030523
- García Izquierdo et al. (2024): https://doi.org/10.3390/atmos15070841
- Diez et al. (2024): https://doi.org/10.5194/amt-17-3809-2024
- Deford et al. (2025): https://doi.org/10.1175/JTECH-D-24-0006.1
- Winter et al. (2025): https://doi.org/10.1021/acssensors.5c00566
- Jin et al. (2026): https://doi.org/10.3390/atmos17030272
- Szewczyk et al. (2004): https://doi.org/10.1145/1031495.1031521
- Barrenetxea et al. (2008): https://doi.org/10.1145/1460412.1460418
- Feinberg et al. (2018): https://doi.org/10.5194/amt-11-4605-2018
- Bernard et al. (2019): https://doi.org/10.3390/cli7020026
- Nakamura and Mahrt (2005): https://doi.org/10.1175/JTECH1762.1
- von Rohden et al. (2022): https://doi.org/10.5194/amt-15-383-2022
- Barkjohn et al. (2021): https://doi.org/10.5194/amt-14-4617-2021
- Couzo et al. (2024): https://doi.org/10.3390/atmos15040415
- Ishizuka et al. (2012): https://doi.org/10.1088/1742-6596/395/1/012122
- Berdahl and Martin (1984): https://doi.org/10.1016/0038-092X(84)90144-0
- Formetta et al. (2016): https://doi.org/10.5194/hess-20-4641-2016
- Defraeye et al. (2011): https://doi.org/10.1016/j.enconman.2010.07.026
- Berdahl and Bretz (1997): https://doi.org/10.1016/S0378-7788(96)01004-3
- Barreira et al. (2021): https://doi.org/10.3390/s21061961
- Levinson et al. (2010): https://doi.org/10.1016/j.solener.2010.04.018
- Tychanicz-Kwiecien et al. (2025): https://doi.org/10.3390/ma18173950
- Janek and Hardon (2026): https://doi.org/10.3390/metrology6030048
- Baraboi et al. (2026): https://doi.org/10.3390/ma19132793
- Lopes et al. (2023): https://doi.org/10.3390/polym15102268
- Rodriguez et al. (2023): https://doi.org/10.3390/ma16237384
- Morgan et al. (2017): https://www.osti.gov/biblio/1341825
- Amendola et al. (2021): https://doi.org/10.1371/journal.pone.0253181
- Kocar et al. (2024): https://doi.org/10.3390/ma17235908
- Holder et al. (2020): https://doi.org/10.3390/s20174796
- Malings et al. (2020): https://doi.org/10.1080/02786826.2019.1623863
- Shlipak et al. (2025): https://doi.org/10.3390/s25154798
- Jayaratne et al. (2018): https://doi.org/10.5194/amt-11-4883-2018
- Samad et al. (2020): https://doi.org/10.3390/s20185175
- Popoola et al. (2016): https://doi.org/10.1016/j.atmosenv.2016.10.024
- Buckingham (1914): https://doi.org/10.1103/PhysRev.4.345
- Sonin (2001): https://web.mit.edu/2.25/www/pdf/DA_unified.pdf
- Ostrach (1953): https://ntrs.nasa.gov/api/citations/19930092147/downloads/19930092147.pdf
- Churchill and Chu (1975), full-read pending: https://doi.org/10.1016/0017-9310(75)90243-4
- Bar-Cohen and Rohsenow (1984), full-read pending: https://doi.org/10.1115/1.3246622
- JCGM 100:2008 (GUM): https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf
- Arlot and Celisse (2010): https://doi.org/10.1214/09-SS054
- Jin et al. (2026, Sensors), full-read pending: https://doi.org/10.3390/s26123853
