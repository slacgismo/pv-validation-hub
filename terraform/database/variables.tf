variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

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

variable "vpc_security_group_id" {
  description = "The identifier for the VPC security group"
  type        = string
}

variable "rds_proxy_security_group_id" {
  description = "The identifier for the VPC security group"
  type        = string
}

variable "rds_security_group_id" {
  description = "The identifier for the RDS instance"
  type        = string
}

variable "rds_subnet_group_id" {
  description = "The identifier for the RDS instance"
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
  sensitive   = true
}

variable "db_subnet_group_name" {
  description = "Database subnet group name"
  type        = string  
}

variable "secretsmanager_secret_name" {
  description = "The name for the Secrets Manager secret"
  type        = string
}

variable "subnet_ids" {
  type    = list(string)
  description = "A list of subnet IDs."
  default = [] # You can provide default values here if needed
}
