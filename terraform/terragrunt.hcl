# terragrunt.hcl
locals {
  project_tag = try(terraform.workspace_var("project_tag"), "default_project_tag")
  project_pa_number = try(terraform.workspace_var("project_pa_number"), "default_project_pa_number")
}

inputs = {
  project_tags = {
    Project = local.project_tag
    project-pa-number = local.project_pa_number
  }
}

terraform {
  extra_arguments "common_vars" {
    commands = ["plan", "apply"]

    arguments = [
      "-var-file=./variables.tfvars"
    ]
  }
}