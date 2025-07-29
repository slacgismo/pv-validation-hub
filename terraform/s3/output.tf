output "valhub_logs_bucket_domain_name" {
  value = aws_s3_bucket.valhub_logs_bucket.bucket_regional_domain_name
}
output "valhub_logs_bucket_id" {
  value = aws_s3_bucket.valhub_logs_bucket.id
}

output "valhub_website_bucket_domain_name" {
  value = aws_s3_bucket.valhub_website.bucket_regional_domain_name
}

output "valhub_bucket_domain_name" {
  value = aws_s3_bucket.valhub_bucket.bucket_regional_domain_name

}
