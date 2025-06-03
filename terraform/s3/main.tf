resource "aws_s3_bucket" "valhub_bucket" {
  bucket = "valhub-bucket"
}

resource "aws_kms_key" "valhub_kms_bucket_key" {
  description             = "KMS key for encrypting S3 buckets"
  enable_key_rotation     = true
  deletion_window_in_days = 7
  tags = {
    Name = "valhub-kms-bucket-key"
  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_bucket_encryption" {
  bucket = aws_s3_bucket.valhub_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.id
      sse_algorithm     = "AES256"
    }
  }

}

resource "aws_s3_bucket_public_access_block" "valhub_bucket_public_access_block" {
  bucket = aws_s3_bucket.valhub_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true

}
# ------------ 

resource "aws_s3_bucket" "valhub_website" {
  bucket = "valhub-website-bucket"

}

resource "aws_s3_bucket_public_access_block" "valhub_website_public_access_block" {
  bucket = aws_s3_bucket.valhub_website.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true

}


resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_website_encryption" {
  bucket = aws_s3_bucket.valhub_website

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.id
      sse_algorithm     = "AES256"
    }
  }

}

resource "aws_s3_bucket" "valhub_logs" {
  bucket = "valhub-logs-bucket"

}

resource "aws_s3_bucket_public_access_block" "valhub_logs_public_access_block" {
  bucket = aws_s3_bucket.valhub_logs.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_logs_encryption" {
  bucket = aws_s3_bucket.valhub_logs

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.id
      sse_algorithm     = "AES256"
    }
  }

}

resource "aws_s3_bucket" "valhub_task_data_bucket" {
  bucket = "valhub-task-data-bucket"

}

resource "aws_s3_bucket_public_access_block" "valhub_task_data_bucket_public_access_block" {
  bucket = aws_s3_bucket.valhub_task_data_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_task_data_bucket_encryption" {
  bucket = aws_s3_bucket.valhub_task_data_bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.id
      sse_algorithm     = "AES256"
    }
  }

}
