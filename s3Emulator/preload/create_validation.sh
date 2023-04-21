#!/bin/bash

API_BASE_URL="http://api:8005/validation_tests"
CSV_FILE="validation_tests.csv"
API_UPLOAD_URL="${API_BASE_URL}/upload_csv/"

if ! command -v curl &> /dev/null
then
    echo "curl command not found. Please install curl and try again."
    exit 1
fi

curl -X POST -H "Content-Type: multipart/form-data" -F "file=@${CSV_FILE}" ${API_UPLOAD_URL}
