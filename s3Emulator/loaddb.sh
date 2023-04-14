#!/bin/bash

# Set the URL for the API endpoint
URL="api:8005/analysis/upload"

# Set the file path for the evaluation script
EVAL_SCRIPT="/pv-validation-hub-bucket/evaluation_scripts/analysis_1.zip"

# Define the JSON data to be posted
JSON_DATA=$(cat <<EOF
{
    "analysis_name": "My Analysis",
    "description": "An analysis of some data",
    "short_description": "A short summary of the analysis",
    "ruleset": "Some ruleset data",
    "dataset_description": "A description of the dataset",
    "evaluation_script": "@$EVAL_SCRIPT",
    "max_concurrent_submission_evaluation": 100
}
EOF
)

# Make the POST request with curl
curl -H "Content-Type: application/json" -X POST -d "$JSON_DATA" $URL
