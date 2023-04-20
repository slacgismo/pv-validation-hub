#!/bin/bash

API_URL="http://api:8005/analysis/create"
ANALYSIS_NAME="Time Shift Analysis"
DESCRIPTION="Time shift validation analysis is a statistical technique used to evaluate the accuracy and consistency of forecasting models. 
    It involves shifting time series data and comparing forecasts against actual values. 
    The purpose is to assess the reliability of models for predicting future time periods. 
    The data is split into a training and validation set, and forecasts are generated for the validation set. 
    Time shifts are then applied to the validation set, 
    and forecasts for the shifted data are compared against the original validation set. 
    The accuracy is measured using statistical metrics like MAE or RMSE. 
    The analysis can provide insights into the stability and reliability of the model. 
    It is useful for evaluating forecasting models and ensuring they are trustworthy for real-world predictions."
SHORT_DESCRIPTION="Time shift validation analysis evaluates the reliability and 
    accuracy of forecasting models by comparing shifted time series data and 
    generated forecasts against the original data."
RULESET="Some ruleset data. Lorem ipsum dolor sit amet, 
    consectetur adipiscing elit. Fusce euismod felis a mi aliquam, sit amet consequat mi aliquet. 
    Vestibulum consectetur, purus vel ullamcorper ullamcorper, 
    libero sapien pharetra sapien, eget varius lorem dui auctor magna."
DATASET_DESCRIPTION="A description of the dataset. Lorem ipsum dolor sit amet, 
    consectetur adipiscing elit. Fusce euismod felis a mi aliquam, sit amet consequat mi aliquet. 
    Vestibulum consectetur, purus vel ullamcorper ullamcorper, 
    libero sapien pharetra sapien, eget varius lorem dui auctor magna."
EVALUATION_SCRIPT_PATH="/pv-validation-hub-bucket/evaluation_scripts/time-shift/pvinsight-time-shift-runner.py"
MAX_CONCURRENT_SUBMISSION_EVALUATION="100"

curl -X POST -H "Content-Type: multipart/form-data" \
  -F "analysis_name=$ANALYSIS_NAME" \
  -F "description=$DESCRIPTION" \
  -F "short_description=$SHORT_DESCRIPTION" \
  -F "ruleset=$RULESET" \
  -F "dataset_description=$DATASET_DESCRIPTION" \
  -F "evaluation_script=@$EVALUATION_SCRIPT_PATH" \
  -F "max_concurrent_submission_evaluation=$MAX_CONCURRENT_SUBMISSION_EVALUATION" \
  $API_URL
