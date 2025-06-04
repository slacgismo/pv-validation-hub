variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
  default     = "us-west-1"

}

variable "azs" {
  description = "Availability Zones to use for the VPC"
  type        = list(string)
}

variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.128.0/24", "10.0.129.0/24"]
}

variable "log_bucket_id" {
  description = "S3 bucket ID for VPC flow logs"
  type        = string
}
