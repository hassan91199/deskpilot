variable "app_name" {
  description = "Name prefix for this instance's resources (security group, IAM role, log group)."
  type        = string
}

variable "image_uri" {
  description = "ECR image URI (registry/repo:tag) to pull and run on boot."
  type        = string
}

variable "container_port" {
  description = "Port the API container listens on (also exposed directly over HTTP for smoke-testing, and reverse-proxied by Caddy for HTTPS)."
  type        = string
  default     = "8080"
}

variable "domain_name" {
  description = "Public domain Caddy requests a Let's Encrypt certificate for and reverse-proxies to the API container (e.g. api.deskpilot.hassanabbas.net)."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.small"
}

variable "plain_env_vars" {
  description = "Additional non-secret runtime env vars for the API container (e.g. FRONTEND_ORIGIN)."
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Map of env var name -> SSM Parameter Store ARN (SecureString) for the API container. Fetched and decrypted by the instance's own role at boot, via user-data - never passed as a plain Terraform variable or baked into the image."
  type        = map(string)
  default     = {}
}
