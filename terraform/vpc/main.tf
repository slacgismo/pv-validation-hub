resource "aws_vpc" "main" {
  assign_generated_ipv6_cidr_block     = false
  cidr_block                           = var.cidr_block
  enable_dns_hostnames                 = true
  enable_dns_support                   = true
  enable_network_address_usage_metrics = false
  instance_tenancy                     = "default"
  ipv4_ipam_pool_id                    = null
  ipv4_netmask_length                  = null
  ipv6_cidr_block                      = null
  ipv6_cidr_block_network_border_group = null
  ipv6_ipam_pool_id                    = null
  ipv6_netmask_length                  = null
  tags = {
    Name = var.vpc_name
  }
}

data "aws_iam_policy_document" "cloudwatch_log_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${var.aws_region}.amazonaws.com"]
    }
    actions = [
      "kms:*"
    ]
    resources = ["*"]
    condition {
      test     = "ArnLike"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:aws:logs:${var.aws_region}:${var.account_id}:log-group:*"]
    }
  }



  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
    }

    actions = [
      "kms:*"
    ]

    resources = [
      "*"
    ]
  }

}

resource "aws_kms_key_policy" "cloudwatch_log_policy" {
  key_id = aws_kms_key.cloudwatch_log_key.id
  policy = data.aws_iam_policy_document.cloudwatch_log_policy_document.json
}

resource "aws_kms_key" "cloudwatch_log_key" {
  description             = "KMS key for encrypting CloudWatch log group"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  policy = data.aws_iam_policy_document.cloudwatch_log_policy_document.json

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


resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(var.public_subnet_cidrs, 0)
  availability_zone = element(var.azs, 0)

  tags = {
    Name = "valhub-public-subnet-1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(var.public_subnet_cidrs, 1)
  availability_zone = element(var.azs, 1)

  tags = {
    Name = "valhub-public-subnet-2"
  }
}


resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(var.private_subnet_cidrs, 0)
  availability_zone = element(var.azs, 0)

  tags = {
    Name = "valhub-private-subnet-1"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(var.private_subnet_cidrs, 1)
  availability_zone = element(var.azs, 1)

  tags = {
    Name = "valhub-private-subnet-2"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "valhub-igw"
  }
}

resource "aws_route_table" "public_route_table_1" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "valhub-public-route-table-1"
  }
}

resource "aws_route_table" "public_route_table_2" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "valhub-public-route-table-2"
  }
}

resource "aws_route_table" "private_route_table_1" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "valhub-private-route-table-1"
  }
}

resource "aws_route" "nat_route_1" {
  route_table_id         = aws_route_table.private_route_table_1.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gw.id
}

resource "aws_route" "nat_route_2" {
  route_table_id         = aws_route_table.private_route_table_2.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gw.id
}

resource "aws_route_table" "private_route_table_2" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "valhub-private-route-table-2"
  }
}

resource "aws_route_table_association" "public_subnet_asso_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table_1.id
}

resource "aws_route_table_association" "public_subnet_asso_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_route_table_2.id
}

resource "aws_route_table_association" "private_subnet_asso_1" {
  subnet_id      = aws_subnet.private_subnet_1.id
  route_table_id = aws_route_table.private_route_table_1.id
}

resource "aws_route_table_association" "private_subnet_asso_2" {
  subnet_id      = aws_subnet.private_subnet_2.id
  route_table_id = aws_route_table.private_route_table_2.id
}

resource "aws_eip" "nat_eip" {

  tags = {
    Name = "valhub-nat-eip"
  }

}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet_1.id

  tags = {
    Name = "valhub-nat-gw"
  }

}


resource "aws_vpc_security_group_ingress_rule" "valhub_api_ingress_rule_http" {
  security_group_id = aws_security_group.valhub_api_lb_sg.id

  description = "Allow HTTP traffic from anywhere"
  from_port   = 80
  to_port     = 80
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"

}

resource "aws_vpc_security_group_ingress_rule" "valhub_api_ingress_rule_https" {
  security_group_id = aws_security_group.valhub_api_lb_sg.id

  description = "Allow HTTPS traffic to anywhere"
  from_port   = 443
  to_port     = 443
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "valhub_api_egress_rule" {
  security_group_id = aws_security_group.valhub_api_lb_sg.id

  description = "Allow all outbound traffic"
  from_port   = -1
  to_port     = -1
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"

}

resource "aws_security_group" "valhub_api_lb_sg" {
  name        = "valhub-api-lb-sg"
  description = "Security group for Valhub API Load Balancer"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "valhub-api-lb-sg"
  }
}


resource "aws_lb" "valhub_api_lb" {
  name                       = "valhub-api-lb-tf"
  internal                   = false
  load_balancer_type         = "application"
  subnets                    = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
  security_groups            = [aws_security_group.valhub_api_lb_sg.id]
  drop_invalid_header_fields = true
  ip_address_type            = "ipv4"
  access_logs {
    enabled = false
    bucket  = var.log_bucket_id
    prefix  = var.api_lb_logs_prefix
  }
  idle_timeout                     = 60 * 15
  enable_deletion_protection       = true
  enable_http2                     = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "valhub-api-lb-tf"
  }

}

resource "aws_lb_target_group" "api_target_group" {
  name        = "valhub-api-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  health_check {
    path                = "/healthy/"
    protocol            = "HTTP"
    port                = "80"
    healthy_threshold   = 2
    unhealthy_threshold = 5

    # TODO: Fix the health check to use HTTPS
    # The health check is currently set to HTTP, but it should be HTTPS
    # The health check is redirected to HTTPS and will return a 301 status code
    # Added matcher to accept 2xx and 3xx responses for a healthy check
    matcher = "200-399" # Accept 2xx and 3xx responses
  }

  tags = {
    Name = "valhub-api-target-group"
  }

  depends_on = [aws_lb.valhub_api_lb]
}





resource "aws_lb_listener" "api_listener_http" {
  load_balancer_arn = aws_lb.valhub_api_lb.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = {
    Name = "valhub-api-listener-http"
  }
}

resource "aws_acm_certificate" "valhub_acm_certificate_us_west_2" {


  domain_name       = "*.${var.domain_name}"
  validation_method = "DNS"


  tags = {
    Name = "valhub-certificate-us-west-2"
  }

}

resource "aws_lb_listener" "api_listener_https" {
  load_balancer_arn = aws_lb.valhub_api_lb.id
  port              = 443
  protocol          = "HTTPS"

  ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-Res-2021-06"
  certificate_arn = aws_acm_certificate.valhub_acm_certificate_us_west_2.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_target_group.arn
  }

  tags = {
    Name = "valhub-api-listener-https"
  }

}


resource "aws_vpc_security_group_ingress_rule" "ecs_worker_ingress_rule_http" {
  security_group_id = aws_security_group.ecs_worker_sg.id

  description = "Allow HTTP traffic from anywhere"
  from_port   = 80
  to_port     = 80
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"

}

resource "aws_vpc_security_group_ingress_rule" "ecs_worker_ingress_rule_https" {
  security_group_id = aws_security_group.ecs_worker_sg.id

  description = "Allow HTTPS traffic from anywhere"
  from_port   = 443
  to_port     = 443
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"

}

resource "aws_security_group" "ecs_worker_sg" {
  name        = "valhub-ecs-worker-sg"
  description = "Security group for Valhub ECS Worker"
  vpc_id      = aws_vpc.main.id



  tags = {
    Name = "valhub-ecs-worker-sg"
  }
}



