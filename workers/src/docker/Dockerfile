
ARG python_version
# Use an official Python runtime as the base image
FROM python:${python_version}-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    libhdf5-dev \
    python3-dev \
    cmake \
    pkg-config

COPY unzip.py .
COPY requirements.txt .

# Install the Python dependencies for the submission wrapper
RUN pip install --no-cache-dir -r requirements.txt

ARG zip_file

# Copy the submission package into the container
COPY $zip_file .

# Unzip the submission package

RUN python -m unzip $zip_file submission

WORKDIR /app/submission

# Install the Python dependencies
RUN pip install -r requirements.txt


# Set the working directory in the container
WORKDIR /app

COPY submission_wrapper.py .
# Command to keep the container running without doing anything
# CMD tail -f /dev/null