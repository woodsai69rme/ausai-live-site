# Charm Crush - User Manual

## Quick Start Guide

### Installation
1. **Enhanced CLI:** No installation required, runs directly with Python
2. **CCR2:** Navigate to `C:\Users\karma\EXPERIMENTAL\_UNSORTED\CCR2\`

### First-Time Setup

#### 1. Configure API Keys
```bash
# Enhanced CLI
python charm_crush_enhanced.py configure

# CCR2
python scripts\charm_crush_cli.py configure
```

#### 2. Set Up GitHub (Optional)
```bash
# Get GitHub token from https://github.com/settings/tokens
# Enable: repo, user, delete_repo
```

#### 3. Configure Download Directory
- Default: `~/github_repos`
- Recommended: `X:\githubrepo`

## Core Features

### AI Chat
```bash
# Enhanced CLI
python charm_crush_enhanced.py chat --message "Hello, how are you?"

# CCR2
python scripts\charm_crush_cli.py chat "Hello, how are you?"
```

**Available Models:**
- GPT-3.5 Turbo
- GPT-4
- Claude 3 Opus
- Claude 3 Sonnet
- Gemini Pro
- OpenRouter Free Models

### GitHub Repository Management
```bash
# Download all repositories from user
python scripts\charm_crush_cli.py github download --target username

# Sync repositories from X:\githubrepo
python scripts\charm_crush_cli.py github sync

# Check repository status
python scripts\charm_crush_cli.py github status
```

### Disk Cleanup
```bash
# Analyze large files (dry run)
python scripts\charm_crush_cli.py cleanup analyze --drives C: X:

# Clean up temp files (dry run)
python scripts\charm_crush_cli.py cleanup --dry-run

# Live cleanup (permanent deletion)
python scripts\charm_crush_cli.py cleanup --live
```

### Repository Management
```bash
# Scan repositories
python scripts\charm_crush_cli.py repo scan

# Check for updates
python scripts\charm_crush_cli.py repo check

# Sync all repositories
python scripts\charm_crush_cli.py repo sync

# Find duplicate repositories
python scripts\charm_crush_cli.py repo duplicates
```

## Configuration

### Enhanced CLI Configuration
```json
{
  "rate_limit_per_minute": 60,
  "rate_limit_buffer": 0.2,
  "monthly_budget": 100.0,
  "default_model": "gpt-3.5-turbo",
  "download_directory": "~/github_repos"
}
```

### CCR2 Configuration
```json
{
  "cost_tracking_enabled": true,
  "rate_limit_strategy": "smart_buffer",
  "model_priority": ["openrouter-free", "claude-direct"],
  "budget_limits": {
    "monthly": 50.0,
    "daily": 2.0
  },
  "security": {
    "encryption_enabled": true,
    "key_rotation_schedule": "monthly"
  }
}
```

### API Key Management
```bash
# Set API key
python scripts\charm_crush_cli.py configure api --provider openrouter --key YOUR_KEY

# Get API key
python scripts\charm_crush_cli.py configure api --provider openrouter
```

## Advanced Features

### Cost Optimization
```bash
# Check cost usage
python scripts\charm_crush_cli.py cost usage

# Set budget limits
python scripts\charm_crush_cli.py cost budget --monthly 50 --daily 2

# Optimize costs
python scripts\charm_crush_cli.py cost optimize
```

### Model Management
```bash
# List available models
python scripts\charm_crush_cli.py models list

# Update free models
python scripts\charm_crush_cli.py models update

# Set model priority
python scripts\charm_crush_cli.py models priority --primary openrouter-free --backup claude-direct
```

### Code Generation
```bash
# Generate Python code
python scripts\charm_crush_cli.py code generate --language python --prompt "Create a web scraper"

# Review code
python scripts\charm_crush_cli.py code review --file script.py
```

## GUI Interface

### Launching the GUI
```bash
# Enhanced CLI GUI
cd C:\Users\karma\projects\ACTIVE\charm_crush_scripts
python charm_crush_gui.py
```

### GUI Features
- **🏠 Home Tab:** Quick actions and status
- **🤖 AI Assistant Tab:** Chat and code generation
- **🐙 GitHub Tab:** Repository management
- **💾 Disk Cleanup Tab:** Cleanup operations
- **📁 Repository Management Tab:** Sync and duplicates

## Security Features

### API Key Encryption
- **Algorithm:** Fernet symmetric encryption
- **Storage:** Encrypted files in home directory
- **Protection:** Access controlled by encryption keys

### Security Best Practices
1. **Regular Key Rotation:** Monthly key rotation recommended
2. **Backup Encryption Keys:** Secure backup required
3. **Environment Variables:** Use for sensitive data
4. **Audit Logs:** Monitor API usage

## Troubleshooting

### Common Issues

#### API Key Not Working
```bash
# Check if API key is set
python scripts\charm_crush_cli.py configure api --provider openrouter

# Reconfigure API key
python scripts\charm_crush_cli.py configure api --provider openrouter --key NEW_KEY
```

#### GitHub Operations Failing
```bash
# Check GitHub token
python scripts\charm_crush_cli.py configure github --token YOUR_TOKEN

# Verify token permissions
# Required: repo, user, delete_repo
```

#### Disk Cleanup Not Working
```bash
# Run in dry-run mode first
python scripts\charm_crush_cli.py cleanup --dry-run

# Check drive permissions
# Ensure user has write access to target drives
```

### Performance Issues

#### Rate Limiting
- **Enhanced CLI:** 60 requests/minute
- **CCR2:** Smart rate limiting with buffer
- **Solution:** Wait for rate limit reset or upgrade to premium API

#### Memory Usage
- **Recommendation:** 2GB RAM minimum
- **Solution:** Close other applications if memory issues occur

## Maintenance

### Regular Updates
```bash
# Update free models
python scripts\charm_crush_cli.py models update

# Check for system updates
python scripts\charm_crush_cli.py update check
```

### Backup Procedures
```bash
# Backup configuration
cp ~/.charm_crush_config.json ~/backup/
cp ~/.charm_crush_encryption.key ~/backup/

# Backup repositories
rsync -av X:\githubrepo ~/backup/
```

### Security Updates
```bash
# Rotate API keys monthly
python scripts\charm_crush_cli.py configure api --rotate

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Support

### Documentation
- **Main Guide:** `CHARM_CRUSH_COMPLETE_DOCUMENTATION.md`
- **API Reference:** `API_REFERENCE.md`
- **Integration Guides:** `INTEGRATION_MAP.md`

### Community
- **GitHub Issues:** After Git setup
- **Documentation:** Comprehensive guides available
- **Updates:** Regular model and feature updates

---

**Version:** 2.0  
**Last Updated:** March 8, 2026  
**Support:** Community-based  
**Status:** ✅ **ACTIVE**