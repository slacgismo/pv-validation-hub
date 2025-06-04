variable "vpc_id" {
  description = "VPC ID where the RDS instance will be deployed."
  type        = string

}
variable "private_subnet_ids" {
  description = "List of private subnet IDs for the RDS instance."
  type        = list(string)

}

variable "db_instance_class" {
  description = "value for the RDS instance class, e.g., db.t3.micro"
  type        = string
  default     = "db.t3.micro"
}
