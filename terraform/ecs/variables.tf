# subdirectory/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_region" {
  description = "The region where AWS operations will take place"
  type        = string
}

variable "ecs_task_execution_role_name" {
  description = "The name of the ECS task execution role"
  type        = string
}

variable "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  type        = string
}

variable "cloudwatch_log_group_name" {
  description = "The name of the CloudWatch log group"
  type        = string
}

variable "ecs_task_definition_family" {
  description = "The family of the ECS task definition"
  type        = string
}

variable "ecs_task_definition_container_name" {
  description = "The name of the container in the ECS task definition"
  type        = string
}

variable "ecs_task_definition_container_image" {
  description = "The image of the container in the ECS task definition"
  type        = string
}

variable "ecs_task_definition_cpu" {
  description = "The cpu for the ECS task definition"
  type        = number
}

variable "ecs_task_definition_memory" {
  description = "The memory for the ECS task definition"
  type        = number
}

variable "alb_name" {
  description = "The name of the Application Load Balancer"
  type        = string
}

variable "lb_target_group_name" {
  description = "The name of the load balancer target group"
  type        = string
}

variable "ecs_service_name" {
  description = "The name of the ECS service"
  type        = string
}

variable "ecs_service_desired_count" {
  description = "The desired count of the ECS service"
  type        = number
}

variable "project_tags" {
  type    = object({
    Project = string,
    project-pa-number = string
  })
}
