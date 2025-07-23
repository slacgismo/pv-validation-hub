data "aws_caller_identity" "current" {}


locals {
  azs = [
    "${var.aws_region}a", "${var.aws_region}b"
  ]
}

module "iam" {
  source = "./iam"
}

module "vpc" {
  source = "./vpc"

  # Import
  account_id                 = data.aws_caller_identity.current.account_id
  aws_region                 = var.aws_region
  azs                        = local.azs
  log_bucket_id              = module.s3.valhub_logs_bucket_id
  valhub_acm_certificate_arn = module.cloudfront.valhub_acm_certificate_arn

  # Variables
  vpc_name             = var.vpc_name
  cidr_block           = var.cidr_block
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  api_lb_logs_prefix   = var.api_lb_logs_prefix

}

module "sqs" {
  source = "./sqs"

  # Import

  # Variables
}

module "s3" {
  source = "./s3"

  # Import
  account_id = data.aws_caller_identity.current.account_id
  aws_region = var.aws_region
  # valhub_api_lb_arn  = module.vpc.valhub_api_lb_arn
  api_lb_logs_prefix = module.vpc.api_lb_logs_prefix

  # Variables
  elb_account_id = var.elb_account_id
}

module "rds" {
  source = "./rds"

  # Import
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # Variables
  db_instance_class        = var.db_instance_class
  valhub_rds_proxy_secrets = var.valhub_rds_proxy_secrets
}

module "cloudfront" {
  source = "./cloudfront"

  providers = {
    aws.us-east = aws.us-east

  }

  # Import
  valhub_logs_bucket_domain_name    = module.s3.valhub_logs_bucket_domain_name
  valhub_website_bucket_domain_name = module.s3.valhub_website_bucket_domain_name
  valhub_bucket_domain_name         = module.s3.valhub_bucket_domain_name

  # Variables
  private_origin_id    = var.private_origin_id
  website_origin_id    = var.website_origin_id
  domain_name          = var.domain_name
  website_name         = var.website_name
  private_content_name = var.private_content_name
}

module "asg" {
  source = "./autoscalinggroups"

  # Import
  account_id                 = data.aws_caller_identity.current.account_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  public_subnet_ids          = module.vpc.public_subnet_ids
  vpc_id                     = module.vpc.vpc_id
  aws_region                 = var.aws_region
  logs_bucket_id             = module.s3.valhub_logs_bucket_id
  api_target_group_http_arn  = module.vpc.api_target_group_http_arn
  api_target_group_https_arn = module.vpc.api_target_group_https_arn
  ecs_worker_sg_id           = module.vpc.ecs_worker_sg_id

  # Variables
  asg_desired_capacity           = var.asg_desired_capacity
  asg_max_size                   = var.asg_max_size
  asg_min_size                   = var.asg_min_size
  worker_instance_type           = var.worker_instance_type
  worker_volume_size             = var.worker_volume_size
  worker_cpu_units               = var.worker_cpu_units
  worker_memory_size             = var.worker_memory_size
  worker_memory_reservation_size = var.worker_memory_reservation_size
  api_cpu_units                  = var.api_cpu_units
  api_memory_size                = var.api_memory_size
  api_memory_reservation_size    = var.api_memory_reservation_size
  valhub_api_django_secret_key   = var.valhub_api_django_secret_key
  valhub_worker_credentials      = var.valhub_worker_credentials

}








