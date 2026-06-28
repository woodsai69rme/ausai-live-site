# GitHub Secrets Management Guide

This document describes the required secrets for the optimized CI/CD pipeline. All secrets must be configured in your GitHub repository's **Settings > Secrets and variables > Actions** section.

## Required Secrets

### Docker Hub Secrets
```
DOCKERHUB_USERNAME      # Your Docker Hub username
DOCKERHUB_TOKEN         # Docker Hub personal access token (create at https://hub.docker.com/settings/security)
```

### Kubernetes Secrets
```
KUBE_CONFIG             # Base64 encoded Kubernetes config file for cluster access
```

### Slack Notification Secrets
```
SLACK_BOT_TOKEN         # Slack bot token (beginning with xoxb-)
SLACK_CHANNEL_ID        # Slack channel ID (e.g., C0123456789)
```

### Security Scanning Secrets
```
SNYK_TOKEN              # Snyk API token (for Node.js dependency scanning)
```

### Application Secrets (for Kubernetes deployment)
These should be configured as Kubernetes secrets. Create them using:

```bash
kubectl create secret generic archon-secrets -n staging \
  --from-literal=supabase_url="your-supabase-url" \
  --from-literal=supabase_service_key="your-supabase-service-key" \
  --from-literal=openrouter_api_key="your-openrouter-api-key" \
  --from-literal=logfire_token="your-logfire-token"

kubectl create secret generic archon-secrets -n production \
  --from-literal=supabase_url="your-supabase-url" \
  --from-literal=supabase_service_key="your-supabase-service-key" \
  --from-literal=openrouter_api_key="your-openrouter-api-key" \
  --from-literal=logfire_token="your-logfire-token"
```

## How to Obtain Each Secret

### Docker Hub Token
1. Go to [Docker Hub Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. Give it a name like "GitHub Actions"
4. Select "Read & Write" permissions
5. Click "Create" and copy the token

### Kubernetes Config File
1. Get your kubeconfig file (usually `~/.kube/config`)
2. Base64 encode it: `cat ~/.kube/config | base64 -w 0`
3. Paste the encoded value as `KUBE_CONFIG` secret

### Slack Bot Token
1. Create a Slack app at [Slack API](https://api.slack.com/apps)
2. Go to "OAuth & Permissions"
3. Under "Bot Token Scopes", add:
   - `chat:write` - Send messages
   - `chat:write.public` - Send messages to public channels
4. Install the app to your workspace
5. Copy the "Bot User OAuth Token"

### Slack Channel ID
1. Open Slack
2. Right-click on the channel
3. Select "View channel details"
4. The channel ID is in the "About" tab (e.g., C0123456789)

### Snyk Token
1. Sign up for a [Snyk account](https://snyk.io)
2. Go to [Snyk Account Settings](https://app.snyk.io/account)
3. Click "API Token"
4. Copy your personal access token

## Best Practices for Secret Management

1. **Rotate Secrets Regularly**: Replace secrets at least every 90 days
2. **Use Least Privilege**: Give each secret the minimum permissions required
3. **Monitor Access**: Review secret access and usage regularly
4. **Secrets in Code**: Never commit secrets to your repository
5. **Environment Separation**: Use separate secrets for staging and production
6. **Secret Scanning**: Enable GitHub's secret scanning feature to detect accidental secret commits

## Secret Rotation Schedule

| Secret Type | Rotation Frequency |
|-------------|-------------------|
| Docker Hub Token | Every 6 months |
| Kubernetes Config | Every 6 months |
| Slack Bot Token | Every 6 months |
| Snyk Token | Every 6 months |
| Application Secrets | Every 12 months |

## Troubleshooting Secrets

### Secret Not Found Error
1. Check that the secret name matches exactly in your workflow
2. Verify the secret is configured in the correct repository
3. Ensure the secret is available to the workflow (check environment restrictions)

### Permission Denied Errors
1. Verify the secret has the required permissions
2. Check that the secret hasn't expired
3. Confirm the service account has access to the secret

### Rate Limiting
1. Some secrets (like Docker Hub tokens) may have rate limits
2. Monitor your usage and adjust if needed
3. Consider using fine-grained tokens for better control
