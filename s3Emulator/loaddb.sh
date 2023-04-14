#!/bin/bash

# Set the URL for the API endpoint
URL="api:8005/analysis/upload"

# Set the file path for the evaluation script
EVAL_SCRIPT="/pv-validation-hub-bucket/evaluation_scripts/analysis_1.zip"

# Define the JSON data to be posted
JSON_DATA=$(cat <<EOF
{
    "analysis_name": "Time Shift Validation Analysis",
    "description": "Time shift validation analysis is a statistical technique used to evaluate the accuracy and consistency of forecasting models. 
    It involves shifting time series data and comparing forecasts against actual values. 
    The purpose is to assess the reliability of models for predicting future time periods. 
    The data is split into a training and validation set, and forecasts are generated for the validation set. 
    Time shifts are then applied to the validation set, 
    and forecasts for the shifted data are compared against the original validation set. 
    The accuracy is measured using statistical metrics like MAE or RMSE. 
    The analysis can provide insights into the stability and reliability of the model. 
    It is useful for evaluating forecasting models and ensuring they are trustworthy for real-world predictions.",
    "short_description": "Time shift validation analysis evaluates the reliability and 
    accuracy of forecasting models by comparing shifted time series data and 
    generated forecasts against the original data.",
    "ruleset": "Some ruleset data",
    "dataset_description": "A description of the dataset",
    "evaluation_script": "@$EVAL_SCRIPT",
    "max_concurrent_submission_evaluation": 100
}
EOF
)

# Make the POST request with curl
curl -H "Content-Type: application/json" -X POST -d "$JSON_DATA" $URL
