resource "aws_kms_key" "valhub_rds_kms_key" {
  description             = "KMS key for ValHub RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "valhub-kms-key"
  }
}

resource "aws_kms_key" "valhub_performance_insights_key" {
  description             = "KMS key for ValHub RDS Performance Insights"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "valhub-performance-insights-key"
  }

}

resource "aws_db_subnet_group" "valhub_rds_subnet_group" {
  name       = "valhub-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "valhub-rds-subnet-group"
  }

}

resource "aws_security_group" "valhub_rds_sg" {
  name        = "valhub-rds-sg"
  description = "Security group for ValHub RDS instance"
  vpc_id      = var.vpc_id

  # TODO: add ingress and egress rules as needed via separate resources`
  # To avoid these problems, use the current best practice of the aws_vpc_security_group_egress_rule and aws_vpc_security_group_ingress_rule resources with one CIDR block per rule.

  tags = {
    Name = "valhub-rds-sg"
  }


}

resource "aws_db_instance" "valhub_rds_instance" {
  identifier                    = "valhub-rds-instance"
  allocated_storage             = 20
  instance_class                = var.db_instance_class
  engine                        = "postgres"
  manage_master_user_password   = true
  username                      = "valhub_admin"
  master_user_secret_kms_key_id = aws_kms_key.valhub_rds_kms_key.arn
  backup_window                 = "09:39-10:09"
  backup_retention_period       = 5
  maintenance_window            = "fri:07:07-fri:07:37"
  multi_az                      = false
  engine_version                = "17.5"
  auto_minor_version_upgrade    = true
  # allow_major_version_upgrade         = true # Uncomment if you want to allow major version upgrades
  license_model                       = "postgresql-license"
  publicly_accessible                 = false
  storage_type                        = "gp2"
  port                                = 5432
  storage_encrypted                   = true
  copy_tags_to_snapshot               = false
  monitoring_interval                 = 0
  iam_database_authentication_enabled = true
  deletion_protection                 = true
  skip_final_snapshot                 = true
  performance_insights_enabled        = true
  performance_insights_kms_key_id     = aws_kms_key.valhub_performance_insights_key.arn
  db_subnet_group_name                = aws_db_subnet_group.valhub_rds_subnet_group.name
  vpc_security_group_ids              = [aws_security_group.valhub_rds_sg.id]


  tags = {
    Name = "valhub-rds-instance"
  }
}

resource "aws_db_proxy_default_target_group" "valhub_rds_proxy_default_target_group" {
  db_proxy_name = aws_db_proxy.valhub_rds_proxy.name
  connection_pool_config {
    max_connections_percent      = 100
    max_idle_connections_percent = 50
    connection_borrow_timeout    = 120
    session_pinning_filters      = ["EXCLUDE_VARIABLE_SETS"]
  }


}

resource "aws_db_proxy_target" "valhub_rds_proxy_target" {
  db_proxy_name          = aws_db_proxy.valhub_rds_proxy.name
  target_group_name      = aws_db_proxy_default_target_group.valhub_rds_proxy_default_target_group.name
  db_instance_identifier = aws_db_instance.valhub_rds_instance.identifier
}

resource "aws_db_proxy_endpoint" "valhub_rds_proxy_endpoint" {
  db_proxy_name          = aws_db_proxy.valhub_rds_proxy.name
  db_proxy_endpoint_name = "valhub-rds-proxy-endpoint"
  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = [aws_security_group.valhub_rds_sg.id]

  tags = {
    Name = "valhub-rds-proxy-endpoint"
  }
}

resource "aws_db_proxy" "valhub_rds_proxy" {
  name                   = "valhub-rds-proxy"
  engine_family          = "POSTGRESQL"
  role_arn               = aws_iam_role.valhub_rds_proxy_role.arn
  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = [aws_security_group.valhub_rds_sg.id]

  auth {
    auth_scheme = "SECRETS"
    description = "Authentication for ValHub RDS Proxy"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.valhub_rds_proxy_secret.arn
  }

  tags = {
    Name = "valhub-rds-proxy"
  }
}

resource "aws_iam_role" "valhub_rds_proxy_role" {
  name = "valhub-rds-proxy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })

  tags = {
    Name = "valhub-rds-proxy-role"
  }
}

resource "aws_secretsmanager_secret" "valhub_rds_proxy_secret" {
  name        = "valhub-rds-proxy-secret"
  description = "Secret for ValHub RDS Proxy authentication"

  tags = {
    Name = "valhub-rds-proxy-secret"
  }
}

resource "aws_secretsmanager_secret_version" "valhub_rds_proxy_secret_version" {
  secret_id     = aws_secretsmanager_secret.valhub_rds_proxy_secret.id
  secret_string = jsonencode(var.valhub_rds_proxy_secrets)
}
