provider "aws" {
  version = "~> 2.0"
  region  = "us-west-2"
}

resource "aws_security_group" "rds_security_group" {
  name_prefix = var.sg_name_prefix
  vpc_id      = "vpc-ab2ff6d3"

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

resource "aws_db_instance" "pv-validation-hub-rds-test" {
  identifier             = "pv-validation-hub-rds-test"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "14.5"
  username               = "postgres"
  password               = var.db_password
  publicly_accessible    = true
  skip_final_snapshot    = true
}

resource "aws_secretsmanager_secret" "pv-valhub-dbsecret" {
  name                = "pvinsight-db"
}

resource "aws_secretsmanager_secret_version" "pvinsight-db" {
  secret_id = aws_secretsmanager_secret.pv-valhub-dbsecret.id
  secret_string = jsonencode({
    "username": aws_db_instance.pv-validation-hub-rds-test.username
    "password": var.db_password
    "engine": aws_db_instance.pv-validation-hub-rds-test.engine
    "host": aws_db_instance.pv-validation-hub-rds-test.address
    "port": 5432
    "dbInstanceIdentifier": aws_db_instance.pv-validation-hub-rds-test.identifier
  })
}