provider "aws" {
  region = var.aws_region
}

data "aws_route53_zone" "main" {
  name = "pv-validation-hub.org"
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "api.pv-validation-hub.org"
  type    = "A"

  alias {
    name                   = var.api_endpoint
    zone_id                = var.elb_hosted_zone_id // The hosted zone ID of the load balancer
    evaluate_target_health = true
  }

}

resource "aws_route53_record" "db" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "db.pv-validation-hub.org"
  type    = "CNAME"
  ttl     = "300"
  records = [var.db_endpoint]
}


resource "aws_route53_record" "cf" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "pv-validation-hub.org"
  type    = "A"

  alias {
    name                   = var.cf_endpoint
    zone_id                = var.cf_zone_id
    evaluate_target_health = false
  }
}
