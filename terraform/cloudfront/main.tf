resource "aws_cloudfront_distribution" "CloudFrontDistribution" {
  aliases = [
    "private-content.pv-validation-hub.org"
  ]
  origin {
    domain_name = "valhub-bucket.s3.us-west-2.amazonaws.com"
    origin_id   = "valhub-bucket.s3.us-west-2.amazonaws.com"

    origin_path = ""
    s3_origin_config {
      origin_access_identity = ""
    }
  }
  default_cache_behavior {
    cached_methods = [
      "HEAD",
      "GET"
    ]
    allowed_methods = [
      "HEAD",
      "GET"
    ]
    compress    = true
    default_ttl = 86400
    forwarded_values {
      cookies {
        forward = "none"
      }
      query_string = false
    }
    max_ttl                = 31536000
    min_ttl                = 0
    smooth_streaming       = false
    target_origin_id       = "valhub-bucket.s3.us-west-2.amazonaws.com"
    viewer_protocol_policy = "redirect-to-https"
  }
  comment     = ""
  price_class = "PriceClass_All"
  enabled     = true
  viewer_certificate {
    acm_certificate_arn            = "arn:aws:acm:us-east-1:041414866712:certificate/75619ac2-080f-45c4-bc88-c09fcb79d6fb"
    cloudfront_default_certificate = false
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  http_version    = "http2"
  is_ipv6_enabled = true
}

resource "aws_cloudfront_distribution" "CloudFrontDistribution2" {
  aliases = [
    "valhub.org"
  ]
  origin {
    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_keepalive_timeout = 5
      origin_protocol_policy   = "http-only"
      origin_read_timeout      = 30
      origin_ssl_protocols = [
        "TLSv1",
        "TLSv1.1",
        "TLSv1.2"
      ]
    }
    domain_name = "valhub-website.s3-website-us-west-2.amazonaws.com"
    origin_id   = "S3-WEBSITE-valhub-website"

    origin_path = ""
  }
  default_cache_behavior {
    cached_methods = aws_cloudfront_distribution.CloudFrontDistribution2.default_cache_behavior[0].cached_methods
    allowed_methods = [
      "HEAD",
      "GET",
      "OPTIONS"
    ]
    compress    = false
    default_ttl = 3600
    forwarded_values {
      cookies {
        forward = "none"
      }
      query_string = false
    }
    max_ttl                = 86400
    min_ttl                = 0
    smooth_streaming       = false
    target_origin_id       = "S3-WEBSITE-valhub-website"
    viewer_protocol_policy = "redirect-to-https"
  }
  comment     = ""
  price_class = "PriceClass_All"
  enabled     = true
  viewer_certificate {
    acm_certificate_arn            = "arn:aws:acm:us-east-1:041414866712:certificate/75619ac2-080f-45c4-bc88-c09fcb79d6fb"
    cloudfront_default_certificate = false
    minimum_protocol_version       = "TLSv1.2_2019"
    ssl_support_method             = "sni-only"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  http_version    = "http2"
  is_ipv6_enabled = true
}
