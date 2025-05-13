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

# resource "aws_ecs_cluster" "worker_cluster" {
#   name = "pv-validation-hub-worker-cluster"
# }

resource "aws_ecs_cluster" "worker_cluster_prod" {
  name = "pv-validation-hub-worker-cluster-prod"
}

resource "aws_ecs_cluster" "api_cluster" {
  name = "pv-validation-hub-api-cluster"
}

resource "aws_ecr_repository" "api_repository" {
  name = "pv-validation-hub-api"
}

resource "aws_ecr_repository" "worker_repository" {
  name = "pv-validation-hub-worker"
}

# TODO: Clean up ECS service
resource "aws_ecs_service" "ECSService" {
  name                               = "worker-service"
  cluster                            = "arn:aws:ecs:us-west-2:041414866712:cluster/pv-validation-hub-worker-cluster-prod"
  desired_count                      = 1
  task_definition                    = aws_ecs_task_definition.ECSTaskDefinition.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  iam_role                           = "arn:aws:iam::041414866712:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS"
  ordered_placement_strategy {
    type  = "spread"
    field = "attribute:ecs.availability-zone"
  }
  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }
  network_configuration {
    assign_public_ip = "DISABLED"
    security_groups = [
      "sg-0ec6afe88decf3d1a"
    ]
    subnets = [
      "subnet-0767b7cb80009dfe8",
      "subnet-0d8bbfb46646711d2"
    ]
  }
  scheduling_strategy = "REPLICA"
}

# TODO: Clean up ECS task definition
resource "aws_ecs_task_definition" "ECSTaskDefinition" {
  container_definitions = "[{\"name\":\"pv-validation-hub-worker-task-ec2\",\"image\":\"041414866712.dkr.ecr.us-west-2.amazonaws.com/pv-validation-hub-worker:latest\",\"cpu\":4096,\"memory\":12288,\"memoryReservation\":12288,\"portMappings\":[{\"containerPort\":80,\"hostPort\":80,\"protocol\":\"tcp\",\"name\":\"pv-validation-hub-worker-task-ec2-80-tcp\"},{\"containerPort\":443,\"hostPort\":443,\"protocol\":\"tcp\",\"name\":\"pv-validation-hub-worker-task-ec2-443-tcp\"},{\"containerPort\":22,\"hostPort\":22,\"protocol\":\"tcp\",\"name\":\"pv-validation-hub-worker-task-22-ec2-tcp\"},{\"containerPort\":65535,\"hostPort\":65535,\"protocol\":\"tcp\",\"name\":\"pv-validation-hub-worker-task-ec2-65535-tcp\"}],\"essential\":true,\"environment\":[],\"mountPoints\":[{\"sourceVolume\":\"docker_in_docker\",\"containerPath\":\"/var/run/docker.sock\"},{\"sourceVolume\":\"current_evaluation\",\"containerPath\":\"/root/worker/current_evaluation\",\"readOnly\":false}],\"volumesFrom\":[],\"logConfiguration\":{\"logDriver\":\"awslogs\",\"options\":{\"awslogs-group\":\"/ecs/pv-validation-hub-worker-task-ec2\",\"awslogs-create-group\":\"true\",\"awslogs-region\":\"us-west-2\",\"awslogs-stream-prefix\":\"pv-validation-hub-worker-task-ec2\"}},\"systemControls\":[]}]"
  family                = "pv-validation-hub-worker-task-ec2"
  task_role_arn         = "arn:aws:iam::041414866712:role/valhub-ecs-task-role"
  execution_role_arn    = "arn:aws:iam::041414866712:role/valhub_worker_ecs_task_execution_role"
  network_mode          = "awsvpc"
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
}

# TODO: Clean up ECS service
resource "aws_ecs_service" "ECSService2" {
  name    = "ecs-api-service"
  cluster = "arn:aws:ecs:us-west-2:041414866712:cluster/pv-validation-hub-api-cluster"
  load_balancer {
    target_group_arn = "arn:aws:elasticloadbalancing:us-west-2:041414866712:targetgroup/valhub-api-target-group/f3f1612b69db93c6"
    container_name   = "pv-validation-hub-api-task"
    container_port   = 80
  }
  desired_count                      = 1
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  task_definition                    = aws_ecs_task_definition.ECSTaskDefinition2.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  iam_role                           = "arn:aws:iam::041414866712:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS"
  network_configuration {
    assign_public_ip = "ENABLED"
    security_groups = [
      "sg-08f04514e1770cd92"
    ]
    subnets = [
      "subnet-0de884df2b205823d",
      "subnet-0e882e68ceca68715"
    ]
  }
  health_check_grace_period_seconds = 120
  scheduling_strategy               = "REPLICA"
}


# TODO: Clean up ECS task definition
resource "aws_ecs_task_definition" "ECSTaskDefinition2" {
  container_definitions = "[{\"name\":\"pv-validation-hub-api-task\",\"image\":\"041414866712.dkr.ecr.us-west-2.amazonaws.com/pv-validation-hub-api:latest\",\"cpu\":1024,\"memory\":2048,\"portMappings\":[{\"containerPort\":80,\"hostPort\":80,\"protocol\":\"tcp\"},{\"containerPort\":443,\"hostPort\":443,\"protocol\":\"tcp\"},{\"containerPort\":22,\"hostPort\":22,\"protocol\":\"tcp\"}],\"essential\":true,\"environment\":[],\"mountPoints\":[],\"volumesFrom\":[],\"logConfiguration\":{\"logDriver\":\"awslogs\",\"options\":{\"awslogs-group\":\"/ecs/pv-validation-hub-api-task\",\"awslogs-create-group\":\"true\",\"awslogs-region\":\"us-west-2\",\"awslogs-stream-prefix\":\"pv-validation-hub-api-task\"}},\"systemControls\":[]}]"
  family                = "pv-validation-hub-api-task"
  task_role_arn         = "arn:aws:iam::041414866712:role/valhub-ecs-task-role"
  execution_role_arn    = "arn:aws:iam::041414866712:role/valhub_ecs_task_execution_role"
  network_mode          = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  cpu    = "1024"
  memory = "2048"
}
