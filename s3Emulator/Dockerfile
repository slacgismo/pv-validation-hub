# Use an official Python runtime as the base image
FROM python:3.9-slim

WORKDIR /

RUN apt-get update && apt-get install git sudo curl jq gawk nano -y
# RUN git clone https://github.com/kperrynrel/time-shift-validation-hub.git

# Set the working directory
WORKDIR /app

# Copy the required files to the working directory
COPY . .

WORKDIR /app/preload

RUN chmod +x *

WORKDIR /app/route_testing

RUN chmod +x *

WORKDIR /app

# Install Requirements
RUN pip install -r requirements.txt



# Make simulated bucket in location
RUN mkdir /valhub-bucket
RUN mkdir /valhub-bucket/data_files
RUN mkdir /valhub-bucket/data_files/files
RUN mkdir /valhub-bucket/data_files/references
RUN mkdir /valhub-bucket/submission_files

# Install the required dependencies
RUN pip install flask boto3

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
