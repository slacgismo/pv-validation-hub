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

variable "subnet_availability_zone_1" {
  type    = string
  default = "us-east-1a"
}

variable "subnet_availability_zone_2" {
  type    = string
  default = "us-east-1b"
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "vpc_name" {
  type    = string
  default = "pv-validation-hub-vpc"
}

#  ecs_task_execution_role_arn = "arn:aws:iam::041414866712:role/ecsTaskExecutionRole"
#  ecs_task_execution_role_name = "ecsTaskExecutionRole"

variable "ecs_task_execution_role_name" {
    type = string
    default = "ecsTaskExecutionRoleValhub"
}