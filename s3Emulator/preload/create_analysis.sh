#!/bin/bash

API_URL="http://api:8005/analysis/create/"
ANALYSIS_NAME="Time Shift Analysis"
EVALUATION_SCRIPT_PATH="/pv-validation-hub-bucket/evaluation_scripts/1/pvinsight-time-shift-runner-old.py"
MAX_CONCURRENT_SUBMISSION_EVALUATION="100"

curl -X POST -H "Content-Type: multipart/form-data" \
  -F "analysis_name=$ANALYSIS_NAME" \
  -F "evaluation_script=@$EVALUATION_SCRIPT_PATH" \
  -F "max_concurrent_submission_evaluation=$MAX_CONCURRENT_SUBMISSION_EVALUATION" \
  $API_URL
