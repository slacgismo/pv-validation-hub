# subdirectory/terragrunt.hcl

include "root" {
  path = find_in_parent_folders()
}

dependency "network" {
  config_path = "../network"
}

inputs = {
  vpc_id                                  = dependency.network.outputs.vpc_id
  subnet_ids                              = slice(dependency.network.outputs.subnet_ids, 0, 2)
  load_balancer_security_group_id         = dependency.network.outputs.load_balancer_security_group_id
  valhub_api_service_security_group_id    = dependency.network.outputs.valhub_api_service_security_group_id
}

terraform {
  extra_arguments "common_vars" {
    commands = ["plan", "apply"]

    arguments = [
      "-var-file=../terraform.tfvars"
    ]
  }
}