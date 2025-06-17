data "aws_caller_identity" "current" {}


locals {
  azs = [
    "${var.aws_region}a", "${var.aws_region}b"
  ]
}


module "vpc" {
  source = "./vpc"

  aws_region    = var.aws_region
  azs           = local.azs
  log_bucket_id = module.s3.valhub_logs_bucket_id
  account_id    = data.aws_caller_identity.current.account_id

}


module "s3" {
  source = "./s3"

  account_id         = data.aws_caller_identity.current.account_id
  aws_region         = var.aws_region
  valhub_api_lb_arn  = module.vpc.valhub_api_lb_arn
  api_lb_logs_prefix = module.vpc.api_lb_logs_prefix
}

module "asg" {
  source = "./autoscalinggroups"

  account_id         = data.aws_caller_identity.current.account_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  vpc_id             = module.vpc.vpc_id
  aws_region         = var.aws_region
  logs_bucket_id     = module.s3.valhub_logs_bucket_id
}

# module "cloudfront" {
#   source = "./cloudfront"

#   valhub_logs_bucket_domain_name    = module.s3.valhub_logs_bucket_domain_name
#   valhub_website_bucket_domain_name = module.s3.valhub_website_bucket_domain_name
#   valhub_bucket_domain_name         = module.s3.valhub_bucket_domain_name
# }

module "sqs" {
  source = "./sqs"
}


module "rds" {
  source = "./rds"

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}
