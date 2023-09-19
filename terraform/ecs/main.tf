provider "aws" {
  version = "~> 2.0"
  region  = var.aws_region
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = var.ecs_task_execution_role_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  tags = merge(var.project_tags)
}

resource "aws_ecs_cluster" "pv-validation-hub-test-cluster" {
  name = var.ecs_cluster_name 
  tags = merge(var.project_tags)
}

resource "aws_cloudwatch_log_group" "ecs_task_log_group" {
  name = var.cloudwatch_log_group_name
  tags = merge(var.project_tags)
}

resource "aws_ecs_task_definition" "pv-validation-hub-test-task" {
  family                   = var.ecs_task_definition_family
  container_definitions    = <<DEFINITION
  [
    {
      "name": "${var.ecs_task_definition_container_name}",
      "image": "${var.ecs_task_definition_container_image}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80
        },
        {
          "containerPort": 443,
          "hostPort": 443
        },
        {
          "containerPort": 22,
          "hostPort": 22
        }
      ],
      "memory": ${var.ecs_task_definition_memory},
      "cpu": ${var.ecs_task_definition_cpu},
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.ecs_task_log_group.name}",
          "awslogs-stream-prefix": "${var.ecs_task_definition_container_name}",
          "awslogs-create-group": "true",
          "awslogs-region": "${var.aws_region}"
        },
      "command": ["/bin/sh", "/app/docker-entrypoint.sh"]
      }
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = var.ecs_task_definition_memory
  cpu                      = var.ecs_task_definition_cpu
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = var.valhub_ecs_task_role
  tags = merge(var.project_tags)
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_smpolicy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = var.ecs_secrets_manager_policy_arn
}

resource "aws_alb" "application_load_balancer" {
  name               = var.alb_name
  load_balancer_type = "application"
  subnets = var.subnet_ids
  security_groups = ["${var.load_balancer_security_group_id}"]
  tags = merge(var.project_tags)
}

resource "aws_lb_target_group" "target_group" {
  name             = var.lb_target_group_name
  port             = 80
  protocol         = "HTTP"
  target_type      = "ip"
  vpc_id           = var.vpc_id
  depends_on = [
    aws_alb.application_load_balancer
  ]
  tags = merge(var.project_tags)

    health_check {
    path                = "/healthy/"
    interval            = 60
    timeout             = 10  # Optional: Adjust this timeout as needed
    healthy_threshold   = 5  # Optional: Adjust as needed
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_alb.application_load_balancer.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }
}

resource "aws_lb_listener" "secure_listener" {
  load_balancer_arn = aws_alb.application_load_balancer.arn
  port              = 443  # Change the port to 443 for HTTPS
  protocol          = "HTTPS"  # Use HTTPS for SSL/TLS

  ssl_policy = "ELBSecurityPolicy-2016-08"
  certificate_arn = var.valhub_certificate_arn  # Specify your SSL certificate ARN here

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }
}

resource "aws_ecs_service" "valhub_my_first_service" {
  name            = var.ecs_service_name
  cluster         = aws_ecs_cluster.pv-validation-hub-test-cluster.id
  task_definition = aws_ecs_task_definition.pv-validation-hub-test-task.arn
  launch_type     = "FARGATE"
  desired_count   = var.ecs_service_desired_count

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = aws_ecs_task_definition.pv-validation-hub-test-task.family
    container_port   = 80
  }

  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = true
    security_groups  = [ var.valhub_ecs_service_security_group_id ]
  }
    # Add health check grace period (in seconds)
  health_check_grace_period_seconds = 120  # Adjust this value as needed

  tags = merge(var.project_tags)
}

########### OUTPUTS #############

output "alb_arn" {
  description = "The ARN of the Application Load Balancer"
  value       = aws_alb.application_load_balancer.arn
}

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = aws_alb.application_load_balancer.dns_name
}

output "alb_hosted_zone_id" {
  description = "The canonical hosted zone ID of the Application Load Balancer (to be used in Route 53 Record Sets)"
  value       = aws_alb.application_load_balancer.zone_id
}