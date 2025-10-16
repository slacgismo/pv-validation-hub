# Terraform

This document will cover information regarding the terraform script and useful commands to make changes to the system on AWS.

## Outline

The main entrypoint to the terraform script is through the [main.tf](main.tf) file in the terraform directory. Each module is defined in its own subdirectory, with its own `main.tf` file which is responsible for the resources and configurations specific to that module. There are also `variables.tf` files in each module to define the input variables for that module. These variables can be used to customize the behavior of the module without modifying the module's code. When using this terraform script you should ensure that you are passing the correct variables for your environment.

The list of modules includes:

- VPC
- S3
- RDS
- CloudFront
- Autoscaling Group
- IAM
- SQS

### AWS Access

AWS credentials will need to be passed into every Terraform command. This can be done making sure that the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` are all present within the `credentials` file within the `.aws` directory on your machine. The `profile` section of the `credentials` file should also be the same profile that you are using in your Terraform tfvars configuration under the `aws_profile` variable.

### AWS S3 bucket for Terraform state

The Terraform state is stored in an S3 bucket. This allows for remote state management and collaboration between team members to pull down and update the same state file asynchronously.

### tfvars files

Each environment (staging, production, etc.) should have its own `.tfvars` file to define the specific variables for that environment. For example, you might have a `staging.tfvars` file for staging settings and a `production.tfvars` file for production settings. Running `terraform apply -var-file=staging.tfvars` will use the variables defined in that file. The Terraform script will create or update only one instance of each resource within the state file and will not create a new set of resources. There is an [example.tfvars](example.tfvars) file included for reference with all the required variables that need to be set.

### Terraform commands

Here are some common Terraform commands you'll use:

Each command should be run from the root of the Terraform configuration directory, and you should specify the appropriate `.tfvars` file for your environment.

- `terraform init -var-file=<path to tfvars file>`: Initialize a Terraform working directory.
- `terraform plan -var-file=<path to tfvars file>`: Create an execution plan, showing what actions Terraform will take.
- `terraform apply -var-file=<path to tfvars file>`: Apply the changes required to reach the desired state of the configuration.
- `terraform destroy -var-file=<path to tfvars file>`: Destroy the Terraform-managed infrastructure.

If you wish to track manually created resources, you can import them into this Terraform state using the `terraform import` command and associating them with a new corresponding resource block that will need to be created inside one of the modules. This allows Terraform to manage these resources alongside those created by the rest of the Terraform script.

### Terraform Version

The terraform version that is being used is the latest stable version which is `~> 5.0`. When looking up documentation, make sure to reference the correct version to avoid any compatibility issues.

Here is the link to the AWS provider documentation for Terraform 5:
<https://registry.terraform.io/providers/hashicorp/aws/5.100.0/docs>
