# Things to take note of

- EC2 that is provisioned needs to have more memory then the task definition within the ECS service
  - EC2 4vCPU 16GB
  - EC2 Task Definition in ECS 4vCPU 12GB
    - Need to check how small the difference can be
- EC2 Needs to have a public IPV4 Address
