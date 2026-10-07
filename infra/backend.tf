# State must survive between deploys; the runner's disk is ephemeral. The
# bucket is a one-time manual bootstrap step (not managed by this config,
# same chicken-and-egg reasoning as ClipForge's clipforge-demo-quota-tfstate).
# No DynamoDB lock table - deploys are manual and rare, so optimistic
# S3-only locking is accepted here.
terraform {
  backend "s3" {
    bucket = "deskpilot-demo-tfstate"
    key    = "deskpilot-demo.tfstate"
    region = "us-east-1"
  }
}
