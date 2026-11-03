# sensirion2024design: Design Guide for Humidity and Temperature Sensors, Version 2

**Source:** https://sensirion.com/media/documents/FC5BED84/662B494D/Sensirion_Humidity_Temperature_Design_Guide.pdf
**Evidence boundary:** Manufacturer guidance. Read in full; the housing test is reported only as plots.

## Sensors

Sensirion SHTxx and STSxx.

### Pros

- Specific layout advice for T/RH sensors.

### Cons

- No independent data.

## Physical Box, Materials, and Geometry

Generic device housings.

### Pros

- PCB heat conduction is the most common error; use distance, thin traces, removed copper and milled slits.
- Wall the sensor into a small volume with large openings and flow-through.
- At 90% RH a 1 C error gives about 5% RH error.

### Cons

- Effect sizes not given in numbers.

## Selection Lessons for This Project

- Supports a walled T/RH compartment with PCB slots and its own opening.

Used in the [vent configuration review](../literature/vent_configuration_review.md).
