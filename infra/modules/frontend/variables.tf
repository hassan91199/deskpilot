variable "bucket_name" {
  description = "S3 bucket to hold the static-exported Next.js build (frontend/out)."
  type        = string
}

variable "domain_name" {
  description = "Custom domain the frontend is served under (e.g. deskpilot.hassanabbas.net)."
  type        = string
}

variable "cert_validation_fqdns" {
  description = <<-EOT
    FQDNs of the DNS validation records for the ACM cert, once the root
    module has created them at the DNS provider (Cloudflare) from this
    module's cert_domain_validation_options output. Left null until then -
    Terraform sequences the two-way dependency automatically in one apply.
  EOT
  type        = list(string)
  default     = null
}
