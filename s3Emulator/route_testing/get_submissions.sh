#!/bin/bash

user_id="1"
api_base_url="http://api:8005/"
route="submissions/user_submission/${user_id}"

curl -X GET "${api_base_url}${route}"
