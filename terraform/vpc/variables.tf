# Import
variable "account_id" {
  description = "AWS account ID to use for the VPC"
  type        = string
}

variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
}

variable "azs" {
  description = "Availability Zones to use for the VPC"
  type        = list(string)
}

variable "log_bucket_id" {
  description = "S3 bucket ID for VPC flow logs"
  type        = string
}



# Variables for the VPC module
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
}

variable "api_lb_logs_prefix" {
  description = "S3 bucket prefix for API Load Balancer logs"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the website"
  type        = string

}
