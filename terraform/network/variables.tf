# subdirectory/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "sg_name_prefix" {
  type    = string
  default = "pv-validation-hub-sg-"
}

variable "subnet_cidr_block_1" {
  type    = string
  default = "10.0.1.0/24"
}

variable "subnet_cidr_block_2" {
  type    = string
  default = "10.0.2.0/24"
}

variable "subnet_cidr_block_3" {
  type    = string
  default = "10.0.3.0/24"
}

variable "subnet_cidr_block_4" {
  type    = string
  default = "10.0.4.0/24"
}

variable "subnet_cidr_block_5" {
  type    = string
  default = "10.0.5.0/24"
}

variable "subnet_availability_zone_1" {
  type    = string
  default = "us-west-2a"
}

variable "subnet_availability_zone_2" {
  type    = string
  default = "us-west-2b"
}

variable "subnet_availability_zone_3" {
  type    = string
  default = "us-west-2c"
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}


variable "vpc_name" {
  type    = string
  default = "pv-validation-hub-vpc"
}

variable "project_tags" {
  type    = object({
    Project = string,
    project-pa-number = string
  })
}
