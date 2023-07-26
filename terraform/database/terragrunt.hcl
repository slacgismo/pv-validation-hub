# subdirectory/terragrunt.hcl

include "root" {
  path = find_in_parent_folders()
}

dependency "network" {
  config_path = "../network"
}

inputs = {
  vpc_id                                  = dependency.network.outputs.vpc_id
  subnet_ids                              = dependency.network.outputs.subnet_ids
  rds_subnet_group_id                     = dependency.network.outputs.rds_subnet_group_id
  rds_security_group_id                   = dependency.network.outputs.rds_security_group_id
  db_subnet_group_name                    = dependency.network.outputs.rds_subnet_group_name
}

terraform {
  extra_arguments "common_vars" {
    commands = ["plan", "apply"]

    arguments = [
      "-var-file=../terraform.tfvars"
    ]
  }
}