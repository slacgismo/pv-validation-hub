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
  value       = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
}

output "api_target_group_arn" {
  description = "ARN of the API target group"
  value       = aws_lb_target_group.api_target_group.arn
}

output "api_lb_logs_prefix" {
  description = "S3 bucket prefix for API Load Balancer logs"
  value       = var.api_lb_logs_prefix
}
