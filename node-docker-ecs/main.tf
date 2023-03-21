provider "aws" {
  version = "~> 2.0"
  region  = "us-east-2"
}

locals {
  vpc_id = "vpc-a27c77ca"
  # refers to pv-validation-kubernetes subnet
  subnet_id_1 = "subnet-01920f4e2aeb35b55"
  subnet_id_2 = "subnet-03602b3cf6a313769"
  ecs_task_execution_role_arn = "arn:aws:iam::041414866712:role/ecsTaskExecutionRole"
  ecs_task_execution_role_name = "ecsTaskExecutionRole"
}

# # Providing a reference to our default VPC
# resource "aws_default_vpc" "default_vpc" {
# }

# Providing a reference to our default subnets
# resource "aws_default_subnet" "default_subnet_a" {
#   availability_zone = "us-east-2a"
# }

# resource "aws_default_subnet" "default_subnet_b" {
#   availability_zone = "us-east-2b"
# }

# resource "aws_default_subnet" "default_subnet_c" {
#   availability_zone = "us-east-2c"
# }

# resource "aws_ecr_repository" "pv-validation-hub-test-ecr-repo" {
#   name = "pv-validation-hub"
# }

resource "aws_ecs_cluster" "pv-validation-hub-test-cluster" {
  name = "pv-validation-hub-test-cluster" # Naming the cluster
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
      "cpu": 256
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"] # Stating that we are using ECS Fargate
  network_mode             = "awsvpc"    # Using awsvpc as our network mode as this is required for Fargate
  memory                   = 512         # Specifying the memory our container requires
  cpu                      = 256         # Specifying the CPU our container requires
  execution_role_arn       = local.ecs_task_execution_role_arn
}

# resource "aws_iam_role" "ecsTaskExecutionRole" {
#   name               = "ecsTaskExecutionRole"
#   assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
# }

# data "aws_iam_policy_document" "assume_role_policy" {
#   statement {
#     actions = ["sts:AssumeRole"]

#     principals {
#       type        = "Service"
#       identifiers = ["ecs-tasks.amazonaws.com"]
#     }
#   }
# }

# resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
#   role       = local.ecs_task_execution_role_name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
# }

resource "aws_alb" "application_load_balancer" {
  name               = "pv-validation-hub-test-lb-tf" # Naming our load balancer
  load_balancer_type = "application"
  subnets = [ # Referencing the default subnets
    local.subnet_id_1,
    local.subnet_id_2
  ]
  # Referencing the security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

# Creating a security group for the load balancer:
resource "aws_security_group" "load_balancer_security_group" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allowing traffic in from all sources
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb_target_group" "target_group" {
  name        = "target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = local.vpc_id # Referencing the default VPC
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = "${aws_alb.application_load_balancer.arn}" # Referencing our load balancer
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our target group
  }
}

resource "aws_ecs_service" "my_first_service" {
  name            = "my-first-service"                             # Naming our first service
  cluster         = "${aws_ecs_cluster.pv-validation-hub-test-cluster.id}"             # Referencing our created Cluster
  task_definition = "${aws_ecs_task_definition.pv-validation-hub-test-task.arn}" # Referencing the task our service will spin up
  launch_type     = "FARGATE"
  desired_count   = 3 # Setting the number of containers to 3

  load_balancer {
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our target group
    container_name   = "${aws_ecs_task_definition.pv-validation-hub-test-task.family}"
    container_port   = 3000 # Specifying the container port
  }

  network_configuration {
    subnets          = [local.subnet_id_1, local.subnet_id_2]
    assign_public_ip = true                                                # Providing our containers with public IPs
    security_groups  = ["${aws_security_group.service_security_group.id}"] # Setting the security group
  }
}


resource "aws_security_group" "service_security_group" {
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    # Only allowing traffic in from the load balancer security group
    security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
