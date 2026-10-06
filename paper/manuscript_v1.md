# Thermal prediction and target-design calibration in outdoor sensor enclosures

**Version:** V1.0 working draft  
**Status:** Draft for PI/lab review  
**Repository:** 500ft/sensor-enclosure-thermal-design

Current scope follows the [roadmap](../ROADMAP.md): the owner-authorized v2
direction is geometry/calibration transfer, with a first-stage estimation-only
thermal comparison. The broader electronics, calibration and reliability
material below retains earlier work as historical context. It supplies no
thermal campaign or transfer result. PI/design/funding decisions remain in
[ENC-2 to ENC-5](../docs/OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions).

## Abstract

The research direction is to estimate how much target-design calibration can be replaced by measured physical inputs and shared thermal laws. The current contribution is the corrected numerical calculation and its checks; transfer remains a future empirical question.

Low-cost outdoor sensor boxes can increase the spatial and temporal resolution of environmental measurements, but enclosure heating, sensor calibration, power, firmware, and data loss affect the deployed system. This work currently provides a literature synthesis, a first-order thermal model, and provisional analysis of external deployment-log exports. Reference co-location, calibration, and physical thermal comparisons are planned, not completed. At 1000 W/m² and 0.5 m/s the model predicts temperature rises of 19.4°C for a dark baseline, 4.5°C for that box painted white, and 3.0°C for the passive shield; the whole-system variants also change heat coupling and convection, so the contrast does not isolate shielding. These are point estimates without propagated input uncertainty. The [documented combined sensitivity settings](../analysis/thermal_bias_results.md) reverse the shield-versus-painted-box ranking, so no design preference follows from that comparison. Historical log summaries reported no brownout-coded records, 95.7% successful-post records, and 91.4% observed-span completeness in an inferred 22-day outdoor window. These rates and the indoor/outdoor classification remain unverified here because the source exports and intended deployment configuration are external. The historical completeness estimator counted rows against an observed-span denominator; revised software instead requires an explicit intended schedule and counts unique occupied slots. No revised field percentage or wall-clock uptime claim is made. The first-stage study will estimate temperature bias and uncertainty against a calibrated reference, with no pass/fail verdict. Historical reliability verification remains deferred; it is separate from the unrun thermal campaign.

## 1. Introduction

Environmental monitoring often requires measurements at locations or spatial densities where commercial weather stations and regulatory-grade instruments are too expensive or too difficult to deploy. Low-cost sensor boxes can help fill this gap by making local measurements of temperature, relative humidity, pressure, particulate matter, gas concentration, light, or other ambient variables. They are especially useful for laboratory field campaigns, distributed outdoor experiments, teaching, and preliminary site characterization.

However, a low-cost sensor box is not accurate simply because its datasheet reports an acceptable sensor tolerance. Outdoor deployment changes sensor behavior. Solar radiation can heat the enclosure and bias temperature and relative humidity. Poor airflow can delay response and create a microclimate inside the box. Rain, snow, condensation, dust, and ultraviolet exposure can degrade materials and electronics. Battery voltage and power management can affect runtime and data continuity. Wireless links, SD cards, firmware, and connectors can fail before the sensing element itself fails. These integration effects determine whether the box produces useful data for days, weeks, or months without intervention.

The owner-authorized research direction asks:

> How much target-design calibration can measured geometry, material and power
> data plus shared thermal laws replace?

The first stage estimates bias and uncertainty beside a calibrated reference,
with I1 first. Transfer requires a later held-out geometry, units and time split,
calibration budgets and physical/empirical baselines. The present result is a
corrected single-node calculation with exact thermal-step and numerical checks.
It neither demonstrates transfer nor establishes a skip-co-location verdict.

## 2. Background and Literature Review

### 2.1 Low-cost outdoor sensor systems

Low-cost weather and environmental sensing systems are usually justified by their ability to increase measurement density and reduce deployment cost. Theisen et al. evaluated a 3D-printed weather station beside an Oklahoma Mesonet station for eight months and found that several measurements were comparable to commercial sensors, while wind direction and durability were more problematic [@theisen2020]. That study is important for this paper because it evaluates the complete station over time, including longevity and component failure, not only instantaneous accuracy.

Tatsumi et al. presented an open-source, low-cost hydrometeorological measurement system for open-field use, emphasizing a compact board, 3D-printed housing, and field comparison with reference values [@tatsumi2021]. Their work supports the design logic of documenting the full system architecture: sensors, board, housing, data storage, and deployment context must be described together because performance depends on the integrated system.

Air quality sensor studies show the same pattern. Low-cost platforms can be useful complements to reference networks, but field calibration, environmental correction, and deployment reliability determine whether their data can be interpreted quantitatively [@clements2017; @desouza2022; @giordano2021; @airsenseur2023]. These studies are directly relevant even if the lab box is not primarily an air-quality box, because they provide calibration and validation practices that generalize to outdoor low-cost sensing.

Recent complete-system deployments strengthen the case for evaluating the box as an integrated instrument. Eclipse deployed 115 solar-powered, cellular-connected urban sensor devices and collected more than 90% of expected sensor-hours during the reported campaign [@daepp2022]. In a different application, Lazarescu's long-term environmental WSN field test showed that mechanical strain, enclosure heat, antenna placement, charging failures, and faulty-node behavior can limit service before the nominal battery lifetime is reached [@lazarescu2015].

### 2.2 Calibration and ambient-condition effects

Calibration is necessary because low-cost sensors can be biased by sensor-to-sensor variability, environmental cross-sensitivity, sensor aging, and differences between laboratory and field conditions. The common baseline approach is co-location with a reference instrument, followed by a statistical correction model. Linear regression and multiple linear regression are widely used first because they are interpretable, require modest data, and provide a defensible baseline before more complex machine-learning models are introduced [@clements2017; @desouza2022; @vajs2021].

For this V1.0 study, calibration should start with:

1. raw sensor value compared with the reference;
2. univariate linear correction using the target sensor reading;
3. multiple linear correction using ambient covariates such as temperature, relative humidity, solar radiation, wind speed, battery voltage, or enclosure temperature if available.

More complex models should only be added after the baseline data show a clear nonlinear pattern and after enough data are available to avoid overfitting. This is especially important for a research paper because the engineering result should remain explainable: the lab needs to know which factor limits the box, not only which model gives the lowest error on one dataset.

Long-duration studies also show why a one-time calibration is insufficient. The three-year QUANT study found substantial variation among commercial sensor systems and documented effects from relocation, manufacturer corrections, and long-term behavior [@diez2024]. Winter et al. found that Alphasense electrochemical sensors could remain stable over three years with frequently updated calibration, while mechanical and electrical failures often limited service first [@winter2025].

### 2.3 Enclosure materials and geometries

Outdoor enclosures and radiation shields affect sensor accuracy by controlling solar exposure, convective airflow, water protection, and thermal coupling between electronics and sensing elements. This section collects the materials and geometries reported in the literature, augments them with candidates of interest to the lab, and records the source of every property so the data can feed the a priori screening in Section 4.6. Following a source hierarchy, what a system was *built from and tested as* is taken from the primary papers, while quantitative material properties are taken from manufacturer datasheets or standard polymer references and are flagged for verification against the specific filament grade actually used. Optical surface properties (solar absorptance/reflectance) are not reported on filament datasheets because they depend on color and finish rather than the base polymer; these are marked as quantities to be measured, not assumed. The full extraction lives in `literature/materials_options.csv` and `literature/geometries_options.csv`.

#### Evidence from the literature

Theisen et al. built a 3D-printed weather station based on the UCAR 3D-PAWS design and ran it beside an Oklahoma Mesonet reference station for eight months [@theisen2020]. More than 100 parts were printed in off-white ASA, chosen over PLA for higher ultraviolet, temperature, and impact resistance; parts used a grid infill to cut print time. Temperature/RH/pressure sensors sat in a *naturally aspirated* radiation shield at 1.5 m, the support frame was standard PVC pipe, and the Raspberry Pi logger was housed in a sealed electrical junction box with a secondary sensor monitoring internal box temperature — effectively a two-zone layout. Two findings are directly relevant to material and geometry selection. First, temperature RMSE fell from 1.22 °C toward ~1.08 °C and lower as wind speed increased, because the passive shield approached the performance of the reference station's actively aspirated shield only at higher airflow; the radiation error is therefore ventilation-limited, and the authors suggest a 5 V aspiration fan as a remedy. Second, the dominant failures were integration and weathering failures, not sensing-element failures: relative-humidity sensor board corrosion at month 6, an anemometer head that sheared off (attributed partly to reduced infill weakening the print), 3D-printed clamps and nuts that loosened over time, insects nesting in 3D-print grooves, glue yellowing on the UV cover, and water intrusion at the joints between printed parts and the PVC frame (resolved with sealant and drain holes).

Botero-Valencia et al. designed an open-source 3D-printed radiation shield from six stacked truncated cones — five with a central perforation and a solid top cone — separated by 20 mm metallic M3 separators that admit airflow while keeping the interior dry, with the SHT10 temperature/RH sensor held inside the second cone from the bottom so it never sees direct light, and a 1-inch PVC pipe coupling at the base for mounting [@botero2022]. They fabricated the shield in both PLA and ASA and compared both against an unshielded sensor and a Davis Vantage Pro reference station; ASA was preferred for ultraviolet resistance, hardness, and degradation resistance, while PLA was cheaper (about \$5.70 versus \$9.00 in material).

Tatsumi et al. reinforce the system-level point: an open-field measurement system must document the board, the 3D-printed housing, and the data storage/communication path together, because field performance depends on the integrated package rather than the sensor alone [@tatsumi2021]. The air-quality platforms in the review [@clements2017; @desouza2022; @giordano2021; @vajs2021] do not treat enclosure material as a primary variable, so they contribute calibration and reliability practice rather than material/geometry data.

Controlled shield comparisons provide stronger geometry-selection evidence, and they put measured magnitudes on the radiation error. Tarara and Hoheisel found that reflective stacked-plate configurations outperformed tube-shaped designs under low wind (<1 m/s) and high irradiance (>600 W/m²): their best stacked-plate shield held errors between −0.7 and +2.2 °C (89% of daytime readings within 1.5 °C), while cone designs reached +5.4 °C and open-bottom tube designs +7.4 °C, which is why open-bottom shields vulnerable to reflected radiation are not advised and tube shields appeared to require more than roughly 30% sidewall perforation to ventilate effectively; aspirated shields in the same study averaged within ±0.5 °C [@tarara2007]. Holden et al. showed that a roughly \$3 folded white corrugated-plastic Gill-style shield could perform similarly to a commercial passive shield — bias under 0.5 °C beneath forest canopy and a mean absolute error of 0.99 °C against mechanically aspirated references in the open — although a warm full-sun low-wind bias remained [@holden2013]. Deford et al. demonstrated a low-cost white-PLA aspirated shield with a double-wall elbow inlet and low-power fan, directly exposing the accuracy-versus-autonomy tradeoff introduced by aspiration [@deford2025].

More complex recent designs address upward radiation and guided airflow. Liu et al. combined silver-coated aluminum plates, black inner surfaces, white-resin layers, eight vents, and a truncated-cone reflector [@liu2023]. Jin et al. used square shading plates and bowl-cover flow-guiding shrouds while comparing plastic, wood, Fe-Ni alloy, and aluminum configurations through CFD and outdoor validation [@jin2026]. A 14-month Arctic intercomparison of ten shield models further showed that shield differences decrease with wind speed and that fan, logger, power, memory, mounting, and storm failures must be included in the design evaluation [@garciaizquierdo2024].

#### Synthesis: material options

| Material | UV / weather | HDT (°C) | Density (g/cm³) | Printability | Used in lit. | Goal served |
|---|---|---:|---:|---|---|---|
| PLA | Poor | ~55 | ~1.24 | Easy | Botero (PLA variant) | Accuracy screening only |
| ABS | Poor (yellows) | ~98 | ~1.04 | Hard (warps, fumes) | General baseline | Heat resistance, UV-limited |
| ASA | **Excellent** | ~95 | ~1.07 | Hard (warps) | Theisen, Botero | **Accuracy + autonomy** |
| PETG | Moderate–good | ~70 | ~1.27 | Easy | Common option | Autonomy / manufacturability |
| PC | Moderate (needs stabilizer) | ~130 | ~1.20 | Very hard | — | High-temp / high-strength |
| PMMA (acrylic) | Excellent | ~95 | ~1.18 | Sheet, not FDM | — | UV-stable windows |
| PVC (box/pipe) | Moderate | ~60–70 | ~1.38 | Off-the-shelf | Theisen, Botero | Mount + sealed electronics zone |

Property values are representative and must be verified against the datasheet of the specific filament grade used; solar absorptance is color/finish dependent and is to be measured, not assumed. UV ratings and glass-transition values are from a published filament comparison and are consistent with the field UV durability Theisen observed for ASA. Full sourcing per cell is in `materials_options.csv`.

#### Synthesis: geometry options

| Geometry | Airflow | Radiation blocking | Water protection | Electronics coupling | Used in lit. |
|---|---|---|---|---|---|
| Naturally aspirated stacked-plate / louvered shield | Passive crossflow | Good | Moderate | Low (sensor isolated) | Theisen |
| Stacked truncated-cone shield | Passive crossflow | Good | Good (20 mm gaps) | Low | Botero |
| Actively aspirated (fan) shield | Forced | Best | Moderate | Low | Suggested by Theisen |
| Two-zone: sealed electronics box + external probe | Sealed + ventilated region | Design-dependent | High (electronics) | Designed-low | Theisen (junction box + Pi) |
| Vented / perforated box (sensor inside) | Passive | Poor–moderate | Moderate | High (warm bias) | Baseline |
| Commercial IP-rated junction box | Sealed | n/a | High (IP65+) | High if sensor inside | Theisen |
| Reflective stacked-plate handmade shield | Passive crossflow | Good | Moderate | Low | Tarara; Holden |
| Double-wall elbow aspirated shield | Fan-forced | Very good | Good | Low | Deford |
| Mixed-finish multilayer eight-vent shield | Passive through vents | Very good | Good | Low | Liu |
| Bowl-cover flow-guided passive shield | Guided passive flow | Very good | Good | Low | Jin |

The material and geometry decision is therefore not simply "which enclosure protects electronics best." A fully sealed box may protect the electronics but create poor airflow or heat buildup. A highly ventilated shield may improve temperature and humidity response but increase risk of water ingress, dust, insects, or connector corrosion. A reflective white ASA shield may reduce heat absorption and survive ultraviolet exposure better than a dark PLA shield, but it may be harder or more expensive to print. Theisen's wind-dependent temperature error and Botero's PLA-versus-ASA comparison are concrete evidence for these tradeoffs.

For the a priori screening in Section 4.6, the enclosure is treated as a set of measurable design factors, each tied to one of the project's two goals (accuracy or autonomy):

- material: PLA, ASA, PETG, ABS, polycarbonate, acrylic, PVC, commercial junction box plastic, or metal;
- color and surface finish (solar absorptance — to be measured): white, reflective, matte, painted, coated, or dark;
- geometry: louvered shield, stacked plates, helical path, perforated box, aspirated shield, sealed electronics box plus external probe;
- airflow path (drives radiation error — see Theisen): passive crossflow, chimney flow, fan aspiration, blocked vents, bottom openings;
- thermal layout: sensor near electronics, sensor isolated from heat sources, sensor outside main electronics volume;
- weather exposure (drives autonomy/lifetime): rain path, drain holes, gasket, cable glands, condensation path, UV exposure.

#### Candidates of interest for this lab

The cited work favors ASA for outdoor durability, but the lab's fabrication capability constrains what is realistic in-house. The current printer is an open-frame FDM machine without a heated chamber, which prints PLA and PETG reliably but makes ASA, ABS, and PC difficult or impractical (ASA and ABS warp without an enclosure; PC needs chamber heating and 270–310 °C). Two consequences follow for candidate selection.

First, **PETG becomes the primary in-house outdoor material.** It prints easily on an open machine, warps little, and has moderate-to-good UV resistance — a better outdoor default than PLA, and achievable without the enclosure ASA demands. ASA is retained as the literature benchmark and an upgrade path (outsourced prints or a future enclosed printer), and PLA is kept only as a control or as a coated part, not as an uncoated outdoor material.

Second, **surface treatment is promoted to a first-class design variable** rather than an afterthought. For an open-FDM lab this is the practical lever on the two properties that most limit performance: a white reflective exterior coating lowers solar absorptance (directly reducing the radiation-heating bias, and supplying the optical value that no filament datasheet provides — to be measured, not assumed), a UV-resistant clear coat extends the field life of PLA/PETG substrates (Theisen used polyurethane to seal a print), and conformal coating on the sensor board targets the moisture-corrosion failure that ended Theisen's relative-humidity sensor at month 6. These appear as candidate rows in `materials_options.csv` and must be validated for adhesion and field-UV durability rather than taken on faith.

On geometry, the study will test, beyond the literature's single-layer stacked-plate and truncated-cone shields: a fan-aspirated shield (to attack the ventilation-limited radiation error directly, at a known power cost), a double/multi-louver Stevenson-type shield (to see how far a purely passive design can close the gap before a fan is needed), a helical/chimney buoyancy-driven shield (fan-like ventilation without the power draw), the two-zone sealed-electronics-plus-external-sensor architecture, and — as the strongest fit for an open-FDM lab — a commercial IP-rated junction box paired with a small printed, field-replaceable PETG vent/shield module. The last option deliberately separates the hard sealing problem (bought off the shelf) from the printable shield problem (cheap to iterate). The vented box with the sensor sharing the electronics volume is retained only as a negative control, since it couples self-heating into the ambient reading. Full candidate details and proxy parameters are in `geometries_options.csv`.

### 2.4 Autonomy and reliability

Autonomy is the period during which the box operates without physical intervention. This is not only battery life. A box loses autonomy when data are missing, sensors drop out, storage fills, clocks drift, wireless upload fails, connectors corrode, firmware hangs, or the enclosure requires repair. EnviSense and similar low-power environmental sensing work demonstrates that field reliability depends on deployment planning, remote device management, and system co-design with domain users, not only the sensor bill of materials [@grimsley2021].

This lesson long predates low-cost air sensing: the canonical large-scale field deployments of low-power sensor networks reported lifetime, node mortality, and data yield as primary results [@szewczyk2004], and their deployment-practice successors warned that a functioning system does not by itself guarantee meaningful data — failures arise across development, packaging, power, and on-site validation, and bench behavior does not predict field behavior [@barrenetxea2008]. In the air-quality domain specifically, long-term collocation studies now evaluate data completeness explicitly alongside accuracy [@feinberg2018].

The expanded literature shows why autonomy must be measured from observed field behavior rather than estimated battery capacity alone. Eclipse reports expected sensor-hours as an operational reliability measure [@daepp2022]. Lazarescu documents how a theoretically long-lived low-power network still required intervention after thermal, mechanical, charging, and communication failures [@lazarescu2015]. The COAT Arctic comparison lost data from fan, logger, power, memory, mounting, and storm events [@garciaizquierdo2024], while Winter et al. found that mechanical and electrical failures could occur before meaningful electrochemical sensing-element degradation [@winter2025].

For the lab's sensor box, autonomy should be reported with several metrics: runtime before physical intervention, uptime percentage, data completeness, number and type of maintenance events, number of power failures, number of sensor dropouts, and time before recalibration is needed. These metrics connect directly to the PI's question: how long can the box last without someone having to change it or fix it?

## 3. Historical Sensor Box Description

This section documents the current lab box before any modification. Table 1 is the baseline inventory. Each value is labeled by evidence source: **[log]** = established by the deployment-log schema or data (Section 5.0), **[owner]** = supplied by the box owner from direct measurement, **[confirm]** = requires confirmation from the lab (open items are tracked in the provenance sheet accompanying the deployment-log audit).

| Component | Current lab box value | Evidence / notes |
|---|---|---|
| Sensor models | T/RH sensor, optical particle counter (0.3 µm count + PM1/PM2.5/PM10 channels), NO2 and Ox electrochemical cells (working + auxiliary electrode channels) | [log] channel set; exact part numbers [confirm] |
| Microcontroller/logger | ESP32-class MCU (dual-core reset codes, deep-sleep wake cycle, hardware brownout detector) | [log] ESP-IDF reset-reason vocabulary; board revision [confirm] |
| Power system | Single-cell Li-ion (observed 3.31–4.17 V) with fuel gauge reporting SOC; battery-temperature channel unpopulated (−42 sentinel on all records); solar panel and regulator details | [log]; panel/regulator ratings [confirm] |
| Enclosure material | 3D-printed ABS, 0.100 in (2.54 mm) nominal wall | [owner] |
| Enclosure geometry | Vented box, 7.711 × 5.490 × 4.550 in exterior; bottom hex-pattern vent 12.04 in² (≈48% of footprint); full roof with 0.200 in vertical gap (nominal lateral outlet ≈4.02 in² if the gap is continuous — unverified); ≈2.83 L gross internal volume | [owner]; gap continuity and internal blockage [confirm] |
| Sensor placement | Improvised layout (components positioned where they fit); gas sensors face downward toward the bottom vent | [owner]; exact coordinates undocumented — a documented limitation for any thermal analysis |
| Logging rate | Observed median 6 min between records | [log]; configured cadence [confirm] |
| Data storage/transmission | Cellular (LTE registration and signal-quality fields) with HTTP POST upload; per-record upload status logged | [log] |
| Firmware behavior | Deep-sleep duty cycle; per-record reset-reason, boot counter, and stage markers; brownout detector active; environmental read is corrupted on brownout-reset records (humidity reads 0) | [log]; timestamp source and retry logic [confirm] |
| Known failure problems | Brownout resets in two distinct modes (Section 5.4); upload failure coupled to power state, not signal quality; fuel-gauge thermistor unpopulated | [log] |

This describes the earlier box. The new rig inventory and selection of designs remain unresolved; this history does not assign the campaign hardware.

## 4. Methods

The thermal method remains the draft [co-location protocol](../docs/COLOCATION_PROTOCOL.md),
including mandatory-first I1 and estimation-only reporting. The broader methods
below are retained proposals. Neither they nor the
[held transient output](../docs/results.md#transient-result-on-hold) constitute a
frozen protocol. Record measured deployment inputs separately from frozen
coefficients, and drive a corrected model with independently acquired weather
under a procedure fixed before outcomes.

### 4.1 Study design

The earlier whole-box study proposed four phases, retained here as history:

1. **Inventory and bench check.** Document hardware, inspect enclosure, confirm sensor operation, verify timestamps, and log battery voltage.
2. **Reference co-location.** Deploy the sensor box near reference instruments under real outdoor conditions. The reference should measure the same variables as the lab sensors whenever possible.
3. **Baseline analysis.** Compare raw data to reference data and quantify error, missing data, uptime, and failure modes.
4. **Calibration and decision analysis.** Apply simple calibration models, compare error reduction, and identify whether the limiting factor is sensor calibration, power, enclosure design, firmware, or maintenance.

### 4.2 Deployment setup

The box should be mounted in the same orientation and exposure expected for normal use. Mounting height, nearby surfaces, shade, roof overhangs, vegetation, walls, and ground material must be recorded because they affect the local microclimate. If possible, wind speed, solar radiation, rain, and ambient temperature should be recorded from a nearby weather station or reference system.

The older whole-box proposal below is superseded for the first-stage thermal campaign, whose maximum window is set in the current protocol. It proposed a 14-day baseline with a 30-day target. A 30-day co-location is long enough to capture day-night cycles, several weather states, battery behavior, and early failures, and it matches the U.S. EPA's non-regulatory air-sensor base-testing protocols, which recommend collocating at least three identical sensor units with reference-grade (FRM/FEM) monitors for a minimum of 30 days per site [@duvall2021]. For any gas or particulate channels, ASTM D8406-22 provides a standardized field performance-evaluation practice for outdoor sensor instruments [@astm2022d8406], and CEN/TS 17660-1 defines the corresponding European evaluation and classification framework [@cen2021ts17660]. For the meteorological channels, sensor siting and exposure — mounting height, radiation shielding, and distance from surfaces and obstructions — should follow the practice in the WMO Guide to Instruments and Methods of Observation where practical [@wmo2023no8]. Longer deployment is preferred if the box is intended for seasonal use.

### 4.3 Accuracy metrics

Let \(x_i\) be the sensor value and \(y_i\) be the reference value at matched timestamp \(i\).

- Bias: mean of \(x_i - y_i\)
- MAE: mean absolute error
- RMSE: square root of mean squared error
- Correlation: Pearson correlation between sensor and reference
- Drift: change in bias over time, estimated by a linear trend in residuals
- Response lag: time offset that maximizes correlation after weather transitions, if sampling rate supports it

Metrics should be reported for each sensor variable before and after calibration. This metric set is aligned with the evaluation metrics recommended by the EPA air-sensor performance protocols — linearity (coefficient of determination), slope, intercept, RMSE/normalized RMSE, and data completeness [@duvall2021] — with drift and response lag added because enclosure thermal behavior is a study variable here.

The uncertainty of the reference instrument itself must be documented and reported alongside these metrics: sensor-minus-reference differences smaller than the reference uncertainty cannot be interpreted as sensor error. Each reference should therefore be identified by make, model, calibration date, and traceability class — FRM/FEM designation for air-quality references [@duvall2021], or documented conformance to WMO measurement-uncertainty and exposure requirements for meteorological references [@wmo2023no8].

### 4.4 Calibration models

The first calibration model should be linear:

\[
y = \beta_0 + \beta_1 x
\]

The second model should include ambient or system covariates when measured:

\[
y = \beta_0 + \beta_1 x + \beta_2 RH + \beta_3 T + \beta_4 V_{battery} + \beta_5 S + \epsilon
\]

where \(RH\) is relative humidity, \(T\) is temperature, \(V_{battery}\) is battery voltage, and \(S\) is solar radiation or another solar-exposure proxy. Not every variable will be available for every sensor. The model should stay simple enough to interpret.

Calibration should be evaluated with a train/test split by time, not random row splitting only. A time split better represents future deployment because the model is trained on earlier data and tested on later data.

### 4.5 Autonomy and reliability metrics

Autonomy is evaluated with:

- total runtime before intervention;
- uptime percentage;
- expected sample count versus received sample count;
- data completeness by sensor channel;
- number of sensor dropouts;
- number of logger resets or firmware hangs;
- battery-voltage trend and low-voltage events;
- physical maintenance events;
- time until recalibration is needed.

The study should report both the first failure and the limiting failure. For example, a short wireless outage may be the first problem, but the limiting problem may be battery depletion after six days.

### 4.6 Material and geometry classification

Candidate materials and geometries should be classified before testing using practical criteria. This is an a priori classification; it helps decide which design variants deserve testing.

| Design factor | Why it matters | Higher-priority direction |
|---|---|---|
| Density / mass | Affects thermal inertia, mounting load, print time | Low enough for field mounting, not so low that parts become fragile |
| Weatherability | UV, rain, freeze-thaw, dust, corrosion | ASA, PETG, UV-stable commercial plastics, coatings |
| Heat absorption | Dark materials and low reflectance increase radiation heating | White or reflective exterior, low solar absorptance |
| Airflow | Controls response time and heat/moisture buildup | Open shield around sensing elements, isolated sealed electronics |
| Water protection | Prevents rain and condensation damage | Overhangs, drains, glands, splash-resistant vent paths |
| Manufacturability | Determines repeatability and cost | Simple prints, few supports, standard fasteners |
| Maintainability | Determines field repair burden | Modular sensor access, replaceable shields, visible status indicators |

## 5. Results

The current [transient result](../docs/results.md#transient-result-on-hold)
corrects initial time, interval forcing and sky assumptions. Its machine-readable
[verification](../analysis/output/thermal_transient_verification.json) contains
the executed RC and refinement checks. Output bands are assumed-input
sensitivity; no calibrated interval, field accuracy or transfer is established.
Original acquisition metadata remains unavailable and parent review stays on HOLD.

At unchanged water-vapor partial pressure, `RH_sensor = RH_air * e_sat(T_air) /
e_sat(T_sensor)`. The same verification output records this limited thermal
sensitivity. Internal-RH empirical PM corrections need revalidation before
substituting ambient RH. This yields no universal PM benefit or agreed tolerance.

The sections below preserve provisional historical log analysis and old
reporting templates. They are separate from the unrun thermal campaign.

### 5.0 Data source and provisional status

Two device logs were analyzed (Log A: 9,324 records, 2026-03-24 to 2026-06-04; Log B: 1,087 records, 2026-05-29 to 2026-06-04; timestamps logger-local, timezone unconfirmed). The historical summaries were produced using `analysis/analyze_deployment_logs.py`; the revised schedule-aware estimator has not regenerated those percentages without the raw exports and confirmed schedule. Source CSVs remain outside this repository pending data terms; hash recording is supported by the script, but does not establish their availability here.

Throughout, a *brownout record* is one whose reset reason is the hardware brownout detector, and an *operational record* is a normal deep-sleep wake with a valid environmental read. Supporting figures: `analysis/figures/deployment_temp_window.png` (deployment-window identification), `deployment_daily_brownout.png` (daily brownout fraction), `deployment_battv_outcome.png` (battery voltage by record outcome).

The deployment timeline is inferred, not documented: the internal temperature signature indicates the box was outdoors only from Apr 20 to May 11 (daily minima drop from a pinned ~21 °C to 4–12 °C with 10–20 °C diurnal swings; all other phases, and all of Log B, sit near room temperature with small swings). This indoor/outdoor classification — and the identity of the two logs, which record contradictory device states during their overlap and therefore appear to be two units — is provisional pending confirmation by the lab. Results below that depend on it are marked accordingly.

### 5.1 Historical reporting template: raw accuracy

**Status: blocked on reference co-location (Section 4.1, phase 2).** The table below is the intended reporting structure.

Report raw bias, MAE, RMSE, correlation, and drift for each sensor channel. Include a time-series plot showing the sensor and reference together, plus a residual plot showing error against time, temperature, humidity, solar exposure, and battery voltage.

| Sensor variable | Bias | MAE | RMSE | Correlation | Drift | Notes |
|---|---:|---:|---:|---:|---:|---|
| Temperature | TODO | TODO | TODO | TODO | TODO | TODO |
| Relative humidity | TODO | TODO | TODO | TODO | TODO | TODO |
| Pressure | TODO | TODO | TODO | TODO | TODO | TODO |
| PM2.5 / gas / light / other | TODO | TODO | TODO | TODO | TODO | TODO |

### 5.2 Historical reporting template: calibrated accuracy

**Status: blocked on reference co-location.** Compare raw data against calibrated data. The key result is not only whether RMSE improves, but whether the calibration remains stable across weather conditions and time.

| Sensor variable | Raw RMSE | Linear RMSE | Multiple linear RMSE | Error reduction | Recommended model |
|---|---:|---:|---:|---:|---|
| Temperature | TODO | TODO | TODO | TODO | TODO |
| Relative humidity | TODO | TODO | TODO | TODO | TODO |
| Pressure | TODO | TODO | TODO | TODO | TODO |
| PM2.5 / gas / light / other | TODO | TODO | TODO | TODO | TODO |

### 5.3 Autonomy and data completeness (preliminary, field window)

**2026-09-05 interpretation correction:** the following numeric values are
historical reports, not newly verified observations. Raw exports, intended
cadence/window, maintenance history, and clock provenance are not available in
this checkout. The corrected unique-slot estimator has not been run on those
private exports. In particular, absence of a recorded event during available
rows does not establish continuous uptime or an unattended deployment.

Runtime and data loss are reported as engineering results, not secondary notes. Values are for the provisional field-deployment window of Log A (Apr 20 – May 11); the bracketing indoor phases are excluded here and analyzed as failure modes in Section 5.4.

| Metric | Value | Interpretation |
|---|---|---|
| Selected window length | 22 days (Apr 20 – May 11, provisional window) | Outdoor placement dates require confirmation |
| Runtime before intervention | Not established | Maintenance history and missing intervals require confirmation |
| Operational received records | 4,735 of 4,736 (historically rounded to 100%) | Received-record fraction, not wall-clock uptime |
| Data completeness | 91.4% vs the observed 6-min cadence | Configured cadence unconfirmed; completeness is relative to observed median interval |
| Upload success | 95.7% of records | Cellular HTTP POST |
| Battery low-voltage events | 0 reported in window (median 3.941 V) | Available records do not establish power balance or solar contribution |
| Sensor dropout events | 1 record with invalid environmental read | Isolated |
| Maintenance events | No reported maintenance signature within window | Actual interventions and cause of subsequent 414-h gap are unconfirmed |
| Internal temperature span | 4.1 to 31.7 °C | Internal readings; not a reference-validated environmental measurement |

The historical summaries report no brownout-coded records in the selected window, 95.7% successful-post records, and 91.4% completeness under the former observed-span estimator. They also report 4,079 brownout-coded records in indoor-signature phases. Reset-event uniqueness and physical location require provenance checks. These descriptions do not establish continuous autonomy or outdoor safety. Reporting completeness and yield remains important [@szewczyk2004; @feinberg2018], but configured expected slots and available-record outcomes must be kept distinct. The proposed bench-versus-field explanation remains provisional [@barrenetxea2008].

### 5.4 Failure modes (preliminary)

Observed failures, coded by the taxonomy below:

- **Power-failure hypotheses — two voltage regimes in indoor-signature phases.** The historical commissioning summary (Mar 26 – Apr 4) reports 99.8% brownout-coded records and 31.5% of Log A's brownout records at ≥ 3.8 V. The terminal summary (May 28 – Jun 4) reports a median 3.53 V on brownout records. Load transients, regulator behavior, setup differences, and depletion are candidate explanations; these logs alone do not identify them or prove physical location.
- **Upload outcome association, not exclusion of connectivity faults.** The summaries report zero successful uploads among 4,079 brownout-coded records, with signal-quality medians of 17 versus 16 in Log A and 18 versus 18 in Log B. Similar medians cannot exonerate the radio link or establish causal ordering between reset and upload failure.
- **Invalid environmental readings co-occur with brownout state.** The summaries report 1,501 of Log A's 1,511 zero-humidity records on brownout-coded rows. This association does not prove resets caused corruption. The existing script excludes zero-humidity rows from environmental summaries; reliability-row outcomes retain them.
- **Instrumentation gap — battery temperature unrecorded.** The fuel-gauge temperature channel reports a −42 sentinel on every record, removing battery temperature from the analyzable variable set.
- Calibration, enclosure (water ingress, heat buildup), and maintenance failure classes: no observable evidence either way in these logs — assessment requires the reference co-location and a documented deployment protocol.

## 6. Discussion

The discussion should identify the dominant limiting factor in the current box. Possible interpretations are:

- If calibration sharply reduces error and autonomy is acceptable, the current hardware may be usable with a defined calibration workflow.
- If the enclosure is limiting accuracy, it will show up in one of two ways rather than as a simple residual correlation: either the calibration achieves its improvement only through large solar, wind, or enclosure-temperature coefficients — meaning the model is compensating for enclosure physics rather than sensor error — or weather-correlated error reappears in the time-separated test period. Note that when solar radiation is included as a calibration covariate (Section 4.4), in-sample residuals will be uncorrelated with solar by construction, so this diagnosis must use held-out data and coefficient magnitudes, not training residuals.
- If the box stops early or misses many samples, power or firmware reliability is more important than sensor accuracy.
- If sensors fail physically, corrode, or drift rapidly, weather protection and replacement schedule become the design priority.
- If maintenance is frequent or difficult, future design should prioritize modularity, connector protection, and easier field access.

A related distinction the discussion must make explicit is *calibrated-away* versus *designed-away* error. A regression that uses solar radiation or enclosure temperature as a covariate can compensate for an enclosure-driven bias without removing its physical cause; that correction is tied to the deployment conditions under which it was trained, and the calibration-transferability literature cautions that such corrections may not transfer across sites, seasons, or hardware revisions [@desouza2022; @diez2024]. Shielding, ventilation and surface finish can reduce physical heat inputs or alter heat transfer, but performance still depends on exposure, unit construction and maintenance. Similar error in one test period does not establish which approach transfers better to later deployments.

The paper should avoid claiming that one material or geometry is universally best. Instead, it should report which component most affects the lab's measurement goal. A temperature and relative-humidity box may need airflow and radiation shielding above all else. A particulate-matter box may need inlet geometry, fan reliability, and humidity correction. A multi-sensor box may need separation between a ventilated sensor region and a sealed electronics/power region.

## 7. Historical Design Criteria for Future Lab Boxes

The lab should use a weighted decision framework when choosing future box designs. The weights can change by experiment, but the criteria should stay consistent.

| Criterion | Metric | Better design means |
|---|---|---|
| Accuracy | Calibrated RMSE, bias, drift | Lower error after calibration |
| Calibration robustness | Test-period error and drift | Correction works across weather states |
| Autonomy | Days before intervention | Longer runtime without field visit |
| Reliability | Uptime and data completeness | Fewer missing samples and dropouts |
| Weather resistance | Physical inspection and failure events | Less UV, rain, condensation, and dust damage |
| Thermal behavior | Signed bias and absolute error by sun/wind regime, compared with a corrected model and declared uncertainty treatment | Estimation-only reporting; assumed-input sensitivity bands do not define acceptance |
| Maintainability | Time to replace sensor/battery | Faster repair with fewer fragile steps |
| Manufacturability | Print/build time, cost, repeatability | Faster, cheaper, more repeatable builds |

For the next prototype, a strong default architecture is a two-zone design:

1. a sealed electronics and power compartment with cable glands, drain-aware mounting, and serviceable access;
2. a ventilated external sensing region or radiation shield that isolates temperature/RH and other ambient sensors from electronics heat while blocking direct solar radiation and rain.

The first material set to compare should be the current enclosure material against at least one more weatherable and reflective option, such as white ASA or white PETG, depending on the lab's printer capability. Dark materials should be avoided for parts near ambient-temperature sensors unless they are painted or shielded from solar radiation.

## 8. Conclusion

The current result is a corrected analytical sensitivity calculation and
numerical verification. The owner-authorized direction asks how much target
calibration can be replaced; first-stage estimation and later geometry-transfer
evidence remain uncollected. The [current blocker](../docs/COLOCATION_OWNER_SESSION.md#current-blocker)
holds parent review and PI, rig and funding status. Historical deployment and
electronics work remains preserved separately.

## References

See `references.bib`.
