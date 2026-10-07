provider "aws" {
  region = var.region
}

# CloudFront's ACM cert must live in us-east-1 regardless of var.region.
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}
