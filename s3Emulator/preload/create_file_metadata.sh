#!/bin/bash

API_BASE_URL="http://api:8005/file_metadata/filemetadata/"

# Read the CSV file and skip the header
tail -n +2 file_metadata.csv | while IFS=, read -r file_id system_id file_name timezone data_sampling_frequency issue subissue
do
  # Use a default value for empty subissue
  if [ -z "$subissue" ]; then
    subissue="N/A"
  fi

  # Create a JSON object from the CSV row
  json_data=$(jq -n \
                --arg file_id "$file_id" \
                --arg system_id "$system_id" \
                --arg file_name "$file_name" \
                --arg timezone "$timezone" \
                --arg data_sampling_frequency "$data_sampling_frequency" \
                --arg issue "$issue" \
                --arg subissue "$subissue" \
                '{file_id: $file_id | tonumber, system_id: $system_id | tonumber, file_name: $file_name, timezone: $timezone, data_sampling_frequency: $data_sampling_frequency | tonumber, issue: $issue, subissue: $subissue}')

  # Upload the JSON data to the API
  curl -X POST -H "Content-Type: application/json" -d "$json_data" "$API_BASE_URL"
  echo ""
done
