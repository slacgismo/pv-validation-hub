# Import
variable "valhub_logs_bucket_domain_name" {
  description = "Name of the S3 bucket for CloudFront logs"
  type        = string
}

variable "valhub_website_bucket_domain_name" {
  description = "Domain name of the S3 bucket for the website"
  type        = string
}

variable "valhub_bucket_domain_name" {
  description = "Domain name of the S3 bucket for the main application"
  type        = string
}

# Variables for the CloudFront module

variable "website_origin_id" {
  description = "Origin ID for the S3 bucket used as the website origin"
  type        = string
}

variable "private_origin_id" {
  description = "Origin ID for the S3 bucket used as the private origin"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the CloudFront distribution"
  type        = string
}

variable "website_name" {
  description = "Name of the website for CloudFront distribution"
  type        = string
}
variable "private_content_name" {
  description = "Name of the private content for CloudFront distribution"
  type        = string
}
