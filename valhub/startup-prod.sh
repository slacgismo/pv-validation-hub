#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

# Define the directory
DIR="/root/valhub"

cd $DIR

# Run valhub_makemigrations
echo "Running makemigrations..."
python3 manage.py makemigrations

# Run valhub_migrate
echo "Running migrations..."
python3 manage.py migrate

# Run valhub_collectstatic
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Run valhub_superuser
echo "Creating superuser..."
{
    python3 manage.py createsuperuser --noinput
} || {
    echo "Superuser already exists, skipping creation."
}

# Starting supervisord
echo "Starting supervisord..."
supervisord -c /root/valhub/supervisord.prod.conf -n