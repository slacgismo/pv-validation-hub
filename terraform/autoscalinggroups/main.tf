locals {
  ecs_worker_task_name = "valhub-worker-task"
  ecs_api_task_name    = "valhub-api-task"
}

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
  name                = "valhub-worker-asg"
  desired_capacity    = var.asg_desired_capacity
  max_size            = var.asg_max_size
  min_size            = var.asg_min_size
  vpc_zone_identifier = var.private_subnet_ids

  launch_template {
    id      = aws_launch_template.worker_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "valhub-worker-asg"
    propagate_at_launch = true
  }

}

resource "aws_ecs_capacity_provider" "worker_capacity_provider" {
  name = "valhub-worker-capacity-provider"

  auto_scaling_group_provider {

    auto_scaling_group_arn = aws_autoscaling_group.worker_asg.arn
    # managed_termination_protection = "ENABLED"
    managed_draining               = "ENABLED"
    managed_termination_protection = "DISABLED"

    managed_scaling {
      status                    = "ENABLED"
      target_capacity           = 100
      minimum_scaling_step_size = 1
      maximum_scaling_step_size = 10000
    }

  }

  tags = {
    Name = "valhub-worker-capacity-provider"
  }
}


data "aws_iam_policy_document" "ecs_instance_assume_role_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com", "ecs.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy_attachment" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role" "ecs_instance_role" {
  name = "valhub-ecs-instance-role"

  assume_role_policy = data.aws_iam_policy_document.ecs_instance_assume_role_policy.json

  tags = {
    Name = "valhub-ecs-instance-role"
  }
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "valhub-ecs-instance-profile"

  role = aws_iam_role.ecs_instance_role.id

  tags = {
    Name = "valhub-ecs-instance-profile"
  }
}



resource "aws_launch_template" "worker_lt" {
  name_prefix   = "valhub-worker-lt-"
  image_id      = data.aws_ami.worker_ami.id
  instance_type = var.worker_instance_type

  iam_instance_profile {
    arn = aws_iam_instance_profile.ecs_instance_profile.arn
  }

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size = var.worker_volume_size
      encrypted   = true

    }
  }

  metadata_options {
    http_tokens = "required"
  }

  lifecycle {
    create_before_destroy = true
  }


  network_interfaces {
    security_groups = [var.ecs_worker_sg_id]
    # subnet_id                   = var.private_subnet_ids[0] # Use the first private subnet
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    ecs_cluster_name = aws_ecs_cluster.worker_cluster.name
  }))

  tags = {
    Name = "valhub-worker-launch-template"
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

  image_tag_mutability = "MUTABLE"

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
  image_tag_mutability = "MUTABLE"

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

  force_new_deployment = true

  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }
  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.ecs_worker_sg_id]
  }
  scheduling_strategy = "REPLICA"

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    create_before_destroy = false
  }

  tags = {
    Name = "valhub-ecs-worker-service"
  }


}

data "aws_iam_policy_document" "ecs_worker_task_assume_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com", "secretsmanager.amazonaws.com", "sqs.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}

data "aws_iam_policy_document" "ecs_worker_task_role_permissions_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:*",
      "sqs:*"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy_attachment" "ecs_worker_task_role_policy_attachment" {
  name       = "valhub-ecs-worker-task-role-policy-attachment"
  roles      = [aws_iam_role.ecs_worker_task_role.name]
  policy_arn = aws_iam_policy.ecs_worker_task_role_policy.arn
}

resource "aws_iam_policy" "ecs_worker_task_role_policy" {
  name        = "valhub-ecs-worker-task-role-policy"
  description = "Policy for ECS worker task role to allow access to Secrets Manager and S3"
  policy      = data.aws_iam_policy_document.ecs_worker_task_role_permissions_policy_document.json

  tags = {
    Name = "valhub-ecs-worker-task-role-policy"
  }
}

resource "aws_iam_role" "ecs_worker_task_role" {
  name               = "valhub-ecs-worker-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_worker_task_assume_role_policy_document.json
  tags = {
    Name = "valhub-ecs-worker-task-role"
  }
}


data "aws_iam_policy_document" "ecs_api_task_assume_role_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com", "secretsmanager.amazonaws.com", "sqs.amazonaws.com", "rds.amazonaws.com", "cloudwatch.amazonaws.com", "logs.amazonaws.com", "kms.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}

data "aws_iam_policy_document" "ecs_api_task_role_permissions_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:*",
      "sqs:*",
      "rds:*",
      "s3:*",
      "cloudwatch:*",
      "logs:*",
      "kms:*"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy_attachment" "ecs_api_task_role_policy_attachment" {
  name       = "valhub-ecs-api-task-role-policy-attachment"
  roles      = [aws_iam_role.ecs_api_task_role.name]
  policy_arn = aws_iam_policy.ecs_api_task_role_policy.arn
}

resource "aws_iam_policy" "ecs_api_task_role_policy" {
  name        = "valhub-ecs-api-task-role-policy"
  description = "Policy for ECS API task role to allow access to Secrets Manager and S3"
  policy      = data.aws_iam_policy_document.ecs_api_task_role_permissions_policy_document.json

  tags = {
    Name = "valhub-ecs-api-task-role-policy"
  }
}

resource "aws_iam_role" "ecs_api_task_role" {
  name               = "valhub-ecs-api-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_api_task_assume_role_policy_document.json

  tags = {
    Name = "valhub-ecs-api-task-role"
  }

}




data "aws_iam_policy_document" "ecs_task_execution_assume_role_policy_document" {
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


resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "valhub-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume_role_policy_document.json

  tags = {
    Name = "valhub-ecs-task-execution-role"
  }
}


resource "aws_ecs_task_definition" "ecs_worker_task_definition" {

  container_definitions = jsonencode([
    {
      name              = local.ecs_worker_task_name,
      image             = aws_ecr_repository.worker_repository.repository_url,
      cpu               = var.worker_cpu_units,
      memory            = var.worker_memory_size,
      memoryReservation = var.worker_memory_reservation_size,
      portMappings = [
        {
          containerPort = 80,
          hostPort      = 80,
          protocol      = "tcp",
          name          = "${local.ecs_worker_task_name}-80-tcp"
        },
        {
          containerPort = 443,
          hostPort      = 443,
          protocol      = "tcp",
          name          = "${local.ecs_worker_task_name}-443-tcp"
        },
        {
          containerPort = 22,
          hostPort      = 22,
          protocol      = "tcp",
          name          = "${local.ecs_worker_task_name}-22-tcp"
        },
        {
          containerPort = 65535,
          hostPort      = 65535,
          protocol      = "tcp",
          name          = "${local.ecs_worker_task_name}-65535-tcp"
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
          awslogs-group         = "/ecs/${local.ecs_worker_task_name}",
          awslogs-create-group  = "true",
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "${local.ecs_worker_task_name}"
        }
      },
      systemControls = []
    }
  ])

  family             = local.ecs_worker_task_name
  task_role_arn      = aws_iam_role.ecs_worker_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
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

  force_new_deployment = true

  # load_balancer {
  #   target_group_arn = var.api_target_group_http_arn
  #   container_name   = local.ecs_api_task_name
  #   container_port   = 80
  # }
  load_balancer {
    target_group_arn = var.api_target_group_https_arn
    container_name   = local.ecs_api_task_name
    container_port   = 443
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

}


# TODO: Clean up ECS task definition
resource "aws_ecs_task_definition" "ecs_api_task_definition" {
  container_definitions = jsonencode([
    {
      name   = local.ecs_api_task_name,
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
          awslogs-group         = "/ecs/${local.ecs_api_task_name}",
          awslogs-create-group  = "true",
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "${local.ecs_api_task_name}"
        }
      },
      systemControls = []
    }
  ])
  family             = local.ecs_api_task_name
  task_role_arn      = aws_iam_role.ecs_api_task_role.arn
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
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

resource "aws_secretsmanager_secret" "valhub_api_django_secret_key" {
  name        = "valhub-api-django-secret-key"
  description = "Secret for Valhub API Django"
}

resource "aws_secretsmanager_secret_version" "valhub_api_django_secret_key" {
  secret_id     = aws_secretsmanager_secret.valhub_api_django_secret_key.id
  secret_string = jsonencode(var.valhub_api_django_secret_key)
}

resource "aws_secretsmanager_secret" "valhub_worker_credentials" {
  name        = "valhub-worker-credentials"
  description = "Secret for Valhub Worker credentials"

}

resource "aws_secretsmanager_secret_version" "valhub_worker_credentials" {
  secret_id     = aws_secretsmanager_secret.valhub_worker_credentials.id
  secret_string = jsonencode(var.valhub_worker_credentials)
}

resource "aws_cloudwatch_log_group" "ecs_worker_log_group" {
  name              = "/ecs/${local.ecs_worker_task_name}"
  retention_in_days = 7

  tags = {
    Name = "valhub-ecs-worker-log-group"
  }

}

resource "aws_cloudwatch_log_group" "ecs_api_log_group" {
  name              = "/ecs/${local.ecs_api_task_name}"
  retention_in_days = 7

  tags = {
    Name = "valhub-ecs-api-log-group"
  }

}
