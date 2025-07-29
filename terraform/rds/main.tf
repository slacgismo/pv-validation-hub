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

resource "aws_vpc_security_group_ingress_rule" "valhub_rds_ingress_rule" {
  security_group_id = aws_security_group.valhub_rds_sg.id
  ip_protocol       = "tcp"
  from_port         = 5432
  to_port           = 5432
  cidr_ipv4         = "0.0.0.0/0"

}

resource "aws_vpc_security_group_egress_rule" "valhub_rds_egress_rule" {
  security_group_id = aws_security_group.valhub_rds_sg.id
  from_port         = -1
  to_port           = -1
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_security_group" "valhub_rds_sg" {
  name        = "valhub-rds-sg"
  description = "Security group for ValHub RDS instance"
  vpc_id      = var.vpc_id

  tags = {
    Name = "valhub-rds-sg"
  }


}

resource "aws_db_instance" "valhub_rds_instance" {
  identifier        = "valhub-rds-instance"
  allocated_storage = 20
  instance_class    = var.db_instance_class
  engine            = "postgres"
  username          = var.valhub_rds_proxy_secrets["username"]
  password          = var.valhub_rds_proxy_secrets["password"]
  # master_user_secret_kms_key_id = aws_kms_key.valhub_rds_kms_key.arn
  backup_window              = "09:39-10:09"
  backup_retention_period    = 5
  maintenance_window         = "fri:07:07-fri:07:37"
  multi_az                   = false
  engine_version             = "17.5"
  auto_minor_version_upgrade = true
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


resource "aws_db_proxy_target" "valhub_rds_proxy_target" {
  db_proxy_name          = aws_db_proxy.valhub_rds_proxy.name
  target_group_name      = aws_db_proxy_default_target_group.valhub_rds_proxy_default_target_group.name
  db_instance_identifier = aws_db_instance.valhub_rds_instance.identifier
}

# resource "aws_db_proxy_endpoint" "valhub_rds_proxy_endpoint" {
#   db_proxy_name          = aws_db_proxy.valhub_rds_proxy.name
#   db_proxy_endpoint_name = "valhub-rds-proxy-endpoint"
#   vpc_subnet_ids         = var.private_subnet_ids
#   vpc_security_group_ids = [aws_security_group.valhub_rds_sg.id]

#   tags = {
#     Name = "valhub-rds-proxy-endpoint"
#   }
# }

resource "aws_db_proxy_default_target_group" "valhub_rds_proxy_default_target_group" {
  db_proxy_name = aws_db_proxy.valhub_rds_proxy.name

  connection_pool_config {
    max_connections_percent   = 100
    connection_borrow_timeout = 120
    session_pinning_filters = [
      "EXCLUDE_VARIABLE_SETS"
    ]
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

data "aws_iam_policy_document" "valhub_rds_proxy_policy_permissions_document" {
  statement {
    effect = "Allow"
    actions = [
      "rds:*",
      "secretsmanager:*",
      "kms:*",
    ]
    resources = [
      "*"
    ]
  }

}

resource "aws_iam_policy" "valhub_rds_proxy_policy" {
  name        = "valhub-rds-proxy-policy"
  description = "Policy for ValHub RDS Proxy to access secrets and connect to the database"

  policy = data.aws_iam_policy_document.valhub_rds_proxy_policy_permissions_document.json

  tags = {
    Name = "valhub-rds-proxy-policy"
  }

}

resource "aws_iam_policy_attachment" "valhub_rds_proxy_policy_attachment" {
  name       = "valhub-rds-proxy-policy-attachment"
  roles      = [aws_iam_role.valhub_rds_proxy_role.name]
  policy_arn = aws_iam_policy.valhub_rds_proxy_policy.arn


}

data "aws_iam_policy_document" "valhub_rds_proxy_assume_role_policy_document" {

  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com", "secretsmanager.amazonaws.com", "kms.amazonaws.com"]
    }
  }

}

resource "aws_iam_role" "valhub_rds_proxy_role" {
  name = "valhub-rds-proxy-role"

  assume_role_policy = data.aws_iam_policy_document.valhub_rds_proxy_assume_role_policy_document.json

  tags = {
    Name = "valhub-rds-proxy-role"
  }
}

resource "aws_secretsmanager_secret" "valhub_rds_proxy_secret" {
  name        = "valhub-rds-proxy-credentials"
  description = "Credentials for ValHub RDS Proxy authentication"

  tags = {
    Name = "valhub-rds-proxy-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "valhub_rds_proxy_secret_version" {
  secret_id     = aws_secretsmanager_secret.valhub_rds_proxy_secret.id
  secret_string = jsonencode(var.valhub_rds_proxy_secrets)
}
