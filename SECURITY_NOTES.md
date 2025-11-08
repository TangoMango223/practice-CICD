# Security Notes - Files with Secrets

This document lists all files that contain sensitive information and how they're protected.

## Files with Secrets (NEVER commit these!)

### 1. `.env`
**Contains:** OpenAI API key for local development
**Protected by:** `.gitignore` (line 38, 58)
**Status:** ✅ Gitignored

### 2. `terraform/terraform.tfvars`
**Contains:**
- OpenAI API key
- Any custom AWS configuration values
**Protected by:** `.gitignore` (line 57)
**Status:** ✅ Gitignored

### 3. `terraform/.terraform/`
**Contains:** Terraform provider binaries and cached modules
**Protected by:** `.gitignore` (line 58)
**Status:** ✅ Gitignored

### 4. `terraform/*.tfstate` and `terraform/*.tfstate.backup`
**Contains:** Complete infrastructure state including sensitive outputs
**Protected by:** `.gitignore` (lines 59-60)
**Status:** ✅ Gitignored

## Safe to Commit

These files are safe to commit because they don't contain actual secrets:

- ✅ `terraform/terraform.tfvars.example` - Template only, no real values
- ✅ `terraform/main.tf` - Infrastructure definition, no secrets
- ✅ `terraform/variables.tf` - Variable definitions, no values
- ✅ `terraform/outputs.tf` - Output definitions (values are in .tfstate)
- ✅ `.github/workflows/*.yml` - Uses GitHub Secrets, not hardcoded values
- ✅ `DEPLOYMENT_STEPS.md` - Contains the credentials BUT this file should be added to .gitignore before committing!

## IMPORTANT: Before Committing

The file `DEPLOYMENT_STEPS.md` currently contains your actual AWS credentials and OpenAI key for easy reference. You have two options:

### Option 1: Remove credentials from DEPLOYMENT_STEPS.md
Edit the file and replace the actual values with placeholders:
```markdown
- **Value:** `<from terraform output>`
```

### Option 2: Don't commit DEPLOYMENT_STEPS.md
Add it to `.gitignore`:
```bash
echo "DEPLOYMENT_STEPS.md" >> .gitignore
```

## GitHub Secrets (Secure)

These are stored securely in GitHub and never appear in your repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `OPENAI_API_KEY`

Access at: https://github.com/YOUR_USERNAME/practice-CICD/settings/secrets/actions

## AWS Secrets Manager (Secure)

Your OpenAI API key is also stored in AWS Secrets Manager:
- Secret name: `llm-app/openai-key`
- Region: `ca-central-1`
- Accessed by: ECS tasks via IAM role (no hardcoded credentials needed)

## Verification

To verify no secrets will be committed:

```bash
# Check what git will track
git status

# Verify specific files are ignored
git check-ignore -v .env terraform/terraform.tfvars terraform/.terraform/

# Should show these files are matched by .gitignore
```

## If You Accidentally Commit Secrets

1. **Immediately rotate the credentials:**
   - AWS: Delete the IAM access key and create a new one
   - OpenAI: Regenerate your API key at https://platform.openai.com/api-keys

2. **Remove from git history:**
   ```bash
   # Use git filter-repo or BFG Repo-Cleaner
   # Or simply delete the repo and start fresh if it's new
   ```

3. **Update GitHub Secrets and terraform.tfvars with new values**

## Best Practices

- ✅ Never hardcode secrets in code
- ✅ Use environment variables (`.env`) for local development
- ✅ Use GitHub Secrets for CI/CD pipelines
- ✅ Use AWS Secrets Manager for production workloads
- ✅ Always check `git status` before committing
- ✅ Review `.gitignore` regularly
- ⚠️ Rotate credentials if ever exposed
