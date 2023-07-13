 # route53/terragrunt.hcl

include "root" {
  path = find_in_parent_folders()
}

dependency "ecs" {
    config_path = "../ecs"
}

dependency "rds" {
    config_path = "../database"
}

dependency "cloudfront" {
  config_path = "../cloudfront"
}

inputs = {
  api_endpoint = dependency.ecs.outputs.alb_dns_name
  api_arn_id  = dependency.ecs.outputs.alb_arn
  elb_hosted_zone_id = dependency.ecs.outputs.alb_hosted_zone_id
  db_endpoint  = dependency.rds.outputs.db_endpoint
  cf_endpoint    = dependency.cloudfront.outputs.cloudfront_distribution_domain_name
  cf_zone_id     = dependency.cloudfront.outputs.cloudfront_distribution_hosted_zone_id
}

terraform {
  extra_arguments "common_vars" {
    commands = ["plan", "apply"]

    arguments = [
      "-var-file=../terraform.tfvars"
    ]
  }
}
