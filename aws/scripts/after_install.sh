#!/bin/bash
set -xe


# Copy zip file from S3 bucket
if [ -d ~/pv-validation-hub ]; then
    rm -rf ~/pv-validation-hub
fi
mkdir -vp ~/pv-validation-hub
aws s3 cp s3://validationhubpipelinedjang-webappdeploymentbucket-1jov8z4e3glao/deploy.zip ~/pv-validation-hub/deploy.zip
cd ~/pv-validation-hub
unzip deploy.zip

# Install libaries
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
# python3 manage.py makemigrations backend
# python3 manage.py migrate

# Retrieve secrets
aws s3 cp s3://validationhubpipelinedjang-webappdeploymentbucket-1jov8z4e3glao/secrets ~/pv-validation-hub/secrets
cat secrets >> ~/.bashrc
source ~/.bashrc

# Start
cd ~/pv-validation-hub/valhub
python3 manage.py runserver
