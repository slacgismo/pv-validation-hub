#!/bin/bash


# Copy zip file from S3 bucket
if [ -d ~/pv-validation-hub ]; then
    rm -rf ~/pv-validation-hub
fi
mkdir -vp ~/pv-validation-hub
aws s3 cp s3://validationhubpipelinedjang-webappdeploymentbucket-1x29h7rms3rx5/deploy.zip ~/pv-validation-hub/deploy.zip
cd ~/pv-validation-hub
unzip deploy.zip

# Install libaries
sudo apt --assume-yes install python3-pip
sudo apt-get --assume-yes install mariadb-client
sudo apt-get --assume-yes install python3-dev default-libmysqlclient-dev build-essential
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
# python3 manage.py makemigrations backend
# python3 manage.py migrate

# Retrieve secrets
aws s3 cp s3://validationhubpipelinedjang-webappdeploymentbucket-1x29h7rms3rx5/secrets ~/pv-validation-hub/secrets
cat secrets >> ~/.bashrc
source ~/.bashrc

# Start
cd ~/pv-validation-hub/valhub
python3 manage.py runserver
