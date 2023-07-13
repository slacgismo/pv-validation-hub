provider "aws" {
  version = "~> 2.0"
  region  = var.aws_region
}

resource "aws_cloudfront_distribution" "my_distribution" {
  origin {
    domain_name = var.bucket_name
    origin_id   = "S3-${var.bucket_name}"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.my_identity.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = var.default_root_object

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-${var.bucket_name}"

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
  
  tags = merge(var.project_tags)
}

########## OUTPUTS #############

output "cloudfront_distribution_domain_name" {
  description = "The domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.my_distribution.domain_name
}

output "cloudfront_distribution_hosted_zone_id" {
  description = "The hosted zone ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.my_distribution.hosted_zone_id
}
