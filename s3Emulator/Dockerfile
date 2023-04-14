# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

RUN mkdir -p /pv-validation-hub-bucket/data_files/analysis_1/
RUN mkdir -p /pv-validation-hub-bucket/data_files/general/

RUN mkdir -p /pv-validation-hub-bucket/evaluation_scripts/
RUN mkdir -p /pv-validation-hub-bucket/submission_files/

# Copy the required files to the working directory
COPY . .

# Install the required dependencies
RUN pip install flask boto3

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
