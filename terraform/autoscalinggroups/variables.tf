# Import

variable "account_id" {
  description = "AWS account ID"
  type        = string
}
variable "logs_bucket_id" {
  description = "S3 bucket ID for storing logs"
  type        = string
}

variable "aws_region" {
  description = "AWS region where the resources will be created"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the Auto Scaling group"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the Auto Scaling group"
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "api_target_group_http_arn" {
  description = "ARN of the API target group"
  type        = string
}

variable "api_target_group_https_arn" {
  description = "ARN of the API target group for HTTPS"
  type        = string
}

variable "ecs_worker_sg_id" {
  description = "Security group ID for ECS Worker"
  type        = string

}

# Variables for the Auto Scaling group module
variable "asg_desired_capacity" {
  description = "Desired capacity of the Auto Scaling group"
  type        = number
}

variable "asg_max_size" {
  description = "Maximum size of the Auto Scaling group"
  type        = number
}

variable "asg_min_size" {
  description = "Minimum size of the Auto Scaling group"
  type        = number
}


variable "worker_instance_type" {
  description = "Instance type for the Auto Scaling group instances"
  type        = string
}

variable "worker_volume_size" {
  description = "Size in GB for the root block device"
  type        = number
}

variable "worker_cpu_units" {
  description = "CPU units for the Auto Scaling group instances"
  type        = number
}

variable "worker_memory_size" {
  description = "Memory size for the Auto Scaling group instances in MiB"
  type        = number
}

variable "worker_memory_reservation_size" {
  description = "Memory reservation for the ECS task in MiB"
  type        = number
}
variable "api_cpu_units" {
  description = "CPU units for the Auto Scaling group instances"
  type        = number
}

variable "api_memory_size" {
  description = "Memory size for the Auto Scaling group instances in MiB"
  type        = number
}

variable "api_memory_reservation_size" {
  description = "Memory reservation for the ECS task in MiB"
  type        = number
}


variable "valhub_api_django_secret_key" {
  description = "Django secret key for the Valhub API"
  type        = map(string)
  sensitive   = true
}

variable "valhub_worker_credentials" {
  description = "Login credentials for PV Validation Hub workers"
  type        = map(string)
  sensitive   = true

}
