resource "aws_s3_bucket" "valhub_bucket" {
  bucket = "valhub-bucket"

}

resource "aws_s3_bucket" "valhub_website" {
  bucket = "valhub-website-bucket"

}

resource "aws_s3_bucket" "valhub_logs" {
  bucket = "valhub-logs-bucket"

}

resource "aws_s3_bucket" "valhub_task_data_bucket" {
  bucket = "valhub-task-data-bucket"

}
