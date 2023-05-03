#!/bin/bash

user_id="1"
api_base_url="http://api:8005/"
route="submissions/user/${user_id}/submissions"

curl -X GET "${api_base_url}${route}"
