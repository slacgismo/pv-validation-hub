
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
    pkg-config \
    unzip

# COPY unzip.py .
COPY requirements.txt .
COPY whitelist-packages.txt .
COPY verify_packages.py .
COPY submission_wrapper.py .

# Install the Python dependencies for the submission wrapper
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ARG zip_file

# Copy the submission package into the container
COPY $zip_file .

# Unzip the submission package
RUN unzip -j $zip_file -d submission

WORKDIR /app/submission

# Install the Python dependencies
RUN pip install --upgrade pip

# Check if package is in whitelist-packages.txt
RUN python ../verify_packages.py requirements.txt ../whitelist-packages.txt

# Install the Python dependencies for the submission package
RUN pip install -r requirements.txt
RUN pip install typing-extensions

# Set the working directory in the container
WORKDIR /app


# Command to keep the container running without doing anything
# CMD tail -f /dev/null