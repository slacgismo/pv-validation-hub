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
  identifier                          = "valhub-rds-instance"
  allocated_storage                   = 20
  instance_class                      = var.db_instance_class
  engine                              = "postgres"
  manage_master_user_password         = true
  username                            = "valhub_admin"
  master_user_secret_kms_key_id       = aws_kms_key.valhub_rds_kms_key.arn
  backup_window                       = "09:39-10:09"
  backup_retention_period             = 5
  maintenance_window                  = "fri:07:07-fri:07:37"
  multi_az                            = false
  engine_version                      = "14.12"
  auto_minor_version_upgrade          = true
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
