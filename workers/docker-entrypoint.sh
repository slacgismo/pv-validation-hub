#!/bin/sh

# Define function to query Django API route
query_api() {
    response=$(curl -s api:8005/healthy/)
    echo "$response"
}

# Query API every 5 seconds
# while true; do
#     query_api
#     sleep 5
# done

python submission_worker_local.py
