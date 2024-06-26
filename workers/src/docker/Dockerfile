# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update 

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
RUN pip install --no-cache-dir -r requirements.txt


# Set the working directory in the container
WORKDIR /app

COPY submission_wrapper.py .
# Command to keep the container running without doing anything
# CMD tail -f /dev/null