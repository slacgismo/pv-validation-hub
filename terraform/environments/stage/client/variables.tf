# define client-specific variables here. Values are assigned to the variables elsewhere.

variable "ami-id" {
    type = string
}

variable "iam-instance-profile" {
    type = string
}

variable "instance-type" {
    default = "t2.small"
    type = string
}

variable "name" {
    type = string
}

variable "key-pair" {
    type = string
}

variable "private-ip" {
    default = ""
    type = string
}

variable "subnet-id" {
    type = string
}

variable "vpc-security-group-ids" {
    default = []
    type = list(string)
}
