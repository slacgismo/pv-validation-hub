provider "aws" {
  version = "~> 3.5"
  region  = var.aws_region
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = var.ecs_worker_task_execution_role_name
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

resource "aws_ecs_cluster" "pv-validation-hub-worker-cluster" {
  name = var.ecs_worker_cluster_name 
  tags = merge(var.project_tags)
}

resource "aws_cloudwatch_log_group" "ecs_task_log_group" {
  name = var.cloudwatch_worker_log_group_name
  tags = merge(var.project_tags)
}

resource "aws_ecs_task_definition" "pv-validation-hub-worker-task" {
  family                   = var.worker_task_definition_family
  container_definitions    = <<DEFINITION
  [
    {
      "name": "${var.worker_task_definition_container_name}",
      "image": "${var.worker_task_definition_container_image}",
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
        },
        {
          "containerPort": 65535,
          "hostPort": 65535
        }
      ],
      "memory": ${var.worker_task_definition_memory},
      "cpu": ${var.worker_task_definition_cpu},
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.ecs_task_log_group.name}",
          "awslogs-stream-prefix": "${var.worker_task_definition_container_name}",
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
  memory                   = var.worker_task_definition_memory
  cpu                      = var.worker_task_definition_cpu
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

resource "aws_ecs_service" "valhub_worker_service" {
  name            = var.ecs_worker_service
  cluster         = aws_ecs_cluster.pv-validation-hub-worker-cluster.id
  task_definition = aws_ecs_task_definition.pv-validation-hub-worker-task.arn
  launch_type     = "FARGATE"
  desired_count   = var.worker_service_desired_count

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = aws_ecs_task_definition.pv-validation-hub-worker-task.family
    container_port   = 80
  }

  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = true
    security_groups  = [ var.valhub_worker_service_security_group_id ]
  }
    # Add health check grace period (in seconds)
  health_check_grace_period_seconds = 120  # Adjust this value as needed

  tags = merge(var.project_tags)
}
