# Github workflows

## Objective

Contains multiple workflows to automate the CI/CD deployment and testing of the repository to AWS.

## Workflow Files

### build.yml

Run on every push to every branch and manual workflow trigger to build and test the repository for both the API and Worker

#### build-api

- runs black to check formatting of python files
- builds a docker image to test if there are any build errors

#### build-worker

- runs black to check formatting of python files
- builds a docker image to test if there are any build errors

### deployapi.yml

Runs on manual workflow trigger and on an offical release. Automates the deployment of the API to AWS in production.

#### deploy_api

- configure AWS credentials with github secrets
- login to AWS ECR
- builds new image and pushes new image to AWS ECR
- downloads latest task definition used for AWS ECS
- builds new task definition from image
- deploys API on AWS ECS with new task definition

### deployfe.yml

Runs on manual workflow trigger and on an official release. Automates the building and deploying of the frontend to AWS in production

#### build_fe

- install node.js
- cache node modules
- install frontend build dependencies
- move build folder to tmp directory
- temporarily save build artifacts within tmp directory

#### deploy_fe

- configure AWS credentials from github secrets
- retrieve build artifacts from build_fe workflow
- deploy artifacts to AWS S3
- run AWS Cloudfront invalidation

### deployworker.yml

Runs on manual workflow trigger and on official release. Automates the deployment of the worker to AWS in production.

#### deploy_worker

- configure AWS credentials from github secrets
- login to AWS ECR
- build and tag image and push new image to AWS ECR
- download task definition from AWS ECS
- update new task definition with new image
- deploy new task definition to AWS ECS

### update.yml

Run on manual workflow trigger to update all submodules within the repository
