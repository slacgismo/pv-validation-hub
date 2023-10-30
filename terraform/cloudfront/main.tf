provider "aws" {
  version = "~> 3.5"
  region  = var.aws_region
}

data "aws_s3_bucket" "pv-validation-hub-website" {
  bucket = var.bucket_name
}

resource "aws_cloudfront_distribution" "pv-validation-hub-website" {
  origin {
    domain_name = data.aws_s3_bucket.pv-validation-hub-website.website_endpoint
    origin_id   = "S3-WEBSITE-${data.aws_s3_bucket.pv-validation-hub-website.id}"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }


  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = var.default_root_object

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-WEBSITE-${data.aws_s3_bucket.pv-validation-hub-website.id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.acm_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2019"
  }

  aliases = [var.alt_domain_name] 
  
  tags = merge(var.project_tags)
}

########## OUTPUTS #############

output "cloudfront_distribution_domain_name" {
  description = "The domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.pv-validation-hub-website.domain_name
}

output "cloudfront_distribution_hosted_zone_id" {
  description = "The hosted zone ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.pv-validation-hub-website.hosted_zone_id
}
