#!/bin/sh

# Define function to query Django API route
# query_api() {
#     response=$(curl -s api:8005/healthy/)
#     echo "$response"
# }

# Query API every 5 seconds
# while true; do
#     query_api
#     sleep 5
# done
ENV=~/.profile sh
python -m debugpy --listen 0.0.0.0:5678 src/submission_worker.py