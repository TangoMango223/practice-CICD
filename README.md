# LLM Chat Application with CI/CD Pipeline

A simple Flask-based LLM chat application with a complete CI/CD pipeline deploying to AWS ECS.

## What This Project Demonstrates

- **Flask Web Application**: Simple chat interface using OpenAI's API
- **Continuous Integration**: Automated testing with GitHub Actions
- **Continuous Deployment**: Automated deployment to AWS ECS with Fargate
- **Docker Containerization**: Application packaged in a Docker container
- **Infrastructure as Code**: AWS resources defined in configuration files

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Visit:** http://localhost:5000

### Run Tests

```bash
pytest test_app.py -v
```

### Build and Run with Docker

```bash
docker build -t llm-app .
docker run -p 5000:5000 -e OPENAI_API_KEY="your-key-here" llm-app
```

## CI/CD Pipeline Setup

See [SETUP.md](SETUP.md) for complete instructions on setting up the CI/CD pipeline with AWS.

## Project Structure

```
.
├── app.py                      # Flask application
├── test_app.py                 # pytest tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── templates/
│   └── index.html             # Web interface
├── .github/workflows/
│   ├── ci.yml                 # CI pipeline (tests)
│   └── deploy.yml             # CD pipeline (AWS deployment)
├── .aws/
│   └── task-definition.json   # ECS task configuration
└── SETUP.md                   # Complete setup guide

```

## How the CI/CD Pipeline Works

### 1. Continuous Integration (CI)
When you push code:
- GitHub Actions runs tests automatically
- Builds Docker image to verify it compiles
- Fails the build if tests fail

### 2. Continuous Deployment (CD)
When tests pass on `main` branch:
- Builds production Docker image
- Pushes to AWS ECR (Container Registry)
- Updates ECS service with new version
- AWS performs zero-downtime deployment

## Technologies Used

- **Backend**: Python, Flask
- **LLM**: OpenAI GPT-3.5-turbo
- **Testing**: pytest
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Cloud Platform**: AWS (ECS, ECR, Fargate)
- **Infrastructure**: AWS Secrets Manager, CloudWatch

## Learn More

This project is designed for learning CI/CD concepts. Check out [SETUP.md](SETUP.md) for:
- Step-by-step AWS configuration
- Understanding each part of the pipeline
- Troubleshooting common issues
- Cost optimization tips
