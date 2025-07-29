# Worker

## Objective

The worker directory contains all the files for building one of the stateless workers that process the user submissions when interacting with the PV Validation Hub.

## Summary

The worker is a stateless handler of all user submissions from the frontend. The worker will pick up the earliest message from the AWS SQS Queue and process the uploaded user submission zip file and compute the results and return them back to be viewed on the leaderboard and private submissions page. The worker is entirely divorced from the rest of the system so that any number of workers can be spun up to dynamically handle the fluctuations in demand.

The worker will create a docker image from the user's submission given the specifications and files that they provided from the frontend and then execute the files in an isolated docker container on the worker machine for all data files. Depending on the amount of memory of the worker machine, the worker will be able to process multiple data files at a time in parallel using Dask to create separate docker containers on the worker machine.

## Workflow

1. Worker will initialize itself and run in an infinite loop checking if there are any messages within the AWS SQS Queue
2. Once the worker finds that a message exists in the AWS SQS Queue it will remove the message from the Queue and process the submission
3. The worker will download all the reference and data files, the metadata, the user submission zip, and any other files associated with the analysis task
4. The worker will then create a docker image from the user's submission from the provided metadata
5. The worker will then create multiple docker containers depending on how much memory is available to process each data file from the analysis task
6. The result from every docker container will be saved in multiple files to the worker machine
7. Once all data files have been processed, the performance metrics will be calculated and the results will be saved
8. Using the results a private Marimo report HTML will be generated
9. After everything has finished, all the artifacts will be uploaded to AWS S3 and the API will be updated with a finished status for the user on the frontend to see the results
10. The worker will kill itself after everything has finished so a new, clean worker can take it's place

## Contents

- `Dockerfile` - Used to build the image for development of the worker
- `Dockerfile.prod` - Used to build the production image of the worker
- `docker-entrypoint.sh` - Used as entrypoint for the worker in the docker container
- `logs` - Folder that contains all logs as the worker runs
- `current_evaluation` - Folder that is used as the working folder during a submission
- `src` - Folder that contains all code for the worker
  - `docker` - Folder that contains all files that are required to be included with every user's created docker image
    - `submission_wrapper.py` - The main python script that get executed inside the user's docker container. This script is responsible for setting up the environment that the user's submission run in as well as keeping track of the results and saving them back to the host machine
  - `errorcodes.json` - A running list of all known error codes that could be thrown for the `operator`, `worker`, and `submission`
  - `logging_config.json` - A config file that configures the various logging that occurs within the worker and creates the log files that are saved as part of each submission
  - `submission_worker.py` - The main script that runs infinitely searching for messages from the AWS SQS Queue and downloads all the files from S3 that are required to process the user's submission
  - `pvinsight-validation-runner.py` - The supporting script that orchestrates the creation of the docker image, processes the data files in parallel using Dask with docker containers, and calculates and saves the results from the user's submission
  - `utility.py` - Contains a lot of the business logic that is used to perform the processing of the user's submission

## AWS EC2 Considerations

- EC2 that is provisioned needs to have more memory then the task definition within the ECS service
  - For Example:
    - EC2 4vCPU 16GB
    - EC2 Task Definition in ECS 4vCPU 12GB
      - TODO: need to determine how little difference is required for ease of deployment
- VPC needs to have endpoints for AWS Services and a NAT Gateway since the worker cluster exists within the private subnet but still needs to access the public API
