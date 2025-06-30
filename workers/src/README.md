# workers/src/ Directory

## Metrics

A set of global metrics functions that used to calculate algorithm performance are located in the metric_operations.py file. 

Currently options for calculation (which are built into a task's configuration file) are as follows:

- Error (calculated via p_error()): Basic error calculation, subtracting the ground truth values of a Pandas series from its predicted values. Returns a Pandas series. Delineated as "error" in the configuration JSON file, under the performance_metrics list.
- Absolute error (calculated via p_absolute_error(): Calculating the absolute difference between a series of Pandas predicted outputs and its ground truth values. Returns a non-negative Pandas series. Delineated as "absolute_error" in the configuration JSON file, under the performance_metrics list.
- Mean absolute error (calculate via p_mean_absolute_error()): Calculates the mean of the absolute error series. Returns a singular non-negative error value. Delineated as "mean_absolute_error" in the configuration JSON file, under the performance_metrics list.

