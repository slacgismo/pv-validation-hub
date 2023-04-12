provider "aws" {
  version = "~> 2.0"
  region  = "us-west-2"
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
}

resource "aws_ecs_cluster" "pv-validation-hub-test-cluster" {
  name = "pv-validation-hub-test-cluster" # Naming the cluster
}

resource "aws_cloudwatch_log_group" "ecs_task_log_group" {
  name = "/ecs/pv-validation-hub-test-task1" # Naming the log group
}

resource "aws_ecs_task_definition" "pv-validation-hub-test-task" {
  family                   = "pv-validation-hub-test-task" # Naming our first task
  container_definitions    = <<DEFINITION
  [
    {
      "name": "pv-validation-hub-test-task",
      "image": "041414866712.dkr.ecr.us-east-2.amazonaws.com/pv-validation-hub:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "hostPort": 3000
        }
      ],
      "memory": 512,
      "cpu": 256,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.ecs_task_log_group.name}",
          "awslogs-stream-prefix": "pv-validation-hub-test-task",
          "awslogs-create-group": "true",
          "awslogs-region": "us-west-2"
        },
      "command": ["/bin/sh", "/app/docker-entrypoint.sh"]
      }
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"] # Stating that we are using ECS Fargate
  network_mode             = "awsvpc"    # Using awsvpc as our network mode as this is required for Fargate
  memory                   = 512         # Specifying the memory our container requires
  cpu                      = 256         # Specifying the CPU our container requires
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
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

resource "aws_alb" "application_load_balancer" {
  name               = "pv-validation-hub-test-lb-tf" # Naming our load balancer
  load_balancer_type = "application"
  subnets = [ # Referencing the default subnets
    aws_subnet.pv-validation-hub_a.id,
    aws_subnet.pv-validation-hub_b.id
  ]
  # Referencing the security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

resource "aws_lb_target_group" "target_group" {
  name             = "valhub-target-group"
  port             = 80
  protocol         = "HTTP"
  target_type      = "ip"
  vpc_id           = aws_vpc.pv-validation-hub.id
  depends_on = [
    aws_alb.application_load_balancer
  ]
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_alb.application_load_balancer.arn # Referencing our load balancer
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn # Updating the target group ARN
  }
}

resource "aws_ecs_service" "valhub_my_first_service" {
  name            = "valhub-my-first-service"
  cluster         = aws_ecs_cluster.pv-validation-hub-test-cluster.id
  task_definition = aws_ecs_task_definition.pv-validation-hub-test-task.arn
  launch_type     = "FARGATE"
  desired_count   = 3

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn # Updated the target group ARN
    container_name   = aws_ecs_task_definition.pv-validation-hub-test-task.family
    container_port   = 3000
  }

  network_configuration {
    subnets          = [aws_subnet.pv-validation-hub_a.id, aws_subnet.pv-validation-hub_b.id]
    assign_public_ip = true
    security_groups  = [aws_security_group.valhub_ecs_service_security_group.id]
  }
}

resource "aws_db_instance" "pv-validation-hub-rds-test" {
  identifier             = "pv-validation-hub-rds-test"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "14.5"
  username               = "postgres"
  password               = var.db_password
  db_subnet_group_name = aws_db_subnet_group.rds_subnet_group.name
  publicly_accessible    = true
  skip_final_snapshot    = true
}

