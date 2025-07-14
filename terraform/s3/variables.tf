# Import
variable "account_id" {
  description = "AWS account ID to use for the Valhub API"
  type        = string
}

variable "aws_region" {
  description = "AWS region where the Valhub API will be created"
  type        = string

}

variable "api_lb_logs_prefix" {
  description = "S3 bucket prefix for API Load Balancer logs"
  type        = string
}

# Variables for the S3 module

variable "elb_account_id" {
  description = "AWS account ID for the Elastic Load Balancing service"
  type        = string
}
