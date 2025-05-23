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

