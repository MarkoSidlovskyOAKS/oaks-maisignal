# Terraform — MAiSIGNAL Infrastructure

AWS infrastructure provisioning for MAiSIGNAL using Terraform with dev/prod workspace separation.

## Resources

| Resource | File | Purpose |
|----------|------|---------|
| **VPC** | `vpc.tf` | Private networking with NAT Gateway, flow logs |
| **ECS Fargate** | `ecs.tf` | Runs the MAiSIGNAL container on a daily schedule |
| **EventBridge** | `eventbridge.tf` | Daily cron trigger for the ECS task |
| **ECR** | `ecr.tf` | Container registry (immutable tags, scan on push) |
| **Lambda** | `lambda.tf` | Snowflake password rotation function |
| **Secrets Manager** | `secrets.tf` | App credentials with automatic rotation (30-day default) |
| **KMS** | `kms.tf` | Encryption key for secrets, logs, and SQS |
| **IAM** | `iam.tf` | Least-privilege roles for ECS, Lambda, EventBridge |
| **Security Groups** | `sg.tf` | HTTPS-only egress for ECS tasks |

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5.0
- AWS CLI configured with appropriate credentials
- S3 bucket `oaks-terraform-state` for remote state

## Usage

```bash
cd terraform

# Initialize
terraform init

# Select workspace
terraform workspace select dev   # or: terraform workspace new dev

# Preview changes
terraform plan -var-file=dev.tfvars -var container_image_tag=<sha>

# Apply
terraform apply -var-file=dev.tfvars -var container_image_tag=<sha>
```

## Workspaces

| Workspace | tfvars | Purpose |
|-----------|--------|---------|
| `dev` | `dev.tfvars` | Development environment |
| `prod` | `prod.tfvars` | Production environment |

Resources are prefixed with `maisignal-<env>` (e.g., `maisignal-dev-ecs-task`).

## State Backend

Terraform state is stored in S3:

| Setting | Value |
|---------|-------|
| Bucket | `oaks-terraform-state` |
| Key | `maisignal/terraform.tfstate` |
| Region | `eu-central-1` |

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `project` | `maisignal` | Project name for resource tagging |
| `aws_region` | `eu-central-1` | AWS region |
| `ecr_repo_name` | `maisignal` | ECR repository name |
| `vpc_cidr` | `10.0.0.0/16` | VPC CIDR block |
| `public_subnet_cidr` | `10.0.0.0/24` | Public subnet (NAT Gateway) |
| `private_subnet_cidrs` | `["10.0.1.0/24", "10.0.2.0/24"]` | Private subnets (one per AZ) |
| `ecs_task_cpu` | `256` | CPU units for Fargate task |
| `ecs_task_memory` | `512` | Memory (MiB) for Fargate task |
| `ecs_schedule_expression` | `cron(0 8 * * ? *)` | Daily schedule for alert task |
| `log_retention_days` | `365` | CloudWatch log retention |
| `container_image_tag` | *(required)* | Docker image tag (git SHA) |
| `rotation_schedule_days` | `30` | Days between Snowflake password rotations |

## Security Scanning

Terraform code is scanned by [Checkov](https://www.checkov.io/) in CI (`.github/workflows/checkov-scan.yml`). Current status: 101 passed, 0 failed.
