output "aws_region" {
  description = "AWS region"
  value       = var.aws_region

}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id

}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private_subnets[*].id

}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public_subnets[*].id
}

output "valhub_api_lb_arn" {
  description = "Load Balancer for Valhub API"
  value       = aws_lb.valhub_api_lb.arn
}

output "api_lb_logs_prefix" {
  description = "S3 bucket prefix for API Load Balancer logs"
  value       = var.api_lb_logs_prefix
}
