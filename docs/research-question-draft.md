# Research-question draft: sensor-enclosure thermal design

Historical question, superseded by the owner-authorized v2 direction in
[the roadmap](../ROADMAP.md) and [ENC-1](OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions).
The original exercise below is retained as background; it is not the current question.

Prepared for the research-question exercise. This draft focuses on enclosure-induced temperature and relative-humidity bias, which is the clearest current research focus in the project.

## 1. Additional reading

If these papers have not already been read, use them as the two additional articles for preparation:

1. Tarara, J. M., & Hoheisel, G.-A. (2007). “Low-cost shielding to minimize radiation errors of temperature sensors in the field.” *HortScience*, 42(6), 1372–1379. https://doi.org/10.21273/HORTSCI.42.6.1372
2. Holden, Z. A., Klene, A. E., Keefe, R. F., & Moisen, G. G. (2013). “Design and evaluation of an inexpensive radiation shield for monitoring surface air temperatures.” *Agricultural and Forest Meteorology*, 180, 281–286. https://doi.org/10.1016/j.agrformet.2013.06.011

An optional third article is Deford, L., Stoll, R., & Pardyjak, E. R. (2025), “Development of a low-cost, 3D-printed, aspirated air temperature measurement radiation shield,” *Journal of Atmospheric and Oceanic Technology*, 42(2), 155–165. https://doi.org/10.1175/JTECH-D-24-0006.1

## 2. Opening sentence and literature review

### Why does this research topic matter?

Low-cost outdoor sensor systems can expand environmental monitoring, but measurements may be biased by the enclosure surrounding the sensor. Solar radiation, poor ventilation, surface color, internal electronics, and nighttime radiative cooling can cause the enclosure to report a temperature and relative humidity different from the actual ambient conditions.

### Literature review

Previous studies show that enclosure design strongly affects the accuracy and durability of outdoor sensors. Theisen et al. (2020) demonstrated that a 3D-printed weather station could support long-term environmental monitoring, but also showed that passive radiation shields were sensitive to wind speed and that mechanical, weathering, and moisture-related failures affected field performance. Controlled comparisons by Tarara and Hoheisel (2007) found that reflective stacked-plate shields reduced radiation errors more effectively than poorly ventilated tube and cone geometries, especially under low-wind and high-solar-radiation conditions. Holden et al. (2013) similarly showed that an inexpensive white radiation shield could approach the performance of commercial shields, although warm bias remained under full sun and low wind. More recent work has examined both materials and more complex geometries: Botero-Valencia et al. (2022) found that 3D-printed shield material and geometry influence outdoor performance and weather resistance, while Deford et al. (2025) demonstrated that active aspiration can further reduce temperature bias at the cost of additional power consumption and mechanical complexity. Together, this literature indicates that accurate outdoor sensing requires a balance among solar reflectance, airflow, weather protection, sensor isolation, and power consumption. However, the effects of these factors have not yet been experimentally quantified for the specific sensor enclosure used in this project.

## 3. Research question

### Gap

The existing literature compares general radiation-shield designs, but it does not establish how the specific enclosure used in this project biases temperature and relative humidity across different surface finishes, ventilation conditions, solar loads, and wind speeds.

### Question

How do enclosure surface finish and ventilation geometry affect the temperature and relative-humidity bias of the project’s outdoor sensor system under different solar-radiation and wind conditions?

The repository’s analytical model predicts that, at high solar loading and low wind, the dark baseline enclosure may heat substantially more than a white-painted enclosure or passive multi-plate shield. Those values are currently model predictions, so the future experiment should compare the configurations against a calibrated reference sensor during both daytime and nighttime conditions.

## Evidence boundary

The current project contains a literature synthesis and first-order thermal model. The model predicts, at 1000 W/m² solar irradiance and 0.5 m/s wind, temperature rises of approximately 19.4 °C for the dark baseline box, 4.5 °C for the same box with a white finish, and 3.0 °C for the passive shield. These are analytical predictions, not physical measurements; calibration, co-location, and thermal validation remain future work.
