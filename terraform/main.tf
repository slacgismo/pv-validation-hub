terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-1"
  default_tags {
    tags = var.global_tags
  }
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  instance_tenancy     = "default"
  tags = {
    Name = "valhub-vpc"
  }
}

resource "aws_flow_log" "vpc_flow_log" {
  log_destination_type = "cloud-watch-logs"
  iam_role_arn         = aws_iam_role.vpc_flow_log_role.arn
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.main.id
  log_destination      = aws_cloudwatch_log_group.vpc_flow_log_group.arn
  tags = {
    Name = "valhub-vpc-flow-log"
  }
}

resource "aws_iam_role" "vpc_flow_log_role" {
  name = "valhub-vpc-flow-log-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  tags = {
    Name = "valhub-vpc-flow-log-role"
  }
}

resource "aws_cloudwatch_log_group" "vpc_flow_log_group" {
  name              = "valhub-vpc-flow-log-group"
  retention_in_days = 7
  kms_key_id        = aws_kms_key.cloudwatch_log_key.arn
  tags = {
    Name = "valhub-vpc-flow-log-group"
  }
}

resource "aws_kms_key" "cloudwatch_log_key" {
  description             = "KMS key for encrypting CloudWatch log group"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  tags = {
    Name = "valhub-cloudwatch-log-key"
  }
}

resource "aws_subnet" "public_subnets" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(var.public_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)

  tags = {
    Name = "valhub-public-subnet-${count.index + 1}"
  }
}

resource "aws_subnet" "private_subnets" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(var.private_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)

  tags = {
    Name = "valhub-private-subnet-${count.index + 1}"
  }
}
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "valhub-igw"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "valhub-public-route-table"
  }
}

resource "aws_route_table_association" "public_subnet_asso" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = element(aws_subnet.public_subnets[*].id, count.index)
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_eip" "nat_eip" {
  count = length(var.private_subnet_cidrs)

  tags = {
    Name = "valhub-nat-eip-${count.index + 1}"
  }

}

resource "aws_nat_gateway" "nat_gw" {
  count         = length(var.private_subnet_cidrs)
  allocation_id = aws_eip.nat_eip[count.index].id
  subnet_id     = element(aws_subnet.public_subnets[*].id, count.index)

  tags = {
    Name = "valhub-nat-gw-${count.index + 1}"
  }
}

# TODO: Clean up the NAT Gateway and EIP resources

resource "aws_security_group" "valhub_api_lb_sg" {
  name        = "valhub-api-lb-sg"
  description = "Security group for Valhub API Load Balancer"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "valhub-api-lb-sg"
  }
}


resource "aws_lb" "valhub_api_lb" {
  name               = "valhub-api-lb-tf"
  internal           = false
  load_balancer_type = "application"
  subnets            = aws_subnet.public_subnets[*].id
  security_groups    = [aws_security_group.valhub_api_lb_sg.id]

  ip_address_type = "ipv4"
  access_logs {
    enabled = false
    bucket  = ""
    prefix  = ""
  }
  idle_timeout                     = 60
  enable_deletion_protection       = false
  enable_http2                     = true
  enable_cross_zone_load_balancing = true
  tags = {
    Name = "valhub-api-lb-tf"
  }
}



module "asg" {
  source = "./autoscalinggroups"

  private_subnet_ids = aws_subnet.private_subnets[*].id
  public_subnet_ids  = aws_subnet.public_subnets[*].id
  vpc_id             = aws_vpc.main.id
}

module "cloudfront" {
  source = "./cloudfront"
}

module "sqs" {
  source = "./sqs"
}

module "s3" {
  source = "./s3"
}

module "rds" {
  source = "./rds"

  vpc_id             = aws_vpc.main.id
  private_subnet_ids = aws_subnet.private_subnets[*].id
}
