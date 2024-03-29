#!/bin/bash
# set -e
set -euo pipefail

if ! command -v aws &> /dev/null
then
    # Delete the old  directory as needed.
    if [ -d ./aws ]; then
        rm -rf ./aws
    fi

    # Install aws-cli
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
fi

# Copy zip file from S3 bucket
if [ -d ~/pv-validation-hub ]; then
    rm -rf ~/pv-validation-hub
fi
mkdir -vp ~/pv-validation-hub
aws s3 cp s3://pv-validation-hub-bucket/deploy.zip ~/pv-validation-hub/deploy.zip
cd ~/pv-validation-hub
unzip deploy.zip

# Install libaries
sudo apt update
sudo apt --assume-yes install python3-pip
sudo apt-get --assume-yes install mariadb-client
sudo apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
# python3 manage.py makemigrations backend
# python3 manage.py migrate

# Retrieve secrets
# aws s3 cp s3://validationhubpipelinedjang-webappdeploymentbucket-1x29h7rms3rx5/secrets ~/pv-validation-hub/secrets
# cat secrets >> ~/.bashrc
# source ~/.bashrc
