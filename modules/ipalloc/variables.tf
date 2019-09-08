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

variable "billing_mode" {
  description = "billing mode"
  type = "string"
  default = "PAY_PER_REQUEST"
}

variable "read_capacity" {
  description = "number of read units"
  type        = "string"
  default     = "20"
}

variable "write_capacity" {
  description = "number of read units"
  type        = "string"
  default     = "20"
}

variable "stream_enabled" {
  description = "stream enabled or disabled for dynamoDB table"
  type        = "string"
  default     = "true"
}

variable "stream_view_type" {
  description = "stream view type for dynamoDB table"
  type        = "string"
  default     = "KEYS_ONLY"
}
