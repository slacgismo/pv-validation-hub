# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update 

COPY submission_wrapper.py /app
COPY requirements.txt /app

# Install the Python dependencies for the submission wrapper
RUN pip install --no-cache-dir -r requirements.txt


# Copy the submission package into the container
COPY submission.zip /app

# Unzip the submission package

RUN apt-get install -y unzip

RUN unzip submission.zip -d submission

WORKDIR /app/submission

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
