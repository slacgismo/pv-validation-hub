

resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  instance_tenancy     = "default"
  tags = {
    Name = "valhub-vpc"
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

resource "aws_cloudwatch_log_group" "vpc_flow_log_group" {
  name              = "valhub-vpc-flow-log-group"
  retention_in_days = 7
  kms_key_id        = aws_kms_key.cloudwatch_log_key.arn
  tags = {
    Name = "valhub-vpc-flow-log-group"
  }
}

data "aws_iam_policy_document" "vpc_flow_log_assume_role_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }

}

resource "aws_iam_role" "vpc_flow_log_role" {
  name = "valhub-vpc-flow-log-role"

  assume_role_policy = data.aws_iam_policy_document.vpc_flow_log_assume_role_policy.json

  tags = {
    Name = "valhub-vpc-flow-log-role"
  }
}


data "aws_iam_policy_document" "vpc_flow_log_policy" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
    ]

    resources = [
      aws_cloudwatch_log_group.vpc_flow_log_group.arn
    ]
  }

}

resource "aws_iam_role_policy" "vpc_flow_log_policy" {
  name = "valhub-vpc-flow-log-policy"
  role = aws_iam_role.vpc_flow_log_role.id

  policy = data.aws_iam_policy_document.vpc_flow_log_policy.json

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

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_security_group" "valhub_api_lb_sg" {
  name        = "valhub-api-lb-sg"
  description = "Security group for Valhub API Load Balancer"
  vpc_id      = aws_vpc.main.id

  # TODO: add ingress and egress rules as needed via separate resources`
  # To avoid these problems, use the current best practice of the aws_vpc_security_group_egress_rule and aws_vpc_security_group_ingress_rule resources with one CIDR block per rule.

  tags = {
    Name = "valhub-api-lb-sg"
  }
}


resource "aws_lb" "valhub_api_lb" {
  name                       = "valhub-api-lb-tf"
  internal                   = true
  load_balancer_type         = "application"
  subnets                    = aws_subnet.public_subnets[*].id
  security_groups            = [aws_security_group.valhub_api_lb_sg.id]
  drop_invalid_header_fields = true
  ip_address_type            = "ipv4"
  access_logs {
    enabled = true
    bucket  = var.log_bucket_id
    prefix  = "api-lb-logs"
  }
  idle_timeout                     = 60
  enable_deletion_protection       = false
  enable_http2                     = true
  enable_cross_zone_load_balancing = true
  tags = {
    Name = "valhub-api-lb-tf"
  }
}

