# subdirectory/variables.tf

variable "project_tags" {
  type    = object({
    Project = string
  })
}
