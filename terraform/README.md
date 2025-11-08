# Terraform AWS Infrastructure Setup

This Terraform configuration creates all the AWS infrastructure needed for deploying the LLM chat application.

## What Gets Created

- **ECR Repository** - Stores Docker images
- **ECS Cluster** - Runs containers
- **ECS Service** - Manages container instances
- **IAM Roles** - Permissions for ECS tasks
- **Security Group** - Network access control
- **CloudWatch Logs** - Application logging
- **Secrets Manager** - Stores OpenAI API key
- **IAM User** - For GitHub Actions deployment

## Prerequisites

### 1. Install Terraform

```bash
# macOS
brew install terraform

# Or download from: https://www.terraform.io/downloads
```

### 2. Configure AWS Credentials

**Option A: AWS CLI (Recommended)**
```bash
# Install AWS CLI
brew install awscli

# Configure credentials
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: ca-central-1
# - Output format: json
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ca-central-1"
```

**Where to get AWS credentials:**
1. AWS Console → IAM → Users → Your user
2. Security credentials tab
3. Create access key
4. Save both keys securely

### 3. Create terraform.tfvars

```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

Add your OpenAI API key:
```hcl
openai_api_key = "sk-proj-your-actual-key-here"
```

## Usage

### Initialize Terraform

```bash
cd terraform/
terraform init
```

This downloads required providers and sets up the backend.

### Plan the Changes

```bash
terraform plan
```

This shows what will be created without actually creating it.

### Apply the Configuration

```bash
terraform apply
```

Type `yes` when prompted. This creates all AWS resources (~5 minutes).

### View Outputs

```bash
terraform output
```

**Important outputs:**
- `ecr_repository_url` - Where to push Docker images
- `github_actions_access_key_id` - For GitHub Secrets
- `github_actions_secret_access_key` - For GitHub Secrets

**To see sensitive outputs:**
```bash
terraform output github_actions_access_key_id
terraform output github_actions_secret_access_key
```

**Save these for GitHub Secrets setup!**

## After Terraform Apply

### 1. Add GitHub Secrets

Go to: **GitHub repo → Settings → Secrets and variables → Actions**

Add these secrets:
- `AWS_ACCESS_KEY_ID`: From terraform output
- `AWS_SECRET_ACCESS_KEY`: From terraform output
- `OPENAI_API_KEY`: Your OpenAI API key

### 2. Update deploy.yml (if needed)

The workflow should already match, but verify:
```yaml
env:
  AWS_REGION: ca-central-1  # ← Should match your region
```

### 3. Push Initial Docker Image

Before the service can start, you need an image in ECR:

```bash
# Get ECR login
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url | cut -d/ -f1)

# Build and tag
docker build -t llm-app .
docker tag llm-app:latest $(terraform output -raw ecr_repository_url):latest

# Push
docker push $(terraform output -raw ecr_repository_url):latest
```

### 4. Verify Deployment

```bash
# Check ECS service
aws ecs describe-services --cluster llm-app-cluster --services llm-app-service --region ca-central-1

# Get task public IP
aws ecs list-tasks --cluster llm-app-cluster --region ca-central-1
# Use task ARN from above
aws ecs describe-tasks --cluster llm-app-cluster --tasks <task-arn> --region ca-central-1
```

## Managing Resources

### View Current State

```bash
terraform show
```

### Update Resources

Edit `.tf` files, then:
```bash
terraform plan
terraform apply
```

### Destroy Everything

**⚠️ This deletes all AWS resources!**

```bash
terraform destroy
```

Type `yes` to confirm.

## Cost Estimate

Running 24/7 in ca-central-1:
- ECS Fargate (0.25 vCPU, 0.5 GB): ~$15/month
- CloudWatch Logs (7-day retention): ~$1/month
- ECR storage: <$1/month
- **Total: ~$16-17/month**

**To save money:**
```bash
# Stop the service (keeps infrastructure)
aws ecs update-service --cluster llm-app-cluster --service llm-app-service --desired-count 0 --region ca-central-1

# Restart when needed
aws ecs update-service --cluster llm-app-cluster --service llm-app-service --desired-count 1 --region ca-central-1
```

## Troubleshooting

### Terraform init fails
```bash
# Clear cache and retry
rm -rf .terraform .terraform.lock.hcl
terraform init
```

### AWS credentials error
```bash
# Verify credentials
aws sts get-caller-identity

# Should show your account info
```

### Resource already exists
```bash
# Import existing resource
terraform import aws_ecr_repository.llm_app llm-app

# Or destroy and recreate
terraform destroy
terraform apply
```

### Task won't start
```bash
# Check logs
aws logs tail /ecs/llm-app --follow --region ca-central-1

# Check service events
aws ecs describe-services --cluster llm-app-cluster --services llm-app-service --region ca-central-1 | grep -A 5 "events"
```

## File Structure

```
terraform/
├── main.tf                    # Main infrastructure
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example variables
├── terraform.tfvars           # Your variables (gitignored)
└── README.md                  # This file
```

## Security Notes

- `terraform.tfvars` is gitignored (contains secrets)
- IAM user has minimal permissions needed
- Security group only allows port 5000
- Secrets stored in AWS Secrets Manager
- Access keys shown once in outputs

## Next Steps

After everything is running:
1. Test the app via the public IP
2. Push code changes → GitHub Actions deploys automatically
3. Monitor logs in CloudWatch
4. Scale as needed: `desired_count = 2` in tfvars
