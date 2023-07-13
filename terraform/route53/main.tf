provider "aws" {
  region = var.aws_region
}

resource "aws_route53_zone" "main" {
  name = "pv-validation-hub.org"

  tags = merge(
    var.project_tags
  )
}

resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.pv-validation-hub.org"
  type    = "A"

  alias {
    name                   = var.api_endpoint
    zone_id                = var.api_zone_id
    evaluate_target_health = true
  }

  tags = merge(
    var.project_tags
  )
}

resource "aws_route53_record" "db" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "db.pv-validation-hub.org"
  type    = "A"

  alias {
    name                   = var.db_endpoint
    zone_id                = "Z1PVAVKGZ6KD59" # This is the hardcoded Route 53 zone ID for RDS instances
    evaluate_target_health = true
  }

  tags = merge(
    var.project_tags
  )
}

resource "aws_route53_record" "cf" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "pv-validation-hub.org"
  type    = "A"

  alias {
    name                   = var.cf_endpoint
    zone_id                = var.cf_zone_id
    evaluate_target_health = true
  }

  tags = merge(
    var.project_tags
  )
}
