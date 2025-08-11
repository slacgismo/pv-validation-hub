# Description

It is not uncommon for PV installation metadata to be improperly labeled, including azimuth, tilt, and mounting configuration. Errors and missing data can be especially frequent in solar fleets that have been recently acquired. Incorrect values for this critical metadata can affect the overall performance of PV system performance modelling.

This analysis benchmarks algorithm performance for correctly identifying azimuth and tilt for fixed tilt systems using AC power time series data as an input. Real-world AC power data from fixed-tilt systems is used to assess algorithm performance.
These systems have been manually reviewed to ensure correct azimuth and tilt values. For each system, ground truth azimuth and tilt values are compared to algorithm-estimated azimuth and tilt values and error in degrees is calculated.
