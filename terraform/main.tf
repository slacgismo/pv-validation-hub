data "aws_caller_identity" "current" {}


locals {
  azs = [
    "${var.aws_region}a", "${var.aws_region}b"
  ]
}

module "vpc" {
  source = "./vpc"

  # Import
  account_id    = data.aws_caller_identity.current.account_id
  aws_region    = var.aws_region
  azs           = local.azs
  log_bucket_id = module.s3.valhub_logs_bucket_id

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
}

module "rds" {
  source = "./rds"

  # Import
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # Variables
  db_instance_class = var.db_instance_class
}

# module "cloudfront" {
#   source = "./cloudfront"

#   # Import
#   valhub_logs_bucket_domain_name    = module.s3.valhub_logs_bucket_domain_name
#   valhub_website_bucket_domain_name = module.s3.valhub_website_bucket_domain_name
#   valhub_bucket_domain_name         = module.s3.valhub_bucket_domain_name

#   # Variables
#   private_origin_id   = var.private_origin_id
#   website_origin_id   = var.website_origin_id
#   website_domain_name = var.website_domain_name
# }

# module "asg" {
#   source = "./autoscalinggroups"

#   # Import
#   account_id         = data.aws_caller_identity.current.account_id
#   private_subnet_ids = module.vpc.private_subnet_ids
#   public_subnet_ids  = module.vpc.public_subnet_ids
#   vpc_id             = module.vpc.vpc_id
#   aws_region         = var.aws_region
#   logs_bucket_id     = module.s3.valhub_logs_bucket_id

#   # Variables
#   asg_desired_capacity           = var.asg_desired_capacity
#   asg_max_size                   = var.asg_max_size
#   asg_min_size                   = var.asg_min_size
#   ecs_worker_task_name           = var.ecs_worker_task_name
#   ecs_api_task_name              = var.ecs_api_task_name
#   ecs_task_role_name             = var.ecs_task_role_name
#   worker_instance_type           = var.worker_instance_type
#   worker_volume_size             = var.worker_volume_size
#   worker_cpu_units               = var.worker_cpu_units
#   worker_memory_size             = var.worker_memory_size
#   worker_memory_reservation_size = var.worker_memory_reservation_size
#   api_cpu_units                  = var.api_cpu_units
#   api_memory_size                = var.api_memory_size
#   api_memory_reservation_size    = var.api_memory_reservation_size
# }








