#!/bin/bash

API_BASE_URL="http://api:8005/"
ANALYSIS_ID=1
USER_ID=1
STATUS="finished"

upload_submission() {
  local data_file="$1"
  local mae=$(jq '.mean_mean_absolute_error' "$data_file")
  local mrt=$(jq '.mean_run_time' "$data_file")
  local data_requirements=$(jq -c '.data_requirements' "$data_file")

  curl -X POST -H "Content-Type: application/json" \
       -d "[
         {
           \"analysis_id\": $ANALYSIS_ID,
           \"user_id\": $USER_ID,
           \"algorithm\": \"dummy_algorithm\",
           \"status\": \"$STATUS\",
           \"mae\": $mae,
           \"mrt\": $mrt,
           \"data_requirements\": {
             \"data_requirements\": $data_requirements
           }
         }
       ]" \
       "${API_BASE_URL}submissions/preload_submissions"
}

main() {
  local data_file="time-shift-public-metrics.json"
  upload_submission "$data_file"
}

main
