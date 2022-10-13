#!/bin/bash
set -xe


# Copy zip file from S3 bucket
mkdir -vp ~/pv-validation-hub
aws s3 cp s3://validationhubpipelinedjang-webappdeploymentbucket-d28ft3kbhuh4/deploy.zip ~/pv-validation-hub/deploy.zip
cd ~/pv-validation-hub
unzip deploy.zip

# Install libaries
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
# python3 manage.py makemigrations backend
# python3 manage.py migrate

# Start
cd valhub
python3 manage.py runserver
