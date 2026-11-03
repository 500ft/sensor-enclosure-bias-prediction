# bosch2018bme280: BME280 Handling, soldering and mounting instructions, rev. 1.8

**Source:** https://www.bosch-sensortec.com/media/boschsensortec/downloads/handling_soldering_mounting_instructions/bst-bme280-hs006.pdf
**Evidence boundary:** Manufacturer guidance. Read in full (Secs. 5.1 to 5.3).

## Sensors

Bosch BME280.

### Pros

- Layout rules for a common T/RH/pressure sensor.

### Cons

- One bullet on port protection and response time is ambiguous.

## Physical Box, Materials, and Geometry

Generic device housings.

### Pros

- Trenches and thin traces around the sensor, a barrier from heat sources, small trapped air volume, large opening, sensor at an edge.
- Keep active time at or below 10% to limit self-heating.

### Cons

- No test data.

## Selection Lessons for This Project

- Supports the walled T/RH compartment and duty-cycle limit.

Used in the [vent configuration review](../literature/vent_configuration_review.md).
