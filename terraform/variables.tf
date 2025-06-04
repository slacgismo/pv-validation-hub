variable "vpc_id" {
  description = "VPC ID to use for the resources"
  type        = string
  default     = ""

}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
  default     = []

}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
  default     = []
}

variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
  default = {
    org       = "pvvalhub"
    billingId = 250026
  }
}

