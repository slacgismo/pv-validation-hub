provider "aws" {
  version = "~> 3.5"
  region  = var.aws_region
}

########## DATA ############

data "aws_secretsmanager_secret" "pv-valhub-dbsecret" {
  name                = var.secretsmanager_secret_name
}

########## POSTGRES RDS ############

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
  db_subnet_group_name   = var.db_subnet_group_name
}

########## DB PROXY ############

resource "aws_iam_role" "valhub_db_proxy_role" {
  name = "valhub-db-proxy-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "rds.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

resource "aws_iam_policy" "valhub_proxy_secrets_manager_policy" {
  name        = "valhub-secrets-manager-policy"
  description = "Policy to allow RDS Proxy to read secrets from Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "secretsmanager:GetSecretValue",
        ],
        Resource = data.aws_secretsmanager_secret.pv-valhub-dbsecret.arn
      },
    ],
  })
}

resource "aws_iam_role_policy_attachment" "proxy_secrets_manager_attachment" {
  policy_arn = aws_iam_policy.valhub_proxy_secrets_manager_policy.arn
  role       = aws_iam_role.valhub_db_proxy_role.name
}

resource "aws_db_proxy" "valhub_db_proxy" {
  name                     = "valhub-db-proxy"
  debug_logging            = false
  idle_client_timeout      = 1800
  require_tls              = true
  role_arn                 = aws_iam_role.valhub_db_proxy_role.arn
  vpc_security_group_ids   = [aws_security_group.rds_security_group.id]
  vpc_subnet_ids           = var.subnet_ids
  engine_family            = "POSTGRESQL"
  tags                     = merge(var.project_tags)

  auth {
    auth_scheme = "SECRETS"
    description = "Proxy auth scheme"
    iam_auth    = "DISABLED"
    secret_arn  = data.aws_secretsmanager_secret.pv-valhub-dbsecret.arn
  }

}

resource "aws_db_proxy_default_target_group" "valhub_proxy_target_group" {
  db_proxy_name = aws_db_proxy.valhub_db_proxy.name

  connection_pool_config {
    connection_borrow_timeout    = 120
    max_connections_percent      = 100
    max_idle_connections_percent = 50
  }
}

resource "aws_db_proxy_target" "valhub_db_proxy_target" {
  db_proxy_name = aws_db_proxy.valhub_db_proxy.name
  db_instance_identifier = aws_db_instance.pv-validation-hub-rds.identifier
  target_group_name      = aws_db_proxy_default_target_group.valhub_proxy_target_group.name
}

########## SECRETS MANAGER ############

resource "aws_secretsmanager_secret_version" "pvinsight-db" {
  secret_id = data.aws_secretsmanager_secret.pv-valhub-dbsecret.id
  secret_string = jsonencode({
    "username": var.db_username
    "password": var.db_password
    "engine": aws_db_instance.pv-validation-hub-rds.engine
    "host": aws_db_instance.pv-validation-hub-rds.address
    "port": 5432
    "dbInstanceIdentifier": aws_db_instance.pv-validation-hub-rds.identifier
    "proxy": aws_db_proxy.valhub_db_proxy.endpoint
  })
}

########## OUTPUTS ############

output "db_endpoint" {
  description = "The connection endpoint for the RDS database"
  value       = aws_db_instance.pv-validation-hub-rds.endpoint
}

output "rds_proxy_endpoint" {
  value = aws_db_proxy.valhub_db_proxy.endpoint
}
