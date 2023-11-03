# Configure provider
provider "aws" {
  region = var.aws_region
}

########### SECURITY #############

resource "aws_security_group" "load_balancer_security_group" {
  name_prefix = "${var.sg_name_prefix}-lb"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [
      var.vpc_cidr_block,
      "pv-validation-hub.org",
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "admin_ec2_security_group" {
  name_prefix = "${var.sg_name_prefix}-ec2"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "valhub_api_service_security_group" {
  name_prefix = "${var.sg_name_prefix}-api"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [aws_security_group.load_balancer_security_group.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "valhub_worker_service_security_group" {
  name_prefix = "${var.sg_name_prefix}-worker"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 0
    to_port     = 0
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

resource "aws_security_group" "rds_security_group" {
  name_prefix = "${var.sg_name_prefix}-rds"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    # 
    cidr_blocks = []
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_proxy_security_group" {
  name_prefix = "${var.sg_name_prefix}-rds-proxy"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    security_groups = [
      aws_security_group.valhub_api_service_security_group.id,
      aws_security_group.rds_security_group.id,
      aws_security_group.admin_ec2.id,
      aws_security_group.valhub_worker_service_security_group.id,
      aws_default_security_group.vpc_security_group.id
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(var.project_tags)
}

# replaces the vpc default security group
# allows all egress and only ingress from within the vpc

resource "aws_default_security_group" "vpc_security_group" {
  name_prefix = "${var.sg_name_prefix}-vpc"
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    # include all security groups in the vpc
    security_groups = [
      aws_security_group.load_balancer_security_group.id,
      aws_security_group.valhub_api_service_security_group.id,
      aws_security_group.rds_security_group.id,
      aws_security_group.rds_proxy_security_group.id,
      aws_security_group.admin_ec2.id,
      aws_security_group.valhub_worker_service_security_group.id,
      aws_default_security_group.vpc_security_group.id
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }
}

########### Network Resources #############

resource "aws_vpc" "pv-validation-hub" {
  cidr_block = var.vpc_cidr_block
  tags = {
      Name = var.vpc_name
    }
  enable_dns_support = true
  enable_dns_hostnames = true
}

resource "aws_sqs_queue" "valhub_submission_queue" {
  name = "valhub_submission_queue.fifo"
  fifo_queue = true

  policy = jsonencode({
    Version = "2012-10-17"
    Id = "example-policy"
    Statement = [
      {
        Sid = "allow-api-service-to-send-messages"
        Effect = "Allow"
        Principal = "*"
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.example.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_security_group.valhub_api_service_security_group.arn
          }
        }
      },
      {
        Sid = "allow-worker-service-to-receive-messages"
        Effect = "Allow"
        Principal = "*"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl",
        ]
        Resource = aws_sqs_queue.example.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_security_group.valhub_worker_service_security_group.arn
          }
        }
      }
    ]
  })
}

resource "aws_internet_gateway" "pv-validation-hub_igw" {
  vpc_id = aws_vpc.pv-validation-hub.id
}

resource "aws_subnet" "pv-validation-hub_a" {
  cidr_block        = var.subnet_cidr_block_1
  availability_zone = var.subnet_availability_zone_1
  vpc_id            = aws_vpc.pv-validation-hub.id
}

resource "aws_subnet" "pv-validation-hub_b" {
  cidr_block        = var.subnet_cidr_block_2
  availability_zone = var.subnet_availability_zone_2
  vpc_id            = aws_vpc.pv-validation-hub.id
}

resource "aws_subnet" "pv-validation-hub_c" {
  cidr_block        = var.subnet_cidr_block_3
  availability_zone = var.subnet_availability_zone_3
  vpc_id            = aws_vpc.pv-validation-hub.id
}

resource "aws_subnet" "pv-validation-hub_d" {
  cidr_block        = var.subnet_cidr_block_4
  availability_zone = var.subnet_availability_zone_1
  vpc_id            = aws_vpc.pv-validation-hub.id
}

resource "aws_subnet" "pv-validation-hub_e" {
  cidr_block        = var.subnet_cidr_block_5
  availability_zone = var.subnet_availability_zone_2
  vpc_id            = aws_vpc.pv-validation-hub.id
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name        = "pv_validation_rds_subnets"
  subnet_ids  = [aws_subnet.pv-validation-hub_c.id,aws_subnet.pv-validation-hub_d.id,aws_subnet.pv-validation-hub_e.id]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.pv-validation-hub.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.pv-validation-hub_igw.id
  }

  tags = {
    Name = "public"
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.pv-validation-hub_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.pv-validation-hub_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_c" {
  subnet_id      = aws_subnet.pv-validation-hub_c.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_d" {
  subnet_id      = aws_subnet.pv-validation-hub_d.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_e" {
  subnet_id      = aws_subnet.pv-validation-hub_e.id
  route_table_id = aws_route_table.public.id
}

######### Outputs for use in other modules

output "rds_subnet_group_id" {
  value = aws_db_subnet_group.rds_subnet_group.id
}

output "rds_subnet_group_name" {
  value = aws_db_subnet_group.rds_subnet_group.name
}

output "vpc_id" {
  value = aws_vpc.pv-validation-hub.id
}

output "subnet_ids" {
  value = [
    aws_subnet.pv-validation-hub_a.id,
    aws_subnet.pv-validation-hub_b.id,
    aws_subnet.pv-validation-hub_c.id,
    aws_subnet.pv-validation-hub_d.id,
    aws_subnet.pv-validation-hub_e.id,
  ]
}

output "load_balancer_security_group_id" {
  value = aws_security_group.load_balancer_security_group.id
}

output "valhub_api_service_security_group_id" {
  value = aws_security_group.valhub_api_service_security_group.id
}

output "rds_security_group_id" {
  value = aws_security_group.rds_security_group.id
}

output "rds_proxy_security_group_id" {
  value = aws_security_group.rds_proxy_security_group.id
}

output "vpc_security_group_id" {
  value = aws_security_group.vpc_security_group.id
}
