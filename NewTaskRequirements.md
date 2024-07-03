# Required files for creating a new PV Validation Hub Task

## config.json

Example JSON:

```json
{
    "category_name": "Time Shift Analysis",
    "function_name": "detect_time_shifts",
    "comparison_type": "time_series",
    "performance_metrics": [
        "runtime",
        "mean_absolute_error"
    ],
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
        "run_time",
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

## system_metadata.csv

Required columns:

```csv
system_id,name,azimuth,tilt,elevation,latitude,longitude,tracking,climate_type,dc_capacity
```

## file_metadata.csv

Required columns:

```csv
file_id,system_id,file_name,timezone,data_sampling_frequency,issue
```

## template.py (Marimo template with cli args input)

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

## csv data files

file names must match what is included in the file_name in the file_metadata.csv

## ground truth csv data files

file names must match what is included in the data files folder

## Markdown files for Task

### description.md

The markdown file used for the description tab in an analysis.

### dataset.md

The markdown file to describe the dataset in the data tab.

### shortdesc.md

The markdown file that is used on the card.

### SubmissionInstructions.md

The markdown file that is used on the Submission Instructions tab in the analysis.
