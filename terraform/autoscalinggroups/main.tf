# resource "aws_ami" "worker_ami" {
#   name                = "valhub-worker-ami"
#   virtualization_type = "hvm"
#   architecture        = "x86_64"
#   root_device_name    = "/dev/xvda"
#   ebs_block_device {
#     device_name           = "/dev/xvda"
#     volume_size           = 8
#     delete_on_termination = true
#     encrypted             = true
#   }
#   tags = {
#     Name = "valhub-worker-ami"
#   }
# }

data "aws_ami" "worker_ami" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# TODO: Uncomment when rest of the code is ready
resource "aws_autoscaling_group" "worker_asg" {
  desired_capacity     = var.asg_desired_capacity
  max_size             = var.asg_max_size
  min_size             = var.asg_min_size
  vpc_zone_identifier  = var.private_subnet_ids
  launch_configuration = aws_launch_configuration.worker_lc.id
  # availability_zones   = var.private_subnet_ids

  tag {
    key                 = "Name"
    value               = "valhub-worker-asg"
    propagate_at_launch = true
  }
}

resource "aws_launch_configuration" "worker_lc" {
  name_prefix   = "valhub-worker-lc-"
  image_id      = data.aws_ami.worker_ami.id
  instance_type = var.worker_instance_type

  root_block_device {
    volume_size = var.worker_volume_size
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


resource "aws_ecs_service" "ecs_worker_service" {
  name                               = "worker-service"
  cluster                            = aws_ecs_cluster.worker_cluster.id
  desired_count                      = 1
  task_definition                    = aws_ecs_task_definition.ecs_worker_task_definition.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

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
  }
}


resource "aws_iam_role" "ecs_task_role" {
  name               = var.ecs_task_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_role_policy_document.json
  tags = {
    Name = var.ecs_task_role_name
  }
}

data "aws_iam_policy_document" "ecs_worker_task_execution_assume_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole"
    ]
  }
}

data "aws_iam_policy_document" "ecs_worker_task_execution_permissions_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = ["sqs:*"]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "secretsmanager:GetSecretValue",
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_worker_task_execution_role_policy" {
  name        = "valhub-ecs-worker-task-execution-role-policy"
  description = "Policy for ECS worker task execution role to allow access to ECR and CloudWatch Logs"
  policy      = data.aws_iam_policy_document.ecs_worker_task_execution_permissions_policy_document.json

  tags = {
    Name = "valhub-ecs-worker-task-execution-role-policy"
  }
}

# resource "aws_iam_policy" "ecs_worker_task_execution_role_policy" {
#   name        = "valhub-ecs-worker-task-execution-role-policy"
#   description = "Policy for ECS worker task execution role to allow access to ECR and CloudWatch Logs"
#   policy      = data.aws_iam_policy_document.ecs_worker_task_execution_role_policy_document.json

#   tags = {
#     Name = "valhub-ecs-worker-task-execution-role-policy"
#   }

# }

resource "aws_iam_role" "ecs_worker_task_execution_role" {
  name               = "valhub-ecs-worker-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_worker_task_execution_assume_role_policy_document.json

  tags = {
    Name = "valhub-ecs-worker-task-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_worker_task_execution_role_policy_attachment" {
  role       = aws_iam_role.ecs_worker_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_worker_task_execution_role_policy.arn
}

data "aws_iam_policy_document" "ecs_api_task_execution_assume_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole"
    ]
  }
}

data "aws_iam_policy_document" "ecs_api_task_execution_permissions_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:CreateLogGroup"
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "secretsmanager:GetSecretValue"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_api_task_execution_role_policy" {
  name        = "valhub-ecs-api-task-execution-role-policy"
  description = "Policy for ECS API task execution role to allow access to ECR and CloudWatch Logs"
  policy      = data.aws_iam_policy_document.ecs_api_task_execution_permissions_policy_document.json

  tags = {
    Name = "valhub-ecs-api-task-execution-role-policy"
  }
}

resource "aws_iam_role" "ecs_api_task_execution_role" {
  name               = "valhub-ecs-api-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_api_task_execution_assume_role_policy_document.json

  tags = {
    Name = "valhub-ecs-api-task-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_api_task_execution_role_policy_attachment" {
  role       = aws_iam_role.ecs_api_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_api_task_execution_role_policy.arn
}



resource "aws_ecs_task_definition" "ecs_worker_task_definition" {
  container_definitions = jsonencode([
    {
      name              = "${var.ecs_worker_task_name}",
      image             = aws_ecr_repository.worker_repository.repository_url,
      cpu               = var.worker_cpu_units,
      memory            = var.worker_memory_size,
      memoryReservation = var.worker_memory_reservation_size,
      portMappings = [
        {
          containerPort = 80,
          hostPort      = 80,
          protocol      = "tcp",
          name          = "${var.ecs_worker_task_name}-80-tcp"
        },
        {
          containerPort = 443,
          hostPort      = 443,
          protocol      = "tcp",
          name          = "${var.ecs_worker_task_name}-443-tcp"
        },
        {
          containerPort = 22,
          hostPort      = 22,
          protocol      = "tcp",
          name          = "${var.ecs_worker_task_name}-22-tcp"
        },
        {
          containerPort = 65535,
          hostPort      = 65535,
          protocol      = "tcp",
          name          = "${var.ecs_worker_task_name}-65535-tcp"
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
          awslogs-group         = "/ecs/${var.ecs_worker_task_name}",
          awslogs-create-group  = "true",
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "${var.ecs_worker_task_name}"
        }
      },
      systemControls = []
    }
  ])

  family             = var.ecs_worker_task_name
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

  tags = {
    Name = "valhub-ecs-worker-task-definition"
  }
}

# TODO: Clean up ECS service



resource "aws_ecs_service" "ecs_api_service" {
  name    = "ecs-api-service"
  cluster = aws_ecs_cluster.api_cluster.id

  desired_count                      = 1
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  task_definition                    = aws_ecs_task_definition.ecs_api_task_definition.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  load_balancer {
    target_group_arn = var.api_target_group_arn
    container_name   = var.ecs_api_task_name
    container_port   = 80
  }

  network_configuration {
    assign_public_ip = true # TODO: turn on for production

    subnets = var.public_subnet_ids
  }
  health_check_grace_period_seconds = 120
  scheduling_strategy               = "REPLICA"

  tags = {
    Name = "valhub-ecs-api-service"
  }

  depends_on = [var.vpc_id]
}


# TODO: Clean up ECS task definition
resource "aws_ecs_task_definition" "ecs_api_task_definition" {
  container_definitions = jsonencode([
    {
      name   = "${var.ecs_api_task_name}",
      image  = aws_ecr_repository.api_repository.repository_url,
      cpu    = var.api_cpu_units,
      memory = var.api_memory_size,
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
          awslogs-group         = "/ecs/${var.ecs_api_task_name}",
          awslogs-create-group  = "true",
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "${var.ecs_api_task_name}"
        }
      },
      systemControls = []
    }
  ])
  family             = var.ecs_api_task_name
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  execution_role_arn = aws_iam_role.ecs_api_task_execution_role.arn
  network_mode       = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  cpu    = var.api_cpu_units
  memory = var.api_memory_size

  tags = {
    Name = "valhub-ecs-api-task-definition"
  }
}
