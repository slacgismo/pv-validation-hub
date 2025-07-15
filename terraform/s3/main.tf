resource "aws_s3_bucket" "valhub_bucket" {
  bucket = "valhub-bucket"
}

resource "aws_s3_bucket_versioning" "valhub_bucket_versioning" {
  bucket = aws_s3_bucket.valhub_bucket.id

  versioning_configuration {
    status = "Enabled"
  }

}

resource "aws_s3_bucket_logging" "valhub_bucket_logging" {
  bucket = aws_s3_bucket.valhub_bucket.id

  target_bucket = aws_s3_bucket.valhub_logs_bucket.id
  target_prefix = "logs/"

}

data "aws_iam_policy_document" "valhub_kms_bucket_key_policy_document" {
  version = "2012-10-17"

  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
    }

    actions = [
      "kms:*"
    ]

    resources = [
      "*"
    ]
  }

  # statement {
  #   effect = "Allow"

  #   principals {
  #     type        = "Service"
  #     identifiers = ["logdelivery.elasticloadbalancing.amazonaws.com"]
  #   }

  #   actions = [
  #     "s3:PutObject",
  #   ]

  #   # TODO: update prefix to match your log delivery prefix from module
  #   resources = [
  #     "arn:aws:s3:::${aws_s3_bucket.valhub_logs_bucket.id}/${var.api_lb_logs_prefix}/AWSLogs/${var.account_id}/*",
  #   ]


  # }
  # statement {
  #   effect = "Allow"
  #   principals {
  #     type        = "Service"
  #     identifiers = ["logdelivery.elasticloadbalancing.amazonaws.com"]
  #   }
  #   actions   = ["s3:GetBucketAcl"]
  #   resources = ["arn:aws:s3:::valhub-logs-bucket"]
  # }

}

data "aws_iam_policy_document" "valhub_logs_bucket_policy_document" {
  version = "2012-10-17"



  statement {
    effect = "Allow"

    principals {
      type = "AWS"
      # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html
      # us-west-2 797873946194
      identifiers = ["arn:aws:iam::${var.elb_account_id}:root"]
    }

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.valhub_logs_bucket.id}/api-lb-logs/AWSLogs/${var.account_id}/*",
    ]


  }


}

resource "aws_kms_key_policy" "valhub_kms_bucket_key_policy" {
  key_id = aws_kms_key.valhub_kms_bucket_key.id
  policy = data.aws_iam_policy_document.valhub_kms_bucket_key_policy_document.json
}

resource "aws_kms_key" "valhub_kms_bucket_key" {
  description             = "KMS key for encrypting S3 buckets"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  policy = data.aws_iam_policy_document.valhub_kms_bucket_key_policy_document.json

  tags = {
    Name = "valhub-kms-bucket-key"
  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_bucket_encryption" {
  bucket = aws_s3_bucket.valhub_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.arn
      sse_algorithm     = "aws:kms"
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

resource "aws_s3_bucket" "valhub_website" {
  bucket = "valhub-website-bucket"


}

resource "aws_s3_bucket_versioning" "valhub_website_versioning" {
  bucket = aws_s3_bucket.valhub_website.id

  versioning_configuration {
    status = "Enabled"
  }

}

resource "aws_s3_bucket_logging" "valhub_website_logging" {
  bucket = aws_s3_bucket.valhub_website.id

  target_bucket = aws_s3_bucket.valhub_logs_bucket.id
  target_prefix = "website-logs/"
}

resource "aws_s3_bucket_public_access_block" "valhub_website_public_access_block" {
  bucket = aws_s3_bucket.valhub_website.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_acl" "valhub_website_acl" {
  bucket = aws_s3_bucket.valhub_website.id
  acl    = "private"

}

resource "aws_s3_bucket_ownership_controls" "valhub_website_ownership_controls" {
  bucket = aws_s3_bucket.valhub_website.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_website_encryption" {
  bucket = aws_s3_bucket.valhub_website.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.arn
      sse_algorithm     = "aws:kms"
    }
  }

}

resource "aws_s3_bucket_policy" "valhub_logs_bucket_policy" {

  bucket = aws_s3_bucket.valhub_logs_bucket.id

  policy = data.aws_iam_policy_document.valhub_logs_bucket_policy_document.json
}

resource "aws_s3_bucket" "valhub_logs_bucket" {
  bucket = "valhub-logs-bucket"

}

resource "aws_s3_bucket_versioning" "valhub_logs_bucket_versioning" {
  bucket = aws_s3_bucket.valhub_logs_bucket.id

  versioning_configuration {
    status = "Enabled"
  }

}

resource "aws_s3_bucket_logging" "valhub_logs_bucket_logging" {
  bucket = aws_s3_bucket.valhub_logs_bucket.id

  target_bucket = aws_s3_bucket.valhub_logs_bucket.id
  target_prefix = "logs/"


}

resource "aws_s3_bucket_public_access_block" "valhub_logs_public_access_block" {
  bucket = aws_s3_bucket.valhub_logs_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true



}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_logs_encryption" {
  bucket = aws_s3_bucket.valhub_logs_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }

}

resource "aws_s3_bucket" "valhub_task_data_bucket" {
  bucket = "valhub-task-data-bucket"



}

resource "aws_s3_bucket_versioning" "valhub_task_data_bucket_versioning" {
  bucket = aws_s3_bucket.valhub_task_data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }

}

resource "aws_s3_bucket_logging" "valhub_task_data_bucket_logging" {
  bucket = aws_s3_bucket.valhub_task_data_bucket.id

  target_bucket = aws_s3_bucket.valhub_logs_bucket.id
  target_prefix = "task-data-logs/"

}

resource "aws_s3_bucket_public_access_block" "valhub_task_data_bucket_public_access_block" {
  bucket = aws_s3_bucket.valhub_task_data_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_server_side_encryption_configuration" "valhub_task_data_bucket_encryption" {
  bucket = aws_s3_bucket.valhub_task_data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.valhub_kms_bucket_key.arn
      sse_algorithm     = "aws:kms"
    }
  }

}
