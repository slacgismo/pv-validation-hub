resource "aws_instance" "default" {
    ami                    = var.ami-id
    iam_instance_profile   = var.iam-instance-profile
    instance_type          = var.instance-type
    key_name               = var.key-pair
    private_ip             = var.private-ip
    subnet_id              = var.subnet-id
    vpc_security_group_ids = var.vpc-security-group-ids
}

tags = {
    project    = "pv-insight"
    Name       = "pv-validation-hub"
    codeDeploy = "pv-validation-hub"
}

// Terraform Version
terraform {
  required_version = ">= 1.3.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4"
    }
  }
}