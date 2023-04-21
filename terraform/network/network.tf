

resource "aws_security_group" "load_balancer_security_group" {
  name_prefix = var.sg_name_prefix
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 80
    to_port     = 80
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

resource "aws_security_group" "valhub_ecs_service_security_group" {
  name_prefix = var.sg_name_prefix
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [
      aws_subnet.pv-validation-hub_a.cidr_block,
      aws_subnet.pv-validation-hub_b.cidr_block,
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_security_group" {
  name_prefix = var.sg_name_prefix
  vpc_id      = aws_vpc.pv-validation-hub.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [
      aws_subnet.pv-validation-hub_c.cidr_block,
      aws_subnet.pv-validation-hub_d.cidr_block,
      aws_subnet.pv-validation-hub_e.cidr_block
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "pv-validation-hub" {
  cidr_block = var.vpc_cidr_block
  tags = {
      Name = var.vpc_name
    }
  enable_dns_support = true
  enable_dns_hostnames = true
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

output "valhub_ecs_service_security_group_id" {
  value = aws_security_group.valhub_ecs_service_security_group.id
}

output "rds_security_group_id" {
  value = aws_security_group.rds_security_group.id
}
