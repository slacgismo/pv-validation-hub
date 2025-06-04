resource "aws_ami" "worker_ami" {
  name                = "valhub-worker-ami"
  virtualization_type = "hvm"
  architecture        = "x86_64"
  root_device_name    = "/dev/xvda"
  ebs_block_device {
    device_name           = "/dev/xvda"
    volume_size           = 8
    delete_on_termination = true
    encrypted             = true
  }
  tags = {
    Name = "valhub-worker-ami"
  }
}

resource "aws_autoscaling_group" "asg" {
  desired_capacity     = var.asg_desired_capacity
  max_size             = var.asg_max_size
  min_size             = var.asg_min_size
  vpc_zone_identifier  = var.private_subnet_ids
  launch_configuration = aws_launch_configuration.lc.id
  # availability_zones   = var.private_subnet_ids

  tag {
    key                 = "Name"
    value               = "valhub-asg"
    propagate_at_launch = true
  }
}

resource "aws_launch_configuration" "lc" {
  name          = "valhub-launch-configuration"
  image_id      = aws_ami.worker_ami.id
  instance_type = "t2.micro"

  root_block_device {
    volume_size = 8
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"
  }

  lifecycle {
    create_before_destroy = true
  }

}

resource "aws_ecs_cluster" "worker_cluster" {
  name = "valhub-worker-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "valhub-worker-cluster"
  }
}

resource "aws_ecs_cluster" "api_cluster" {
  name = "valhub-api-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = {
    Name = "valhub-api-cluster"
  }
}

resource "aws_kms_key" "ecr_kms_key" {
  description             = "KMS key for ECR repository encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  tags = {
    Name = "valhub-ecr-kms-key"
  }

}

resource "aws_ecr_repository" "api_repository" {
  name = "valhub-api"

  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr_kms_key.arn
  }

  tags = {
    Name = "valhub-api-repository"
  }
}

resource "aws_ecr_repository" "worker_repository" {
  name                 = "valhub-worker"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr_kms_key.arn
  }
  tags = {
    Name = "valhub-worker-repository"
  }
}

data "aws_iam_policy_document" "ecs_service_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]

    # TODO: Specify the resources more precisely
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "ecs_service_role_policy" {
  name   = "valhub-ecs-service-role-policy"
  role   = aws_iam_role.ecs_service_role.id
  policy = data.aws_iam_policy_document.ecs_service_role_policy_document.json
}

resource "aws_iam_role" "ecs_service_role" {
  name               = "valhub-ecs-service-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_service_role_policy_document.json

  tags = {
    Name = "valhub-ecs-service-role"
  }
}

# # TODO: Clean up ECS service
resource "aws_ecs_service" "ecs_worker_service" {
  name                               = "worker-service"
  cluster                            = aws_ecs_cluster.worker_cluster.id
  desired_count                      = 1
  task_definition                    = aws_ecs_task_definition.ecs_worker_task_definition.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  iam_role                           = aws_iam_role.ecs_service_role.arn

  depends_on = [aws_iam_role_policy.ecs_service_role_policy]

  ordered_placement_strategy {
    type  = "spread"
    field = "attribute:ecs.availability-zone"
  }
  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }
  network_configuration {
    assign_public_ip = false
    subnets          = var.private_subnet_ids
  }
  scheduling_strategy = "REPLICA"

  tags = {
    Name = "valhub-ecs-worker-service"
  }
}

# TODO: Clean up ECS task definition\

data "aws_iam_policy_document" "ecs_task_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]


    # TODO: Specify the resources more precisely
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_task_role_policy" {
  name        = "valhub-ecs-task-role-policy"
  description = "Policy for ECS task role to allow access to ECR and CloudWatch Logs"
  policy      = data.aws_iam_policy_document.ecs_task_role_policy_document.json

  tags = {
    Name = "valhub-ecs-task-role-policy"
  }

}

resource "aws_iam_role" "ecs_task_role" {
  name               = "valhub-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_role_policy_document.json
  tags = {
    Name = "valhub-ecs-task-role"
  }
}

data "aws_iam_policy_document" "ecs_worker_task_execution_role_policy_document" {
  # TODO: Add task execution role policy document
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]

    # TODO: Specify the resources more precisely
    resources = ["*"]
  }

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sqs.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]

    # TODO: Specify the resources more precisely
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "secretsmanager:GetSecretValue",
    ]

    # TODO: Specify the resources more precisely
    resources = ["*"]
  }

}

resource "aws_iam_policy" "ecs_worker_task_execution_role_policy" {
  name        = "valhub-ecs-worker-task-execution-role-policy"
  description = "Policy for ECS worker task execution role to allow access to ECR and CloudWatch Logs"
  policy      = data.aws_iam_policy_document.ecs_worker_task_execution_role_policy_document.json

  tags = {
    Name = "valhub-ecs-worker-task-execution-role-policy"
  }

}

resource "aws_iam_role" "ecs_worker_task_execution_role" {
  name               = "valhub-ecs-worker-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_worker_task_execution_role_policy_document.json

  tags = {
    Name = "valhub-ecs-worker-task-execution-role"
  }

}

data "aws_iam_policy_document" "ecs_api_task_execution_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]

    # TODO: Specify the resources more precisely
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "secretsmanager:GetSecretValue",
    ]

    # TODO: Specify the resources more precisely
    resources = ["*"]
  }

}

resource "aws_iam_policy" "ecs_api_task_execution_role_policy" {
  name        = "valhub-ecs-api-task-execution-role-policy"
  description = "Policy for ECS API task execution role to allow access to ECR and CloudWatch Logs"
  policy      = data.aws_iam_policy_document.ecs_api_task_execution_role_policy_document.json

  tags = {
    Name = "valhub-ecs-api-task-execution-role-policy"
  }

}

resource "aws_iam_role" "ecs_api_task_execution_role" {
  name               = "valhub-ecs-api-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_api_task_execution_role_policy_document.json

  tags = {
    Name = "valhub-ecs-api-task-execution-role"
  }

}



resource "aws_ecs_task_definition" "ecs_worker_task_definition" {
  container_definitions = jsonencode([
    {
      name              = "valhub-worker-task-ec2",
      image             = aws_ecr_repository.worker_repository.repository_url,
      cpu               = 4096,
      memory            = 12288,
      memoryReservation = 12288,
      portMappings = [
        {
          containerPort = 80,
          hostPort      = 80,
          protocol      = "tcp",
          name          = "valhub-worker-task-ec2-80-tcp"
        },
        {
          containerPort = 443,
          hostPort      = 443,
          protocol      = "tcp",
          name          = "valhub-worker-task-ec2-443-tcp"
        },
        {
          containerPort = 22,
          hostPort      = 22,
          protocol      = "tcp",
          name          = "valhub-worker-task-ec2-22-tcp"
        },
        {
          containerPort = 65535,
          hostPort      = 65535,
          protocol      = "tcp",
          name          = "valhub-worker-task-ec2-65535-tcp"
        }
      ],
      essential   = true,
      environment = [],
      mountPoints = [
        {
          sourceVolume  = "docker_in_docker",
          containerPath = "/var/run/docker.sock"
        },
        {
          sourceVolume  = "current_evaluation",
          containerPath = "/root/worker/current_evaluation",
          readOnly      = false
        }
      ],
      volumesFrom = [],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/valhub-worker-task-ec2",
          awslogs-create-group  = "true",
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "valhub-worker-task-ec2"
        }
      },
      systemControls = []
    }
  ])

  family             = "valhub-worker-task-ec2"
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  execution_role_arn = aws_iam_role.ecs_worker_task_execution_role.arn
  network_mode       = "awsvpc"

  volume {
    name      = "docker_in_docker"
    host_path = "/var/run/docker.sock"
  }
  volume {
    name      = "current_evaluation"
    host_path = "/home/current_evaluation"
  }
  requires_compatibilities = [
    "EC2"
  ]
  cpu    = "4096"
  memory = "12288"
  tags = {
    Name = "valhub-ecs-worker-task-definition"
  }
}

# TODO: Clean up ECS service

resource "aws_lb_target_group" "api_target_group" {
  name     = "valhub-api-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  tags = {
    Name = "valhub-api-target-group"
  }
}

resource "aws_ecs_service" "ecs_api_service" {
  name    = "ecs-api-service"
  cluster = aws_ecs_cluster.api_cluster.id
  load_balancer {
    target_group_arn = aws_lb_target_group.api_target_group.arn
    container_name   = aws_ecr_repository.api_repository.name
    container_port   = 80
  }
  desired_count                      = 1
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  task_definition                    = aws_ecs_task_definition.ecs_api_task_definition.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  iam_role                           = aws_iam_role.ecs_service_role.arn
  depends_on                         = [aws_iam_role_policy.ecs_service_role_policy]

  network_configuration {
    assign_public_ip = false
    # TODO: Update security groups and subnets
    security_groups = [
      "sg-08f04514e1770cd92"
    ]
    subnets = var.public_subnet_ids
  }
  health_check_grace_period_seconds = 120
  scheduling_strategy               = "REPLICA"

  tags = {
    Name = "valhub-ecs-api-service"
  }
}


# TODO: Clean up ECS task definition
resource "aws_ecs_task_definition" "ecs_api_task_definition" {
  container_definitions = jsonencode([
    {
      name   = "valhub-api-task",
      image  = aws_ecr_repository.api_repository.repository_url,
      cpu    = 1024,
      memory = 2048,
      portMappings = [
        {
          containerPort = 80,
          hostPort      = 80,
          protocol      = "tcp"
        },
        {
          containerPort = 443,
          hostPort      = 443,
          protocol      = "tcp"
        },
        {
          containerPort = 22,
          hostPort      = 22,
          protocol      = "tcp"
        }
      ],
      essential   = true,
      environment = [],
      mountPoints = [],
      volumesFrom = [],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/valhub-api-task",
          awslogs-create-group  = "true",
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "valhub-api-task"
        }
      },
      systemControls = []
    }
  ])
  family             = "valhub-api-task"
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  execution_role_arn = aws_iam_role.ecs_worker_task_execution_role.arn
  network_mode       = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  cpu    = "1024"
  memory = "2048"

  tags = {
    Name = "valhub-ecs-api-task-definition"
  }
}
