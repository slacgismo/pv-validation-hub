variable "private_subnet_ids" {
  description = "List of private subnet IDs for the RDS instance."
  type        = list(string)

}

variable "vpc_id" {
  description = "VPC ID where the RDS instance will be deployed."
  type        = string

}
