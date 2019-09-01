variable "memory_size" {
  description = "memory size in MB allowed for lambda executions"
  type        = "string"
  default     = "150"
}

variable "runtime" {
  description = "runtime to use for lambda executions"
  type        = "string"
  default     = "python3.7"
}

variable "timeout" {
  description = "amount of time in seconds lambdas are allowed to execute for"
  type        = "string"
  default     = "10"
}
