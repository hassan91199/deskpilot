output "bucket_name" {
  description = "S3 bucket to sync frontend/out into after each build."
  value       = aws_s3_bucket.site.id
}

output "distribution_id" {
  description = "CloudFront distribution ID, for cache invalidation after each sync."
  value       = aws_cloudfront_distribution.site.id
}

output "distribution_domain_name" {
  description = "CloudFront distribution's own domain name (before the custom-domain CNAME)."
  value       = aws_cloudfront_distribution.site.domain_name
}

output "cert_domain_validation_options" {
  description = "ACM cert's DNS validation records - create these at the DNS provider, then feed the resulting FQDNs back via cert_validation_fqdns."
  value       = aws_acm_certificate.site.domain_validation_options
}
