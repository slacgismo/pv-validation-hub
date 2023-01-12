#!/bin/bash
# set -xe
set -euo pipefail

# Start
# cd ~/pv-validation-hub
# export $(grep -v '^#' secrets | xargs)
cd ~/pv-validation-hub/valhub
screen -d -m -L python3 manage.py runserver 0.0.0.0:8080