resource "aws_acm_certificate" "valhub_acm_certificate" {
  domain_name       = var.website_domain_name
  validation_method = "DNS"
  tags = {
    Name = "valhub-certificate"
  }

}

resource "aws_wafv2_web_acl" "valhub_waf_web_acl" {
  name        = "valhub-web-acl"
  description = "WAF ACL for ValHub"
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "valhubWebACL"
    sampled_requests_enabled   = true
  }

  rule {
    name     = "RateLimitRule"
    priority = 1
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  tags = {
    Name = "valhub-waf-web-acl"
  }

}

resource "aws_cloudfront_distribution" "valhub_private_content_cloudfront_distribution" {



  aliases = [
    "private-content.pv-validation-hub.org"
  ]
  web_acl_id = aws_wafv2_web_acl.valhub_waf_web_acl.id
  origin {
    domain_name = var.valhub_bucket_domain_name
    origin_id   = var.private_origin_id

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
    target_origin_id       = var.private_origin_id
    viewer_protocol_policy = "redirect-to-https"
  }
  comment     = ""
  price_class = "PriceClass_All"
  enabled     = true

  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.valhub_acm_certificate.arn
    cloudfront_default_certificate = false
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  logging_config {
    bucket          = var.valhub_logs_bucket_domain_name
    include_cookies = false
    prefix          = "cloudfront-logs/private-content/"
  }

  http_version    = "http2"
  is_ipv6_enabled = true
}




resource "aws_cloudfront_distribution" "valhub_website_cloudfront_distribution" {
  aliases = [
    "pv-validation-hub.org"
  ]

  web_acl_id = aws_wafv2_web_acl.valhub_waf_web_acl.id

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
    domain_name = var.valhub_website_bucket_domain_name
    origin_id   = var.website_origin_id
  }
  default_cache_behavior {
    cached_methods = [
      "HEAD",
      "GET",
      "OPTIONS"
    ]
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
    target_origin_id       = var.website_origin_id
    viewer_protocol_policy = "redirect-to-https"
  }
  comment     = ""
  price_class = "PriceClass_All"
  enabled     = true
  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.valhub_acm_certificate.arn
    cloudfront_default_certificate = false
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  logging_config {
    bucket = var.valhub_logs_bucket_domain_name

    include_cookies = false
    prefix          = "cloudfront-logs/valhub-website/"
  }

  http_version    = "http2"
  is_ipv6_enabled = true
}
