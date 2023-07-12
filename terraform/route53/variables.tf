variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "api_endpoint" {
  description = "API endpoint"
  type        = string
}

variable "api_zone_id" {
  description = "API Route53 zone ID"
  type        = string
}

variable "db_endpoint" {
  description = "Database endpoint"
  type        = string
}

variable "db_zone_id" {
  description = "Database Route53 zone ID"
  type        = string
}

variable "project_tags" {
  description = "Tags to be added to the resources"
  type        = map(string)
}
