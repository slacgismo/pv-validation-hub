# Variables for the Terraform configuration
# Each variable must also be defined in each respective environment's `*.tfvars` file
# Must include a default value for each variable
# Each module's variables need to also be defined in a respective `variables.tf` file located in the modules folder (without the default value parameter)


# Root Module
variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  default     = "default"
}

variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
  default     = "us-west-2"
}

variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
  default     = { environment = "development" }
}

# VPC Module
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
  default     = "valhub-vpc"
}

variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.128.0/24", "10.0.129.0/24"]
}

variable "api_lb_logs_prefix" {
  description = "S3 bucket prefix for API Load Balancer logs"
  type        = string
  default     = "api-lb-logs"
}

# SQS Module

# S3 Module
variable "elb_account_id" {
  description = "AWS account ID for the Elastic Load Balancing service"
  type        = string
  # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html
  default = "797873946194" # elb account ID for us-west-2
}

# RDS Module
variable "db_instance_class" {
  description = "value for the RDS instance class, e.g., db.t3.micro"
  type        = string
  default     = "db.t3.micro"
}

# CloudFront Module
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

# Autoscaling Groups Module
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

variable "ecs_task_role_name" {
  description = "Name of the ECS task role"
  type        = string
  default     = "valhub-ecs-task-role"
}

variable "worker_instance_type" {
  description = "Instance type for the Auto Scaling group instances"
  type        = string
  default     = "t2.micro" # Example instance type, can be changed as needed

}

variable "worker_volume_size" {
  description = "Size in GB for the root block device"
  type        = number
  default     = 30 # Default size in GB

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


