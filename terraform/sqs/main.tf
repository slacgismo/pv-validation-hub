resource "aws_kms_key" "valhub_kms_key" {
  description             = "KMS key for encrypting SQS queue"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  tags = {
    Name = "valhub-kms-key"
  }

}

# TODO: Narrow down the permissions for the SQS queue policy
data "aws_iam_policy_document" "submission_queue_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sqs.amazonaws.com"]
    }

    actions = [
      "sqs:*"
    ]

    resources = [
      aws_sqs_queue.submission_queue.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "kms:*"
    ]

    resources = [
      aws_kms_key.valhub_kms_key.arn
    ]
  }

}

resource "aws_sqs_queue_policy" "submission_queue_policy" {
  queue_url = aws_sqs_queue.submission_queue.id

  policy = data.aws_iam_policy_document.submission_queue_policy_document.json

}

resource "aws_sqs_queue" "submission_queue" {
  name                        = "valhub_submission_queue.fifo"
  content_based_deduplication = false
  delay_seconds               = 0
  fifo_queue                  = true
  max_message_size            = 262144
  message_retention_seconds   = 345600
  receive_wait_time_seconds   = 0
  visibility_timeout_seconds  = 21600
  kms_master_key_id           = aws_kms_key.valhub_kms_key.arn


  tags = {
    Name = "valhub_submission_queue"
  }
}
