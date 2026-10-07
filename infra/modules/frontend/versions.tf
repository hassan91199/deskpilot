# CloudFront requires its ACM cert in us-east-1 regardless of the stack's
# primary region - the root module passes that aliased provider in.
terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 5.0"
      configuration_aliases = [aws.us_east_1]
    }
  }
}
