variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "asg_desired_capacity" {
  description = "Desired capacity of the Auto Scaling group"
  type        = number
  default     = 1
}

variable "asg_max_size" {
  description = "Maximum size of the Auto Scaling group"
  type        = number
  default     = 1
}

variable "asg_min_size" {
  description = "Minimum size of the Auto Scaling group"
  type        = number
  default     = 0
}

variable "ecs_worker_task_name" {
  description = "Name of the ECS worker task"
  type        = string
  default     = "valhub-worker-task"
}

variable "ecs_api_task_name" {
  description = "Name of the ECS API task"
  type        = string
  default     = "valhub-api-task"

}

variable "worker_cpu_units" {
  description = "CPU units for the Auto Scaling group instances"
  type        = number
  default     = 4096 # 1 vCPU = 1024 CPU units
}

variable "worker_memory_size" {
  description = "Memory size for the Auto Scaling group instances in MiB"
  type        = number
  default     = 8192 # 1 GB = 1024 MiB

}

variable "worker_memory_reservation_size" {
  description = "Memory reservation for the ECS task in MiB"
  type        = number
  default     = 8192 # 1 GB = 1024 MiB
}
variable "api_cpu_units" {
  description = "CPU units for the Auto Scaling group instances"
  type        = number
  default     = 1024 # 1 vCPU = 1024 CPU units
}

variable "api_memory_size" {
  description = "Memory size for the Auto Scaling group instances in MiB"
  type        = number
  default     = 2048 # 1 GB = 1024 MiB

}

variable "api_memory_reservation_size" {
  description = "Memory reservation for the ECS task in MiB"
  type        = number
  default     = 2048 # 1 GB = 1024 MiB
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

variable "ecs_task_role_name" {
  description = "Name of the ECS task role"
  type        = string
  default     = "valhub-ecs-task-role-testing"
}

