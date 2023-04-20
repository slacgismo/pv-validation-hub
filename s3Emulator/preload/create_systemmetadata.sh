#!/bin/bash

API_URL="http://api:8005/system_metadata/systemmetadata/bulk_create/"

# Remove the header from the CSV and convert it to JSON
tail -n +2 system_metadata.csv | awk -F, '{
    printf "{\"system_id\": %d, \"name\": \"%s\", \"azimuth\": %f, \"tilt\": %f, \"elevation\": %f, \"latitude\": %f, \"longitude\": %f, \"tracking\": %s, \"climate_type\": \"%s\", \"dc_capacity\": %f}\n", $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
}' | jq -s '.' > system_metadata.json

# Upload the JSON data to the API
curl -X POST -H "Content-Type: application/json" -d "@system_metadata.json" "${API_URL}"

# Clean up the temporary JSON file
rm system_metadata.json
