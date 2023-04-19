# terragrunt.hcl

inputs = {
  project_tags = {
    Project = "TESS"
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