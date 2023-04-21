#!/bin/bash

API_URL="http://api:8005/register"
USERNAME="JohnTest"
EMAIL="JohnTest@testing.email"
PASSWORD="test1234"
FIRST_NAME="John"
LAST_NAME="Test"

curl -X POST -H "Content-Type: application/json" -d '{
  "username": "'"$USERNAME"'",
  "email": "'"$EMAIL"'",
  "password": "'"$PASSWORD"'",
  "firstName": "'"$FIRST_NAME"'",
  "lastName": "'"$LAST_NAME"'"
}' $API_URL
