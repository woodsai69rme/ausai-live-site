# Enhanced Charm Crush CLI - Quick Start Guide

## 🚀 Installation & Setup

### 1. Run Setup Script
```bash
cd C:/Users/karma
python setup_enhanced_cli.py
```

### 2. Configure API Keys
```bash
python charm_crush_enhanced.py configure
```
- Enter OpenRouter API key (optional, for AI features)
- Enter GitHub Personal Access Token (optional, for GitHub features)
- Set download directory (default: X:/githubrepo or ~/github_repos)

## 📋 Core Features

### 🤖 AI Assistant
```bash
# Chat with AI
python charm_crush_enhanced.py chat "Create a Python function"

# Check status and costs
python charm_crush_enhanced.py status
```

### 📦 GitHub Repository Management

#### Download All Your Repositories
```bash
# Your repositories
python github_bulk_downloader.py --all --output X:/githubrepo

# Starred repositories only
python github_bulk_downloader.py --starred --output X:/githubrepo

# Organization repositories
python github_bulk_downloader.py --org mycompany --output X:/githubrepo

# List first, then download (to check what you'll get)
python github_bulk_downloader.py --user yourusername --list-only
python github_bulk_downloader.py --user yourusername --output X:/githubrepo
```

#### Sync Existing Repositories in X:\githubrepo
```bash
# Check for updates (dry run)
python repo_sync_organizer.py --base-path X:/githubrepo --check-updates --token YOUR_TOKEN

# Sync repositories
python repo_sync_organizer.py --base-path X:/githubrepo --sync --token YOUR_TOKEN

# Find duplicates
python repo_sync_organizer.py --base-path X:/githubrepo --find-duplicates

# Remove duplicates (dry run first)
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates --dry-run
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates
```

### 🧹 Disk Cleanup

#### Safe Cleanup (C:\ and X:\ drives)
```bash
# Dry run - see what would be deleted
python disk_cleanup_tool.py --dry-run

# Real cleanup
python disk_cleanup_tool.py --live

# Clean specific areas only
python disk_cleanup_tool.py --live --locations temp cache

# Windows-specific cleanup
python disk_cleanup_tool.py --live --windows-specific
```

#### Large File Analysis
```bash
# Find files > 100MB on C:\
python disk_cleanup_tool.py --large-files --threshold 100

# Scan X:\ drive
python disk_cleanup_tool.py --large-files --threshold 50 --drives X:
```

## 🔧 Enhanced CLI Commands

```bash
# Configure
python charm_crush_enhanced.py configure

# Status
python charm_crush_enhanced.py status

# GitHub operations
python charm_crush_enhanced.py github --action status
python charm_crush_enhanced.py github --action download --target yourusername
python charm_crush_enhanced.py github --action sync --target X:/githubrepo

# Disk cleanup
python charm_crush_enhanced.py cleanup --dry-run
python charm_crush_enhanced.py cleanup --live --drives C: X:

# File analysis
python charm_crush_enhanced.py analyze --directory C:/ --threshold 50
```

## 📁 File Locations

- **Scripts**: `C:/Users/karma/`
- **Config**: `~/.charm_crush_enhanced/`
- **Downloads**: `X:/githubrepo` (or configured path)

## 🎯 Common Workflows

### 1. Initial Setup & Download
```bash
# 1. Setup
python setup_enhanced_cli.py

# 2. Configure
python charm_crush_enhanced.py configure

# 3. Download all repos
python github_bulk_downloader.py --all --output X:/githubrepo
```

### 2. Weekly Sync & Cleanup
```bash
# 1. Sync existing repos
python repo_sync_organizer.py --base-path X:/githubrepo --sync --token YOUR_TOKEN

# 2. Clean disk (dry run first)
python disk_cleanup_tool.py --dry-run
python disk_cleanup_tool.py --live

# 3. Check large files
python disk_cleanup_tool.py --large-files --threshold 100
```

### 3. Find & Organize
```bash
# 1. Find duplicates
python repo_sync_organizer.py --base-path X:/githubrepo --find-duplicates

# 2. Remove duplicates
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates --dry-run
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates

# 3. Export inventory
python repo_sync_organizer.py --base-path X:/githubrepo --export inventory.json
```

## 🔐 Security Tips

1. **GitHub Token**: Get from https://github.com/settings/tokens (give repo access)
2. **OpenRouter Key**: Get from https://openrouter.ai/settings/keys
3. **Permissions**: Keys are stored encrypted in `~/.charm_crush_enhanced/keys.json`
4. **Safety**: Always use `--dry-run` first for cleanup operations

## 🚨 Important Notes

⚠️ **Disk Cleanup Safety**:
- Always run `--dry-run` first
- Avoids system directories automatically
- Requires confirmation for live cleanup

⚠️ **GitHub Rate Limits**:
- Without token: 60 requests/hour
- With token: 5000 requests/hour
- Use `--max-repos` to limit downloads

⚠️ **Git Required**:
- Ensure Git is installed: `git --version`
- Download from: https://git-scm.com/

## 📊 Monitoring

```bash
# Check costs
python charm_crush_enhanced.py status

# Check downloads
python repo_sync_organizer.py --base-path X:/githubrepo --scan-only

# Check disk usage
python disk_cleanup_tool.py --large-files --threshold 1
```

## 🔧 Troubleshooting

### "Python not found"
```bash
# Use full path to Python
C:/Python311/python.exe charm_crush_enhanced.py configure
```

### "Git not found"
```bash
# Install Git for Windows
# Then restart terminal
```

### "Permission denied"
```bash
# Run as administrator for system cleanup
# Or use --dry-run to see what's affected
```

### "No module named..."
```bash
# Reinstall dependencies
python setup_enhanced_cli.py
```

## 📞 Support

All tools include help:
```bash
python charm_crush_enhanced.py --help
python github_bulk_downloader.py --help
python disk_cleanup_tool.py --help
python repo_sync_organizer.py --help
```

## 🎉 Quick Commands Summary

```bash
# Setup
python setup_enhanced_cli.py
python charm_crush_enhanced.py configure

# Download repos
python github_bulk_downloader.py --all --output X:/githubrepo

# Sync repos
python repo_sync_organizer.py --base-path X:/githubrepo --sync --token YOUR_TOKEN

# Clean disk
python disk_cleanup_tool.py --live

# AI chat
python charm_crush_enhanced.py chat "Hello!"
```

## ⚡ Performance Tips

1. **Concurrent Downloads**: Default 5, can increase with `--max-concurrent`
2. **Timeout**: Default 5 minutes, increase for large repos
3. **Rate Limiting**: Built-in to avoid API limits
4. **Memory**: Large repos may need more RAM

## 📦 File Structure After Setup

```
C:/Users/karma/
├── charm_crush_enhanced.py          # Main CLI
├── github_bulk_downloader.py        # GitHub downloads
├── disk_cleanup_tool.py             # Disk cleanup
├── repo_sync_organizer.py           # Repo sync
├── setup_enhanced_cli.py            # Setup script
├── requirements_enhanced.txt        # Dependencies
├── QUICK_START.md                   # This file
└── ENHANCED_CLI_README.md           # Detailed docs

~/.charm_crush_enhanced/
├── config.json                      # Settings
├── keys.json                        # Encrypted keys
└── encryption.key                   # Encryption key

X:/githubrepo/                       # Your repositories
├── repo1_owner1/
├── repo2_owner2/
└── ...
```

Happy coding! 🚀