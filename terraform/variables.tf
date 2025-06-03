variable "azs" {
  description = "Availability Zones to use for the VPC"
  type        = list(string)
  default     = ["us-west-1a", "us-west-1b"]
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

variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
  default = {
    org       = "pvvalhub"
    billingId = 250026
  }
}

