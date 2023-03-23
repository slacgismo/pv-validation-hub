

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

resource "aws_vpc" "pv-validation-hub" {
  cidr_block = var.vpc_cidr_block
  tags = {
      Name = var.vpc_name
    }
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
