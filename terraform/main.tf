module "vpc" {
  source = "./vpc"

  log_bucket_id = module.s3.valhub_logs_bucket_id
}

module "asg" {
  source = "./autoscalinggroups"

  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  vpc_id             = module.vpc.vpc_id
}

module "s3" {
  source = "./s3"
}

module "cloudfront" {
  source                            = "./cloudfront"
  valhub_logs_bucket_domain_name    = module.s3.valhub_logs_bucket_domain_name
  valhub_website_bucket_domain_name = module.s3.valhub_website_bucket_domain_name
  valhub_bucket_domain_name         = module.s3.valhub_bucket_domain_name
}

module "sqs" {
  source = "./sqs"
}



module "rds" {
  source = "./rds"

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}
