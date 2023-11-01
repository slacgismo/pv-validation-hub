# subdirectory/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
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

variable "valhub_certificate_arn" {
  description = "The name of the load balancer target group"
  type        = string
}

variable "ecs_secrets_manager_policy_arn" {
  description = "The arn for the policy granting access to AWS secrets manager."
  type        = string
}

variable "valhub_ecs_task_role" {
  description = "The arn for the policy granting access to AWS secrets manager."
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

variable "subnet_ids" {
  description = "The list of IDs for the subnets to be used"
  type        = list(string)
}

variable "load_balancer_security_group_id" {
  description = "The security group ID for the load balancer"
  type        = string
}

variable "vpc_id" {
  description = "The VPC ID"
  type        = string
}

variable "valhub_api_service_security_group_id" {
  description = "The security group ID for the ecs service"
  type        = string  
}

variable "project_tags" {
  type    = object({
    Project = string,
    project-pa-number = string
  })
}
