# Quick Start Guide

## What You Have Now

A complete CI/CD pipeline project with:
- ✅ Flask LLM chat application
- ✅ Automated testing
- ✅ Docker containerization
- ✅ GitHub Actions workflows
- ✅ AWS deployment configuration

## Next Steps (Choose Your Path)

### Option A: Test Locally First (Recommended for Learning)

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```

5. **Test it:** Open http://localhost:5000 in your browser

6. **Run tests:**
   ```bash
   pytest test_app.py -v
   ```

### Option B: Test with Docker

1. **Build the image:**
   ```bash
   docker build -t llm-app .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 -e OPENAI_API_KEY="sk-your-key-here" llm-app
   ```

3. **Test it:** Open http://localhost:5000

### Option C: Deploy to AWS (Full CI/CD Pipeline)

This is the main goal! Follow [SETUP.md](SETUP.md) which walks you through:

**Phase 1: AWS Setup** (~30-45 minutes)
- Create IAM user for GitHub Actions
- Set up ECR (container registry)
- Store OpenAI key in Secrets Manager
- Create ECS cluster and service
- Set up IAM roles

**Phase 2: GitHub Setup** (~5 minutes)
- Add AWS credentials as GitHub secrets
- Push code to trigger CI/CD

**Phase 3: Verify Deployment** (~5 minutes)
- Check GitHub Actions logs
- Find your app's public IP
- Test the live application

## Understanding the Flow

```
┌─────────────────┐
│  You Edit Code  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Git Push       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  GitHub Actions (CI)    │
│  - Run tests            │
│  - Build Docker image   │
└────────┬────────────────┘
         │
         ▼ (only if tests pass)
┌─────────────────────────┐
│  GitHub Actions (CD)    │
│  - Push to ECR          │
│  - Deploy to ECS        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Live on AWS! 🚀        │
│  http://your-ip:5000    │
└─────────────────────────┘
```

## Key Concepts to Understand

### 1. Continuous Integration (CI)
Every time you push code, GitHub automatically:
- Checks out your code
- Sets up Python
- Installs dependencies
- Runs tests
- Builds Docker image

**Why?** Catches bugs early, before they reach production.

### 2. Continuous Deployment (CD)
When tests pass on the `main` branch:
- Builds production Docker image
- Pushes to AWS ECR (your private registry)
- Updates ECS task definition
- Deploys new version (AWS handles rolling update)

**Why?** Get changes to production quickly and safely.

### 3. Docker
Packages your app + all dependencies into a container:
- Same environment everywhere (dev, test, prod)
- Easy to deploy
- Isolated from other apps

### 4. AWS ECS + Fargate
- **ECS**: Orchestrates running your containers
- **Fargate**: Serverless - no servers to manage
- **ECR**: Stores your Docker images
- **Secrets Manager**: Securely stores API keys

## Tips for Learning

1. **Start local:** Test the app on your machine first
2. **Read the logs:** GitHub Actions logs show every step
3. **Experiment:** Try making a change and pushing to see CI/CD in action
4. **Monitor costs:** Check AWS billing dashboard regularly

## Common Commands

```bash
# Local development
python app.py

# Run tests
pytest test_app.py -v

# Build Docker
docker build -t llm-app .

# Stop ECS service (save money)
aws ecs update-service --cluster llm-app-cluster --service llm-app-service --desired-count 0

# Start ECS service
aws ecs update-service --cluster llm-app-cluster --service llm-app-service --desired-count 1

# View logs
aws logs tail /ecs/llm-app --follow

# Check service status
aws ecs describe-services --cluster llm-app-cluster --services llm-app-service
```

## Files to Know

| File | Purpose |
|------|---------|
| [app.py](app.py) | Main Flask application |
| [test_app.py](test_app.py) | Tests for the app |
| [requirements.txt](requirements.txt) | Python dependencies |
| [Dockerfile](Dockerfile) | How to build the container |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | CI pipeline definition |
| [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | CD pipeline definition |
| [.aws/task-definition.json](.aws/task-definition.json) | ECS task configuration |

## Getting Help

- **GitHub Actions failing?** Check the Actions tab in GitHub
- **App not working locally?** Check you set OPENAI_API_KEY
- **AWS deployment issues?** Check CloudWatch logs: `aws logs tail /ecs/llm-app --follow`
- **Need detailed AWS setup?** See [SETUP.md](SETUP.md)

## What to Try Next

After getting it working:

1. **Make a change:** Edit the welcome message in [templates/index.html](templates/index.html)
2. **Push it:** `git add . && git commit -m "Update welcome" && git push`
3. **Watch the magic:** See CI run → CD deploy → Live on AWS
4. **Add features:**
   - Chat history
   - Different AI models
   - User authentication
   - Custom system prompts

Have fun learning CI/CD! 🚀