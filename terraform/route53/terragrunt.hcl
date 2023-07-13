# route53/terragrunt.hcl

include "root" {
  path = find_in_parent_folders()
}

dependency "ecs" {
    config_path = "../ecs"
}

dependency "rds" {
    config_path = "../rds"
}

dependency "frontend" {
  config_path = "../frontend"
}

inputs = {
  api_endpoint = dependency.ecs.outputs.alb_dns_name
  api_zone_id  = dependency.ecs.outputs.alb_arn
  db_endpoint  = dependency.rds.outputs.db_endpoint
  cf_endpoint    = dependency.frontend.outputs.cloudfront_distribution_domain_name
  cf_zone_id     = dependency.frontend.outputs.cloudfront_distribution_hosted_zone_id
}

terraform {
  extra_arguments "common_vars" {
    commands = ["plan", "apply"]

    arguments = [
      "-var-file=../terraform.tfvars",
      "-var-file=../variables.tfvars"
    ]
  }
}
