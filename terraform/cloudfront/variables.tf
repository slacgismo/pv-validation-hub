# subdirectory/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "bucket_name" {
  description = "The name of the S3 bucket where the website is hosted"
  type        = string
}

variable "default_root_object" {
  description = "The default root object for the CloudFront distribution"
  type        = string
}

variable "acm_certificate_arn" {
  description = "The ARN of the ACM certificate"
  type        = string
}

variable "alt_domain_name" {
  description = "Needed to allow cf use in route53"
  type        = string 
}

variable "project_tags" {
  type    = object({
    Project = string,
    project-pa-number = string
  })
}
