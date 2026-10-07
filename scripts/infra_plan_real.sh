#!/bin/sh
# Real `terraform plan` against the real AWS account + Cloudflare zone and
# the real S3 state (read-only - never applies). LocalStack/`terraform
# validate` catch syntax and schema problems, but not AWS-account-specific
# facts (missing IAM actions, an AMI's minimum root volume size, which AZs
# support a given instance type) - those only surface on a real plan/apply.
# Running this locally catches them in seconds instead of a full demo-up
# CI round-trip.
#
# Requires: an `aws configure` profile named "deskpilot" with the
# deskpilot-deploy credentials, the Cloudflare token at
# ~/.cloudflare-tokens/deskpilot, and `gh` authenticated as a repo admin
# (to read the production environment's vars - never its secrets).
set -e
cd "$(dirname "$0")/../infra"

REPO=hassan91199/deskpilot
CLOUDFLARE_TOKEN=$(cat ~/.cloudflare-tokens/deskpilot)
AWS_ACCOUNT_ID=$(AWS_PROFILE=deskpilot aws sts get-caller-identity --query Account --output text)
IMAGE_TAG=$(AWS_PROFILE=deskpilot aws ecr describe-images --repository-name deskpilot --region us-east-1 \
    --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' --output text)

VARS_JSON=$(as-hassan-personal gh variable list --repo "$REPO" --env production --json name,value)
var() {
    echo "$VARS_JSON" | python3 -c "
import sys, json
for v in json.load(sys.stdin):
    if v['name'] == '$1':
        print(v['value'])
        break
"
}

eval "$(AWS_PROFILE=deskpilot aws configure export-credentials --format env)"

tf() {
    docker run --rm \
        -v "$PWD":/workspace -w /workspace \
        -v deskpilot-tf-plugin-cache:/plugin-cache \
        -e TF_PLUGIN_CACHE_DIR=/plugin-cache \
        -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
        -e AWS_DEFAULT_REGION="$(var AWS_REGION)" \
        -e TF_VAR_image_uri="$AWS_ACCOUNT_ID.dkr.ecr.$(var AWS_REGION).amazonaws.com/deskpilot:$IMAGE_TAG" \
        -e TF_VAR_frontend_bucket_name="$(var FRONTEND_BUCKET_NAME)" \
        -e TF_VAR_frontend_domain_name="$(var FRONTEND_DOMAIN_NAME)" \
        -e TF_VAR_api_domain_name="$(var API_DOMAIN_NAME)" \
        -e TF_VAR_cloudflare_zone_id="$(var CLOUDFLARE_ZONE_ID)" \
        -e TF_VAR_cloudflare_api_token="$CLOUDFLARE_TOKEN" \
        -e TF_VAR_openai_api_key_param_arn="$(var OPENAI_API_KEY_PARAM_ARN)" \
        hashicorp/terraform:1.16 "$@"
}

tf init -input=false
tf plan -input=false
