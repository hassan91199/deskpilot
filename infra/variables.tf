variable "region" {
  description = "AWS region for EC2/S3/IAM."
  type        = string
  default     = "us-east-1"
}

variable "image_uri" {
  description = "ECR image URI (registry/repo:tag) to pull and run on the API instance."
  type        = string
}

variable "api_app_name" {
  description = "Name prefix for the API instance's resources (security group, IAM role, log group)."
  type        = string
  default     = "deskpilot-api"
}

variable "instance_type" {
  description = "EC2 instance type. t3.small is enough for FastAPI + a small Postgres + Caddy for a short demo window."
  type        = string
  default     = "t3.small"
}

variable "container_port" {
  description = "Port the API container listens on."
  type        = string
  default     = "8080"
}

variable "openai_api_key_param_arn" {
  description = "SSM Parameter Store ARN (SecureString) holding the real OPENAI_API_KEY. Fetched and decrypted by the instance's own role at boot - never passed as a plain Terraform variable."
  type        = string
}

variable "frontend_bucket_name" {
  description = "S3 bucket for the static-exported Next.js build (must be globally unique)."
  type        = string
}

variable "frontend_domain_name" {
  description = "Custom domain the frontend is served under, e.g. deskpilot.hassanabbas.net."
  type        = string
}

variable "api_domain_name" {
  description = "Custom domain the API is served under, e.g. api.deskpilot.hassanabbas.net."
  type        = string
}

variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID that hassanabbas.net lives in."
  type        = string
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token, scoped to DNS edit on the zone above."
  type        = string
  sensitive   = true
}
