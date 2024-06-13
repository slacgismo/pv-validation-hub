# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the submission package into the container
COPY submission.zip /app

# Unzip the submission package
RUN apt-get update && apt-get install -y unzip
RUN unzip submission.zip

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# # Set the command to run the application
# CMD [ "python", "submission.py" ]