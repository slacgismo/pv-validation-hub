variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  default     = "default"

}

variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
  default     = "us-west-1"
}

variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
  default     = { environment = "development" }
}

variable "vpc_id" {
  description = "VPC ID to use for the resources"
  type        = string
  default     = ""

}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
  default     = []

}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
  default     = []
}



