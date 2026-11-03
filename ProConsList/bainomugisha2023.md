# bainomugisha2023: AirQo sensor kit: A particulate matter air quality sensing kit custom designed for low-resource settings

**Source:** https://doi.org/10.1016/j.ohx.2023.e00482
**Evidence boundary:** Open-hardware paper. Read in full; the STL files were not opened, so vent dimensions are unknown.

## Sensors

Two PMS5003, external SHT25, internal DHT11.

### Pros

- Logs internal box conditions with a separate sensor.

### Cons

- No measured enclosure effect.

## Physical Box, Materials, and Geometry

3D-printed body holding battery and PM sensors, separate cover for the PCB.

### Pros

- Venting larger than the PM sensor's own vent to cut flow resistance.
- Mount in free space with at least 180 degrees of airflow; flat mounting lets dust cling to sensors.

### Cons

- Dust clogging was a major issue in the field.

## Selection Lessons for This Project

- Supports vent area larger than the sensor inlet and a free-air mounting check.

Used in the [vent configuration review](../literature/vent_configuration_review.md).
