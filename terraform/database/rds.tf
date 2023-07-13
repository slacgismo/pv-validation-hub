provider "aws" {
  version = "~> 2.0"
  region  = var.aws_region
}

resource "aws_security_group" "rds_security_group" {
  name_prefix = var.sg_name_prefix
  vpc_id      = var.vpc_id

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
  tags = merge(var.project_tags)
}

resource "aws_db_instance" "pv-validation-hub-rds" {
  identifier             = var.rds_identifier
  instance_class         = var.rds_instance_class
  allocated_storage      = var.rds_allocated_storage
  engine                 = var.rds_engine
  engine_version         = var.rds_engine_version
  username               = var.db_username
  password               = var.db_password
  publicly_accessible    = true
  skip_final_snapshot    = true
  tags = merge(var.project_tags)
  vpc_security_group_ids = [ 
    var.rds_security_group_id
  ]

    db_subnet_group_id = var.rds_subnet_group_id
}

resource "aws_secretsmanager_secret" "pv-valhub-dbsecret" {
  name                = var.secretsmanager_secret_name
  tags = merge(var.project_tags)
}

resource "aws_secretsmanager_secret_version" "pvinsight-db" {
  secret_id = aws_secretsmanager_secret.pv-valhub-dbsecret.id
  secret_string = jsonencode({
    "username": aws_db_instance.pv-validation-hub-rds.username
    "password": var.db_password
    "engine": aws_db_instance.pv-validation-hub-rds.engine
    "host": aws_db_instance.pv-validation-hub-rds.address
    "port": 5432
    "dbInstanceIdentifier": aws_db_instance.pv-validation-hub-rds.identifier
  })
}

########## OUTPUTS ############

output "db_endpoint" {
  description = "The connection endpoint for the RDS database"
  value       = aws_db_instance.pv-validation-hub-rds.endpoint
}
