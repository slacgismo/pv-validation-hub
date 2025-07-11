terraform {
  # Can't put variables in here, so these values are hardcoded. Make sure the S3 bucket exists with the correct permissions.
  backend "s3" {
    bucket  = "valhub-terraform-storage"
    key     = "terraform.tfstate"
    region  = "us-west-1"
    profile = "nrel-pvinsight"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region

  default_tags {
    tags = var.global_tags
  }
}
