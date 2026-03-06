variable "project" {
  description = "Project name used for tagging resources."
  type        = string
  default     = "maisignal"
}

variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "eu-central-1"
}

variable "ecr_repo_name" {
  description = "Name of the ECR repository."
  type        = string
  default     = "maisignal"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet (NAT Gateway only)."
  type        = string
  default     = "10.0.0.0/24"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "ecs_task_cpu" {
  description = "CPU units for the ECS Fargate task (1 vCPU = 1024)."
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Memory (MiB) for the ECS Fargate task."
  type        = number
  default     = 512
}

variable "ecs_schedule_expression" {
  description = "EventBridge schedule expression for the daily alert task."
  type        = string
  default     = "cron(0 8 * * ? *)"
}

variable "log_retention_days" {
  description = "CloudWatch log group retention in days."
  type        = number
  default     = 365
}

variable "container_image_tag" {
  description = "Docker image tag (git commit SHA) for the ECS task container."
  type        = string
}

variable "rotation_schedule_days" {
  description = "Number of days between automatic Snowflake password rotations."
  type        = number
  default     = 30
}
