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

variable "website_origin_id" {
  description = "Origin ID for the S3 bucket used as the website origin"
  type        = string
  default     = "S3WebsiteOrigin"

}

variable "private_origin_id" {
  description = "Origin ID for the S3 bucket used as the private origin"
  type        = string
  default     = "S3PrivateOrigin"

}

variable "website_domain_name" {
  description = "Domain name for the CloudFront distribution"
  type        = string
  default     = "pv-validation-hub.org"

}
