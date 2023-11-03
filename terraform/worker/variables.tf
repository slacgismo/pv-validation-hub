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

variable "ecs_worker_task_execution_role_name" {
  description = "The name of the ECS task execution role"
  type        = string
}

variable "ecs_worker_cluster_name" {
  description = "The name of the ECS cluster"
  type        = string
}

variable "cloudwatch_worker_log_group_name" {
  description = "The name of the CloudWatch log group"
  type        = string
}

variable "worker_task_definition_family" {
  description = "The family of the ECS task definition"
  type        = string
}

variable "worker_task_definition_container_name" {
  description = "The name of the container in the ECS task definition"
  type        = string
}

variable "worker_task_definition_container_image" {
  description = "The image of the container in the ECS task definition"
  type        = string
}

variable "worker_task_definition_cpu" {
  description = "The cpu for the ECS task definition"
  type        = number
}

variable "worker_task_definition_memory" {
  description = "The memory for the ECS task definition"
  type        = number
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

variable "ecs_worker_service" {
  description = "The name of the ECS service"
  type        = string
}

variable "worker_service_desired_count" {
  description = "The desired count of the ECS service"
  type        = number
}

variable "subnet_ids" {
  description = "The list of IDs for the subnets to be used"
  type        = list(string)
}

variable "vpc_id" {
  description = "The VPC ID"
  type        = string
}

variable "valhub_worker_service_security_group_id" {
  description = "The security group ID for the ecs service"
  type        = string  
}