# CI/CD Pipeline Setup Guide

This guide will walk you through setting up the complete CI/CD pipeline for the LLM application.

## Architecture Overview

```
Developer Push → GitHub → CI Tests → Build Docker → Deploy to AWS ECS
```

**What happens:**
1. You push code to GitHub
2. GitHub Actions runs tests automatically (CI)
3. If tests pass on `main` branch, it builds a Docker image
4. The image is pushed to AWS ECR (Container Registry)
5. AWS ECS automatically deploys the new version (CD)

---

## Prerequisites

- GitHub account with this repository
- AWS account
- OpenAI API key

---

## Part 1: AWS Setup

### 1.1 Create an IAM User for GitHub Actions

1. Go to AWS Console → IAM → Users → Create User
2. User name: `github-actions-user`
3. Attach policies:
   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `IAMReadOnlyAccess`
4. Create access key → Select "Third-party service"
5. **Save the Access Key ID and Secret Access Key** (you'll need these for GitHub)

### 1.2 Create ECR Repository

```bash
aws ecr create-repository \
    --repository-name llm-app \
    --region us-east-1
```

**What this does:** Creates a private Docker registry to store your container images.

**Save the repository URI** (looks like: `123456789.dkr.ecr.us-east-1.amazonaws.com/llm-app`)

### 1.3 Store OpenAI API Key in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
    --name llm-app/openai-key \
    --secret-string "your-openai-api-key-here" \
    --region us-east-1
```

**What this does:** Securely stores your OpenAI API key. ECS will inject it as an environment variable.

**Save the secret ARN** (looks like: `arn:aws:secretsmanager:us-east-1:123456789:secret:llm-app/openai-key-xxxxx`)

### 1.4 Create ECS Cluster

```bash
aws ecs create-cluster \
    --cluster-name llm-app-cluster \
    --region us-east-1
```

**What this does:** Creates a logical grouping for your containers.

### 1.5 Create IAM Roles

**ECS Task Execution Role** (allows ECS to pull images and get secrets):

```bash
# Create trust policy file
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://trust-policy.json

# Attach AWS managed policy
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Add Secrets Manager permissions
cat > secrets-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:llm-app/openai-key*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-name SecretsManagerPolicy \
    --policy-document file://secrets-policy.json
```

**ECS Task Role** (allows your application to access AWS services):

```bash
# Create the role
aws iam create-role \
    --role-name ecsTaskRole \
    --assume-role-policy-document file://trust-policy.json
```

**Get your AWS Account ID:**
```bash
aws sts get-caller-identity --query Account --output text
```

### 1.6 Update Task Definition

Edit [.aws/task-definition.json](.aws/task-definition.json) and replace:
- `YOUR_ACCOUNT_ID` with your AWS account ID (in 3 places)
- Update the secret ARN with the one you saved earlier

### 1.7 Create CloudWatch Log Group

```bash
aws logs create-log-group \
    --log-group-name /ecs/llm-app \
    --region us-east-1
```

### 1.8 Create VPC Resources (if you don't have a default VPC)

Most AWS accounts have a default VPC. Check with:
```bash
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true"
```

If you need to create one, follow AWS VPC setup documentation.

### 1.9 Create ECS Service

First, you need to create an Application Load Balancer (optional but recommended):

```bash
# Get your default VPC ID
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)

# Get subnets
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')

# Create security group
SG_ID=$(aws ec2 create-security-group \
    --group-name llm-app-sg \
    --description "Security group for LLM app" \
    --vpc-id $VPC_ID \
    --output text)

# Allow inbound traffic on port 5000
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0
```

**Create the ECS Service:**

```bash
aws ecs create-service \
    --cluster llm-app-cluster \
    --service-name llm-app-service \
    --task-definition llm-app-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
    --region us-east-1
```

**What this does:** Creates a service that ensures 1 instance of your app is always running.

---

## Part 2: GitHub Setup

### 2.1 Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

1. **AWS_ACCESS_KEY_ID**: The access key from Step 1.1
2. **AWS_SECRET_ACCESS_KEY**: The secret key from Step 1.1
3. **OPENAI_API_KEY**: Your OpenAI API key

### 2.2 Push Your Code

```bash
git add .
git commit -m "Add CI/CD pipeline configuration"
git push origin main
```

**What happens next:**
1. GitHub Actions will run the CI pipeline (see Actions tab)
2. If tests pass, it will trigger the deployment pipeline
3. Your app will be deployed to AWS ECS

---

## Part 3: Testing Your Deployment

### 3.1 Find Your App's Public IP

```bash
# Get the task ARN
TASK_ARN=$(aws ecs list-tasks \
    --cluster llm-app-cluster \
    --service-name llm-app-service \
    --query 'taskArns[0]' \
    --output text)

# Get the ENI ID
ENI_ID=$(aws ecs describe-tasks \
    --cluster llm-app-cluster \
    --tasks $TASK_ARN \
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
    --output text)

# Get the public IP
PUBLIC_IP=$(aws ec2 describe-network-interfaces \
    --network-interface-ids $ENI_ID \
    --query 'NetworkInterfaces[0].Association.PublicIp' \
    --output text)

echo "Your app is running at: http://$PUBLIC_IP:5000"
```

### 3.2 Test the Application

```bash
# Health check
curl http://$PUBLIC_IP:5000/health

# Test chat endpoint
curl -X POST http://$PUBLIC_IP:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

Or open in browser: `http://$PUBLIC_IP:5000`

---

## Part 4: Understanding the CI/CD Flow

### When you push code to GitHub:

1. **CI Pipeline** ([.github/workflows/ci.yml](.github/workflows/ci.yml)):
   - Checks out code
   - Sets up Python
   - Installs dependencies
   - Runs tests
   - Builds Docker image

2. **CD Pipeline** ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)) - only on main branch:
   - Waits for CI to succeed
   - Authenticates with AWS
   - Builds and pushes Docker image to ECR
   - Updates ECS task definition
   - Deploys to ECS (zero-downtime deployment)

---

## Cost Considerations

**Estimated monthly costs (running 24/7):**
- ECS Fargate (0.25 vCPU, 0.5GB): ~$15/month
- Application Load Balancer (optional): ~$16/month
- Data transfer: Minimal for testing
- **Total: ~$15-31/month**

**To minimize costs:**
- Stop the ECS service when not in use:
  ```bash
  aws ecs update-service \
      --cluster llm-app-cluster \
      --service llm-app-service \
      --desired-count 0
  ```
- Restart when needed:
  ```bash
  aws ecs update-service \
      --cluster llm-app-cluster \
      --service llm-app-service \
      --desired-count 1
  ```

---

## Troubleshooting

### Check GitHub Actions logs:
- Go to your repo → Actions tab → Click on the workflow run

### Check ECS logs:
```bash
aws logs tail /ecs/llm-app --follow
```

### Check ECS service status:
```bash
aws ecs describe-services \
    --cluster llm-app-cluster \
    --services llm-app-service
```

### Common issues:

1. **Task keeps stopping**: Check CloudWatch logs for errors
2. **Can't pull image**: Verify ECR permissions in task execution role
3. **Can't get secrets**: Verify Secrets Manager permissions
4. **Deployment fails**: Check that task definition ARNs are correct

---

## Next Steps

1. **Add a Load Balancer**: For a production domain name and HTTPS
2. **Set up Auto Scaling**: Scale based on CPU/memory usage
3. **Add monitoring**: Set up CloudWatch alarms
4. **Add staging environment**: Create a develop branch workflow
5. **Implement blue/green deployments**: For even safer deployments

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
