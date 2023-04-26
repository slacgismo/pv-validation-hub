# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

WORKDIR /

RUN apt-get update && apt-get install git sudo curl jq gawk nano -y
RUN git clone https://github.com/kperrynrel/time-shift-validation-hub.git

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

# Move simulated bucket to location 
RUN mv ./pv-validation-hub-bucket /
RUN rm -r /pv-validation-hub-bucket/submission_files
RUN mv /time-shift-validation-hub/data/file_data/* /pv-validation-hub-bucket/data_files/analytical/
RUN mv /time-shift-validation-hub/data/validation_data/* /pv-validation-hub-bucket/data_files/ground_truth/
# Install the required dependencies
RUN pip install flask boto3

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
