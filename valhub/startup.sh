#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Define the directory
DIR="/root/valhub"

cd $DIR

# Run valhub_makemigrations
echo "Running makemigrations..."
python3 manage.py makemigrations

# Run valhub_migrate
echo "Running migrations..."
python3 manage.py migrate

# Run valhub_initial_data
echo "Loading initial data..."
python3 manage.py loaddata initial_data.json

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
supervisord -c /root/valhub/supervisord.conf -n

# # Keep the container running
# tail -f /dev/null