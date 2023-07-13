variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "sg_name_prefix" {
  type    = string
  default = "pv-validation-hub-sg-"
}

variable "rds_password" {
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

variable "vpc_id" {
  description = "The VPC ID to create the security group in"
  type        = string
}

variable "rds_identifier" {
  description = "The identifier for the RDS instance"
  type        = string
}

variable "rds_instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
}

variable "rds_allocated_storage" {
  description = "The allocated storage for the RDS instance"
  type        = number
}

variable "rds_engine" {
  description = "The database engine to use"
  type        = string
}

variable "rds_engine_version" {
  description = "The engine version to use"
  type        = string
}

variable "db_username" {
  description = "The username for the database"
  type        = string
}

variable "db_password" {
  description = "The password for the database"
  type        = string
}

variable "secretsmanager_secret_name" {
  description = "The name for the Secrets Manager secret"
  type        = string
}

