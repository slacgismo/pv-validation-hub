# Configure provider
provider "aws" {
  region = var.aws_region
}


# Define the CloudFront distribution
resource "aws_cloudfront_distribution" "my_distribution" {
  origin {
    domain_name = aws_s3_bucket.my_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.my_bucket.id}"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.my_identity.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # Set up caching behavior
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-${aws_s3_bucket.my_bucket.id}/build"

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
    cloudfront_default_certificate = true
  }
}

# Define the DNS record in Route53
resource "aws_route53_record" "my_dns_record" {
  zone_id = data.aws_route53_zone.my_zone.id
  name    = "pv-validation-hub.org"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.my_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.my_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

######### OUTPUTS ############


output "s3_bucket_name" {
  value = aws_s3_bucket.my_bucket.id
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.my_distribution.id
}

output "dns_record_name" {
  value = aws_route53_record.my_dns_record.fqdn
}


