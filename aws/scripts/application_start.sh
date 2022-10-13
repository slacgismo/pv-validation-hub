#!/bin/bash
set -xe

# Start
cd ~/pv-validation-hub
export $(grep -v '^#' secrets | xargs)
cd ~/pv-validation-hub/valhub
nohup python3 manage.py runserver > log