# EC2 Directory

## Objective

The EC2 directory aims to be the central point for admins to update and upload new submission tasks through the `insert_analysis.py` script for development or production. This EC2 folder should ideally be hosted on an AWS EC2 instance in the public subnet of the VPC and would be only accessed via IAM privileges. Although, if the correct AWS access keys exist on the host system you are able to update the production analysis tasks regardless.

## Contents

- `insert_analysis.py` that allows admins with AWS access keys to update or upload analysis tasks to the PV Validation Hub S3 and API for either development or production.
- `routes.json` is the file which determines the location of the files required for a proper analysis task insertion. This will need to be updated to point to the new files for a new analysis task.

## Required

- Environment variables
  - `admin_username` admin user needs to exist in API
  - `admin_password`
- `~/.aws` folder containing the AWS access required for S3 

## Insert Analysis

A new analysis task for insertion into the PV Validation Hub needs to contain certain files to be successful.

### Analysis File Requirements

- `config.json` - contains all metadata regarding the analysis task
- `file_metadata.csv` - contains the metadata for each data file for the analysis
- `system_metadata.csv` - contains the metadata for each system associated with the data files
- `template.py` - marimo template for the private results page for each submission
- Data files - folder containing all csv files the analysis
- Ground truth files - folder containing all results for each data file

### config.json

Example JSON:

```json
{
  "category_name": "Time Shift Detection",
  "function_name": "detect_time_shifts",
  "comparison_type": "time_series",
  "display_metrics": {
    "mean_mean_absolute_error_time_series": "Mean Mean Absolute Error",
    "median_mean_absolute_error_time_series": "Median Mean Absolute Error"
  },
  "performance_metrics": [
    "runtime",
    "mean_absolute_error"
  ],
  "metrics_operations": {
    "mean_absolute_error_time_series": [
      "mean",
      "median"
    ],
    "runtime": [
      "mean"
    ]
  },
  "allowable_kwargs": [
    "latitude",
    "longitude",
    "data_sampling_frequency"
  ],
  "ground_truth_compare": [
    "time_series"
  ],
  "public_results_table": "time-shift-public-metrics.json",
  "private_results_columns": [
    "system_id",
    "file_name",
    "runtime",
    "data_requirements",
    "mean_absolute_error_time_series",
    "data_sampling_frequency",
    "issue"
  ],
  "plots": [ 
    {
      "type": "histogram",
      "x_val": "mean_absolute_error_time_series",
      "color_code": "issue",
      "title": "Time Series MAE Distribution by Issue",
      "save_file_path": "mean_absolute_error_time_series_dist.png"
    },
    {
      "type": "histogram",
      "x_val": "mean_absolute_error_time_series",
      "color_code": "data_sampling_frequency",
      "title": "Time Series MAE Distribution by Sampling Frequency",
      "save_file_path": "mean_absolute_error_time_series_dist.png"
    },
    {
      "type": "histogram",
      "x_val": "run_time",
      "title": "Run Time Distribution",
      "save_file_path": "run_time_dist.png"
    }
  ]
}
```

#### Properties

- "category_name" - name of analysis which will be used on frontend
- "function_name" - name of function required within submission file
- "comparison_type" - type of comparison
- "display_metrics" - mapping of final metric name to the display name for the leaderboard
  - The formatting is as follows `<metric_operation>_<performance_metric>_<ground_truth_type>`
  - e.g. `median_mean_absolute_error_time_series`
- "performance_metrics" - list of metrics to calculate for analysis task
- "metrics_operations" - contains a mapping of aggregate metric to the operation list to be performed on each metric
  - The formatting is as follows `<performance_metric>_<ground_truth_type>`
  - e.g. `mean_absolute_error_time_series`
- "allowable_kwargs" - kwargs for the submission function that are allowed
- "ground_truth_compare" - comparrison type that is used for calculating metrics
- "public_results_table" - name of json result file that contains information about submission results
- "private_results_columns" - name of columns that will be in final dataframe that is passed to marimo template
  - will need to contain final metric name to be used in marimo template
  - The formatting is as follows `<metric_operation>_<performance_metric>_<ground_truth_type>`
- "plots" - not currently used as marimo template is most recent way to visualize results

### system_metadata.csv

Required columns:

```csv
system_id,name,azimuth,tilt,elevation,latitude,longitude,tracking,climate_type,dc_capacity
```

### file_metadata.csv

Required columns:

```csv
file_id,system_id,file_name,timezone,data_sampling_frequency,issue
```

### template.py (Marimo template with cli args input)

Marimo python file will need to input data from `mo.cli_args()` method

Example:

```python
def create_df_from_cli_args():
        args = mo.cli_args().to_dict()
        data = args.get("results_df")
        rows = []
        for row in data:
            rows.append(json.loads(row))

        df = pd.DataFrame.from_records(rows)
        return df
```

### Regarding Frontend Images and Markdown

To update analytic task images and markdown on the frontend you will need to do so within the frontend client repository. Using the analysis ID that is within the URL or within the admin dashboard in the analysis section.

Within the pv-validation-hub-client you will need to create a new folder using the ID for the task in the `public/static/assets/{ID}` folder. You can use the `development` folder and the markdown and images as a reference. Once the files are updated you may need to redeploy the frontend docker container for the changes to show.