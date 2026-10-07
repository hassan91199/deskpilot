# DP-8: on-demand demo infra (apply to bring it up, destroy to tear it
# down completely, everything in one AWS+Cloudflare graph).
#   module.api        - EC2 + Caddy: postgres + api containers, custom domain
#   module.frontend    - S3 + CloudFront: static-exported Next.js frontend
# No App Runner, no RDS, no quota module - DeskPilot has no public BYOK-style
# tier (unlike ClipForge's clipforge-demo), so there's nothing to rate-limit
# and no second backend service to justify. Postgres+pgvector runs as a
# container on the same instance as the API rather than on RDS: the whole
# instance (and its data) is destroyed on every teardown anyway, and ingest
# reseeds it fresh on every boot, so RDS's persistence buys nothing here -
# just a faster, simpler up/down cycle.
#
# EC2 (not App Runner/ECS Fargate) for the API for the same reason as
# ClipForge's CF-35: App Runner's managed proxy silently killed a
# multi-minute SSE stream even with a heartbeat, and /chat here is exactly
# that shape. Caddy on the instance terminates TLS directly via its own
# Let's Encrypt cert, so there's no AWS-managed proxy left in the path.

module "api" {
  source          = "./modules/ec2_api"
  app_name        = var.api_app_name
  image_uri       = var.image_uri
  container_port  = var.container_port
  domain_name     = var.api_domain_name
  instance_type   = var.instance_type
  secret_env_vars = { OPENAI_API_KEY = var.openai_api_key_param_arn }
  plain_env_vars  = { FRONTEND_ORIGIN = "https://${var.frontend_domain_name}" }
}

module "frontend" {
  source      = "./modules/frontend"
  bucket_name = var.frontend_bucket_name
  domain_name = var.frontend_domain_name

  cert_validation_fqdns = [for r in cloudflare_record.frontend_cert_validation : r.hostname]

  providers = {
    aws.us_east_1 = aws.us_east_1
  }
}

# --- DNS (Cloudflare) - created/destroyed in the same apply/destroy as the
# AWS resources above, so a single terraform destroy leaves nothing behind.

resource "cloudflare_record" "frontend_cert_validation" {
  for_each = {
    for dvo in module.frontend.cert_domain_validation_options : dvo.domain_name => dvo
  }
  zone_id = var.cloudflare_zone_id
  name    = each.value.resource_record_name
  type    = each.value.resource_record_type
  content = each.value.resource_record_value
  ttl     = 60
  proxied = false
}

resource "cloudflare_record" "frontend" {
  zone_id = var.cloudflare_zone_id
  name    = var.frontend_domain_name
  type    = "CNAME"
  content = module.frontend.distribution_domain_name
  ttl     = 60
  proxied = false
}

# No cert-validation records here (unlike frontend's ACM cert above) - Caddy
# on the instance gets its own Let's Encrypt cert directly at boot, so there
# is no Terraform-side validation step for the API's domain.
resource "cloudflare_record" "api" {
  zone_id = var.cloudflare_zone_id
  name    = var.api_domain_name
  type    = "A"
  content = module.api.public_ip
  ttl     = 60
  proxied = false
}
