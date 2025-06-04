resource "aws_kms_key" "valhub_kms_key" {
  description             = "KMS key for encrypting SQS queue"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  tags = {
    Name = "valhub-kms-key"
  }

}

resource "aws_sqs_queue" "SQSQueue" {
  name                        = "valhub_submission_queue.fifo"
  content_based_deduplication = false
  delay_seconds               = 0
  fifo_queue                  = true
  max_message_size            = 262144
  message_retention_seconds   = 345600
  receive_wait_time_seconds   = 0
  visibility_timeout_seconds  = 21600
  kms_master_key_id           = aws_kms_key.valhub_kms_key.id

  tags = {
    Name = "valhub_submission_queue"
  }
}
