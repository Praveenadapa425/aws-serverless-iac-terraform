variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "handler" {
  description = "Handler function name"
  type        = string
}

variable "runtime" {
  description = "Runtime environment for the Lambda function"
  type        = string
}

variable "filename" {
  description = "Path to the Lambda function zip file"
  type        = string
}

variable "timeout" {
  description = "Timeout for the Lambda function"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Memory size for the Lambda function"
  type        = number
  default     = 128
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 14
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  type        = string
}