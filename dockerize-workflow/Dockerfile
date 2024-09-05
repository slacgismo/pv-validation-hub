# Use an official Python runtime as the base image
FROM python:3.12-alpine

# Set the working directory to /app

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

RUN apk add --no-cache docker-cli

RUN apk add gcc python3-dev musl-dev linux-headers

RUN python3 -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt

# run container without closing
CMD ["tail", "-f", "/dev/null"]