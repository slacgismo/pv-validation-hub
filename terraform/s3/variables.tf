# Import
variable "account_id" {
  description = "AWS account ID to use for the Valhub API"
  type        = string
}

variable "aws_region" {
  description = "AWS region where the Valhub API will be created"
  type        = string

}

# variable "valhub_api_lb_arn" {
#   description = "ARN of the Valhub API Load Balancer"
#   type        = string

# }

variable "api_lb_logs_prefix" {
  description = "S3 bucket prefix for API Load Balancer logs"
  type        = string
}

# Variables for the S3 module
