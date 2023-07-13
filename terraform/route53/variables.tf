variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "api_endpoint" {
  description = "API endpoint"
  type        = string
}

variable "api_arn_id" {
  description = "API Route53 zone ID"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 zone ID"
  type        = string
}

variable "db_endpoint" {
  description = "Database endpoint"
  type        = string
}

variable "elb_hosted_zone_id" {
  description = "Load balancer hosted zone"
  type        = string
}

#variable "cf_endpoint" {
#  description = "API endpoint"
#  type        = string
#}

#variable "cf_arn_id" {
#  description = "API Route53 zone ID"
#  type        = string
#}

variable "project_tags" {
  description = "Tags to be added to the resources"
  type        = map(string)
}
