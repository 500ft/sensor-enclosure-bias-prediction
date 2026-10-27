# johnston2019: City Scale Particulate Matter Monitoring Using LoRaWAN Based Air Quality IoT Devices

**Source:** https://doi.org/10.3390/s19010209
**Evidence boundary:** Design and deployment paper. Read in full. Design changes are reported from experience; their effect on readings is not quantified.

## Sensors

PMS5003, PMS7003, Honeywell HPMA115S0, Alphasense OPC-N2.

### Pros

- Four PM sensors in one node.

### Cons

- No measured effect of each enclosure change.

## Physical Box, Materials, and Geometry

Version 1: IP65 ABS box 360 x 200 x 160 mm, grids of 8 mm holes in base and one side, steel mesh 3 mm holes and 51% open area, Pi above a bulkhead. Version 2: three stacked sections (electronics top, sensors middle, intake and exhaust bottom), two 54 mm intake and two 70 mm exhaust holes with the same mesh, sloped drip cover over the Pi, two Gore breather vents.

### Pros

- Records why the hole grid became a few large holes and why sections were sealed from each other.
- Sensors exhausting into the electronics section caused recirculation that had to be ducted out.

### Cons

- Much larger box than the lab box.

## Selection Lessons for This Project

- Supports a partitioned layout with sealed electronics and separate intake and exhaust.
- Cannot rank the variants.

Used in the [vent configuration review](../literature/vent_configuration_review.md).
