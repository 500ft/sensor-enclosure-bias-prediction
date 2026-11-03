# Literature Pros and Cons Analyses

Every paper added to this repository must have a corresponding analysis in this folder.

The analysis must distinguish between:

- facts explicitly reported by the paper;
- engineering advantages and limitations supported by the paper's setup or results;
- uncertainties caused by missing enclosure, material, geometry, or sensor details.

Do not infer an enclosure material merely because a commercial sensor box is described as outdoor-rated.

## Required Workflow for New Literature

When adding a paper:

1. Add its citation to `paper/references.bib`.
2. Add it to `literature/literature_matrix.csv`.
3. Add verified sensor, material, geometry, and setup details to `literature/sensor_material_geometry_summary.md`.
4. Create a `ProConsList/<citation-key>.md` file using `TEMPLATE.md`.
5. Update the coverage table below.

## Current Coverage

| Citation key | Paper | Analysis |
|---|---|---|
| `theisen2020` | 3D-printed weather station | `theisen2020.md` |
| `botero2022` | 3D-printed radiation shields | `botero2022.md` |
| `tatsumi2021` | Hydrometeorological measurement system | `tatsumi2021.md` |
| `desouza2022` | Love My Air calibration network | `desouza2022.md` |
| `clements2017` | Low-cost monitoring workshop summary | `clements2017.md` |
| `giordano2021` | Low-cost PM calibration review | `giordano2021.md` |
| `vajs2021` | AQ10x calibration study | `vajs2021.md` |
| `grimsley2021` | EnviSense low-power nodes | `grimsley2021.md` |
| `airsenseur2023` | AirSensEUR network deployment | `airsenseur2023.md` |
| `tarara2007` | Low-cost passive shielding comparison | `tarara2007.md` |
| `holden2013` | Inexpensive folded radiation shield | `holden2013.md` |
| `lazarescu2015` | Long-term environmental WSN field test | `lazarescu2015.md` |
| `daepp2022` | Eclipse city-scale sensor platform | `daepp2022.md` |
| `liu2023` | Naturally ventilated ground-temperature shield | `liu2023.md` |
| `garciaizquierdo2024` | Arctic radiation-shield intercomparison | `garciaizquierdo2024.md` |
| `diez2024` | QUANT commercial-sensor evaluation | `diez2024.md` |
| `deford2025` | 3D-printed aspirated shield | `deford2025.md` |
| `winter2025` | Three-year electrochemical-sensor performance | `winter2025.md` |
| `jin2026` | High-accuracy naturally ventilated shield | `jin2026.md` |
| `jin2026sensors` | CFD-trained correction and same-design field evaluation | [Full-text assessment](jin2026sensors.md) |
| `duvall2021` | EPA PM2.5 sensor performance protocols (EPA/600/R-20/280) | `duvall2021.md` |
| `wmo2023no8` | WMO-No. 8 instruments and observation methods guide | `wmo2023no8.md` |
| `astm2022d8406` | ASTM D8406-22 outdoor sensor evaluation practice | `astm2022d8406.md` |
| `cen2021ts17660` | CEN/TS 17660-1 sensor-system performance classification | `cen2021ts17660.md` |
| `linden1990` | Linden et al. 1990 | `linden1990.md` |
| `misale1997` | Misale 1997 | `misale1997.md` |
| `karava2004` | Karava et al. 2004 | `karava2004.md` |
| `ohba2006` | Ohba et al. 2006 | `ohba2006.md` |
| `valera2006` | Valera et al. 2006 | `valera2006.md` |
| `burt2022` | Burt 2022 | `burt2022.md` |
| `tetreault2023cci` | Tetreault and Hagan 2023 (CCI TB 38) | `tetreault2023cci.md` |
| `smardo2018amca` | Smardo 2018 (AMCA 500-L talk) | `smardo2018amca.md` |
| `freeth2015bsria` | Freeth 2015 (BSRIA EN 13030 report) | `freeth2015bsria.md` |
| `masters2006soffit` | Masters 2006 | `masters2006soffit.md` |
| `ganchowdhury2009vents` | Gan Chowdhury et al. 2009 | `ganchowdhury2009vents.md` |
| `blocken2004` | Blocken and Carmeliet 2004 | `blocken2004.md` |
| `staliulionis2016` | Staliulionis et al. 2016 | `staliulionis2016.md` |
| `porexvirtek` | Porex Virtek datasheets | `porexvirtek.md` |
| `gore2011cycling` | Gore 2011 technical note | `gore2011cycling.md` |
| `ouimette2024` | Ouimette et al. 2024 | `ouimette2024.md` |
| `johnston2019` | Johnston et al. 2019 | `johnston2019.md` |
| `bainomugisha2023` | Bainomugisha et al. 2023 | `bainomugisha2023.md` |
| `tse2025` | Tse and Liang 2025 | `tse2025.md` |
| `schilt2023` | Schilt et al. 2023 | `schilt2023.md` |
| `sensirion2024design` | Sensirion 2024 T/RH design guide | `sensirion2024design.md` |
| `sensirion2021sen5x` | Sensirion SPS30/SEN5x/SEN6x guidelines | `sensirion2021sen5x.md` |
| `plantower2016` | Plantower 2016 PMS5003 manual | `plantower2016.md` |
| `bosch2018bme280` | Bosch 2018 BME280 mounting | `bosch2018bme280.md` |

The cross-paper analysis from the initial literature review is preserved in `consolidated_selections.md`.
