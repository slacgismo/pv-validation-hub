variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "sg_name_prefix" {
  type    = string
  default = "pv-validation-hub-sg-"
}

variable "db_password" {
  description = "RDS root user password"
  type        = string
  sensitive   = true
}

# subdirectory/variables.tf

variable "project_tags" {
  type    = object({
    Project = string,
    project-pa-number = string
  })
}
