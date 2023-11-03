Good resources to learn Terraform:

Quick, 25 min. Resource
https://www.youtube.com/watch?v=TMWOdaO8_Is

Long, 2.5h tutorial
https://www.youtube.com/watch?v=7xngnjfIlK4

All variable definitions will be done per each module. All variable assignment(e.g. ```*.tfvars```) will be done in the variables folder, within the respective production or staging subfolder. Terraform init should be run from the top level.

Each microservice (api, client, db, workers) should be built and defined in their respective module directories, located under the environments directory. All development should be done under "stage", and should replace "prod" once development is stable.

# Dependency structure
Network: None
Cloudfront: Pre-made s3 bucket
Database: Network
ECS: Network
Route53: RDS, ECS, Network
Worker: Network, ECS
