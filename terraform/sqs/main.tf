resource "aws_sqs_queue" "SQSQueue" {
  content_based_deduplication = false
  delay_seconds               = 0
  fifo_queue                  = true
  max_message_size            = 262144
  message_retention_seconds   = 345600
  receive_wait_time_seconds   = 0
  visibility_timeout_seconds  = 21600
  name                        = "valhub_submission_queue.fifo"
}
