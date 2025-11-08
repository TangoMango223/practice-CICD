# Terraform outputs

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.llm_app.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.llm_app.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.llm_app.name
}

output "github_actions_user" {
  description = "IAM user for GitHub Actions"
  value       = aws_iam_user.github_actions.name
}

output "github_actions_access_key_id" {
  description = "Access key ID for GitHub Actions (save this!)"
  value       = aws_iam_access_key.github_actions.id
  sensitive   = true
}

output "github_actions_secret_access_key" {
  description = "Secret access key for GitHub Actions (save this!)"
  value       = aws_iam_access_key.github_actions.secret
  sensitive   = true
}

output "security_group_id" {
  description = "Security group ID for the ECS tasks"
  value       = aws_security_group.llm_app.id
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.llm_app.name
}
