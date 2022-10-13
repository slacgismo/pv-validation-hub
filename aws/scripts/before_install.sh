#!/bin/bash
set -xe

# Delete the old  directory as needed.
if [ -d ~/pv-validation-hub ]; then
    rm -rf ~/pv-validation-hub
fi

mkdir -vp ~/pv-validation-hub