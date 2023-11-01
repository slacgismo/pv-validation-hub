variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project_tags" {
  type    = object({
    Project = string,
    project-pa-number = string
  })
}