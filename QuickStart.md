# PV Validation Hub Development Environment Setup

## Requirements

Docker Desktop:
<https://www.docker.com/products/docker-desktop/>

Python 3.11: <https://www.python.org/downloads/release/python-31110/>

Git: <https://git-scm.com/>

## Repositories

PV Validation Hub: <https://github.com/slacgismo/pv-validation-hub>

PV Validation Hub Front-end: <https://github.com/slacgismo/pv-validation-hub-client>

## Outline

### Pull PV Validation Hub Repository

We are going to pull in the develop branch

```bash
git clone -b develop <https://github.com/slacgismo/pv-validation-hub.git>
```

### Pull Frontend Submodule

```bash
git submodule update --init --recursive
```

### Copy .env.example into a new file called .env

Replace admin username and password and anything with <> to the correct file path on your machine

### Create Python Virtual Environment

Create a python virtual environment

```bash
 python -m venv .venv
```

then activate the virtual environment with the following commands based on your system

MAC

```bash
source .venv/bin/activate
```

WINDOWS

```bash
source .venv/scripts/activate
```

### Install Python Requirements

```bash
pip install -r requirements.txt
```

### Install pre-commit

```bash
pre-commit install
```

### Run all containers

**Note:** You can increase the memory allocation for Docker through the Settings > Resources > Memory Limit slider

Kill all containers with ctrl + C or cmd + C and relaunch docker compose

```bash
docker compose build

docker compose up
```

### Sign Into Frontend and Django Backend

Frontend: <http://localhost:3000/>

Backend: <http://localhost:8005/admin/>

### Upload new analysis

Inserting new Analysis happens in the EC2 folder within the PV Validation Hub Repository.

### Open a shell within the EC2 container

When the containers are running within Docker Desktop, you can click on the 3 dots next to the EC2 container and select “Open in Terminal”.

This will create a terminal within the container to then run the command

If you have the Docker VS Code extension you can right click on the EC2 container and select “Attach Shell”

### Insert the Analysis

In the EC2 containers shell, you are able to manage tasks by using the manage.sh bash script with optional flags

```bash
bash manage.sh {insert} <analysis-task-name> [--dry-run] [--force] [--prod] [--limit <number>] [--use-cloud-files]
```

**-–dry-run** - Test that all the files are present and validation has passed without inserting the analysis

**-–force** - Forcefully create an analysis even if the exact same analysis is already present

**-–limit** - Useful during development to only include the top N files for an analysis to shorten time for testing

**-–prod** - If a valid AWS key exists to the production AWS, you can push an analysis to production instead of your local development environment

**--use-cloud-files** - If you have a valid AWS key then you can use files that exist within a private AWS S3 bucket for sensitive data

#### REQUIRED: YOU WILL NEED TO REBUILD THE FRONTEND IMAGE AFTER INSERTING A NEW ANALYSIS FOR CHANGES TO SHOW ON FRONT END

```bash
docker compose build react-client
docker compose up react-client
```
