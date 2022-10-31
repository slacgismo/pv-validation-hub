#!/bin/bash
# set -xe
set -euo pipefail

# Start
# cd ~/pv-validation-hub
# export $(grep -v '^#' secrets | xargs)
cd ~/pv-validation-hub/valhub
screen -d -m python3 manage.py runserver 8080