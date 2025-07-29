# Create a tfvars file with the following content
# staging.tfvars for staging settings
# production.tfvars for production settings

# Root Module
aws_profile = "nrel-pvinsight"
aws_region  = "us-west-2"
global_tags = {
  org         = "pvvalhub"
  billingId   = 250026
  environment = "staging"
}

# VPC Module
vpc_name             = "valhub-vpc"
cidr_block           = "172.18.19.0/24"
public_subnet_cidrs  = ["172.18.19.0/26", "172.18.19.64/26"]
private_subnet_cidrs = ["172.18.19.128/26", "172.18.19.192/26"]
api_lb_logs_prefix   = "api-lb-logs"

# SQS Module

# S3 Module
elb_account_id = "797873946194" # elb account ID for us-west-2

# RDS Module
db_instance_class = "db.t3.micro"
valhub_rds_proxy_secrets = {
  "username" = "pvinsight"
  "password" = "RDS_PASSWORD_HERE"
}

# CloudFront Module
website_origin_id    = "valhub-website-bucket.s3.us-west-2.amazonaws.com-md6tc31vlbn"
private_origin_id    = "valhub-bucket.s3.us-west-2.amazonaws.com-mddu54413fr"
domain_name          = "stratus.nrel.gov"
website_name         = "pv-validation-hub"
private_content_name = "private-content-pv-validation-hub"

# Autoscaling Groups Module
asg_desired_capacity           = 1
asg_max_size                   = 1
asg_min_size                   = 0
worker_instance_type           = "m6in.xlarge"
worker_volume_size             = 30
worker_cpu_units               = 4096
worker_memory_size             = 8192
worker_memory_reservation_size = 8192
api_cpu_units                  = 1024
api_memory_size                = 2048
api_memory_reservation_size    = 2048
valhub_api_django_secret_key   = { "DJANGO_SECRET_KEY" = "PUT_SECRET_KEY_HERE" }
# Create a user in the validation hub with the following credentials
valhub_worker_credentials = {
  "username" = "worker"
  "password" = "PUT_WORKER_PASSWORD_HERE"
}
