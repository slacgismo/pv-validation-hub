#!/bin/bash

# Variables
API_BASE_URL="http://api:8005"
ENDPOINT="/submissions/submission_results/"
SUBMISSION_ID="2"

# Send GET request to the Django API
curl -X GET "${API_BASE_URL}${ENDPOINT}${SUBMISSION_ID}"
