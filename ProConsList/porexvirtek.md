# porexvirtek: Virtek PMV10L and PMV27 membrane vent datasheets

**Source:** https://www.porex.com/?p=28634
**Evidence boundary:** Manufacturer data; test methods not stated. Read in full.

## Sensors

None.

### Pros

- Gives airflow and water-entry pressure for two membranes from one vendor.

### Cons

- Ratings at 70 mbar, far above passive pressures.

## Physical Box, Materials, and Geometry

ePTFE membrane vents.

### Pros

- PMV10L: water entry pressure 185 mbar minimum, airflow 85 l/h/cm2 typical at 70 mbar.
- PMV27: 750 mbar minimum, 7 l/h/cm2 typical.

### Cons

- At pascal-range pressures the flow is very small (own linear estimate).

## Selection Lessons for This Project

- Supports a membrane vent on the sealed electronics section.
- Does not support a membrane as the sensor ventilation path.

Used in the [vent configuration review](../literature/vent_configuration_review.md).
