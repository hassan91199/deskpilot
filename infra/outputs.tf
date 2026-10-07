output "api_instance_ip" {
  description = "Direct http://ip:<port> URL for the FastAPI container, reachable before DNS/TLS are ready - used for CI smoke-testing only; real traffic goes through the custom domain via Caddy."
  value       = "http://${module.api.public_ip}:${var.container_port}"
}

output "frontend_bucket" {
  value = module.frontend.bucket_name
}

output "frontend_distribution_id" {
  description = "CloudFront distribution ID - invalidate this after each frontend sync."
  value       = module.frontend.distribution_id
}

output "frontend_url" {
  value = "https://${var.frontend_domain_name}"
}

output "api_url" {
  value = "https://${var.api_domain_name}"
}
