# DP-8: a single EC2 instance running three containers - postgres, the
# FastAPI api, and Caddy - instead of App Runner/ECS Fargate + RDS. EC2 so
# there is no AWS-managed proxy in the request path to impose an
# undocumented timeout on /chat's SSE stream (see ClipForge CF-35: App
# Runner silently killed the same shape of multi-minute SSE response even
# with an active heartbeat). Postgres as a container on this same instance
# rather than RDS: the whole instance (and its data) is destroyed on every
# teardown anyway, and ingest reseeds it fresh on every boot, so RDS's
# persistence buys nothing here - just a slower, more complex up/down cycle.

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_subnet" "default" {
  for_each = toset(data.aws_subnets.default.ids)
  id       = each.value
}

# Not every AZ in a region supports every instance type - pick a subnet
# whose AZ actually offers var.instance_type instead of an arbitrary first
# subnet.
data "aws_ec2_instance_type_offerings" "available" {
  filter {
    name   = "instance-type"
    values = [var.instance_type]
  }
  location_type = "availability-zone"
}

locals {
  supported_subnet_ids = [
    for s in data.aws_subnet.default : s.id
    if contains(data.aws_ec2_instance_type_offerings.available.locations, s.availability_zone)
  ]
}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "this" {
  name        = "${var.app_name}-instance"
  description = "DeskPilot demo instance: HTTP(S) + the raw container port for smoke-testing. Postgres (5432) is never opened here - only reachable from inside the instance."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTPS (Caddy)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP (ACME challenge + redirect)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Raw container port, for CI smoke-testing before DNS/TLS are ready"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "instance" {
  name = "${var.app_name}-instance"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_instance_profile" "this" {
  name = "${var.app_name}-instance"
  role = aws_iam_role.instance.name
}

resource "aws_iam_role_policy" "ecr_pull" {
  name = "${var.app_name}-ecr-pull"
  role = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
      ]
      Resource = "*"
    }]
  })
}

# Same SecureString-by-ARN pattern as ClipForge: secret values never pass
# through a Terraform variable or get baked into the image, only resolved
# at boot by the instance's own role (see user-data).
resource "aws_iam_role_policy" "secrets" {
  count = length(var.secret_env_vars) > 0 ? 1 : 0
  name  = "${var.app_name}-secrets"
  role  = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ssm:GetParameter"
        Resource = values(var.secret_env_vars)
      },
      {
        Effect   = "Allow"
        Action   = "kms:Decrypt"
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${data.aws_region.current.name}.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "logs" {
  name = "${var.app_name}-logs"
  role = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
      ]
      Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/deskpilot/${var.app_name}*"
    }]
  })
}

resource "aws_instance" "this" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = local.supported_subnet_ids[0]
  vpc_security_group_ids = [aws_security_group.this.id]
  iam_instance_profile   = aws_iam_instance_profile.this.name

  associate_public_ip_address = true

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
  }

  user_data_replace_on_change = true
  user_data = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    region          = data.aws_region.current.name
    image_uri       = var.image_uri
    container_port  = var.container_port
    domain_name     = var.domain_name
    log_group       = "/deskpilot/${var.app_name}"
    plain_env_vars  = var.plain_env_vars
    secret_env_vars = var.secret_env_vars
  })

  tags = {
    Name = var.app_name
  }
}
