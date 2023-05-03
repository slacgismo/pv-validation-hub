variable "sg_name_prefix" {
  type    = string
  default = "pv-validation-hub-sg-"
}

variable "db_password" {
  description = "RDS root user password"
  type        = string
  sensitive   = true
}

# subdirectory/variables.tf

variable "common_tags" {
  type        = map(string)
  description = "Common tags to be applied to all resources"
  default     = {}
}
