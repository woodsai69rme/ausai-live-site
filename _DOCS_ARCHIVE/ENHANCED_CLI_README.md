# Enhanced Charm Crush CLI

## 🚀 Complete AI Assistant with GitHub & Disk Management

A comprehensive suite of tools for developers, combining AI assistance, GitHub repository management, and intelligent disk cleanup.

### 🎯 Quick Overview

This is a complete enhancement of the original Charm Crush CLI that now includes:

- ✅ **All original AI features** (OpenRouter integration, multiple models, cost tracking)
- ✅ **GitHub repository management** (download, sync, organize)
- ✅ **Intelligent disk cleanup** (safe C:\ and X:\ cleaning)
- ✅ **Repository synchronization** (update existing repos, find duplicates)
- ✅ **Enhanced security** (encrypted API keys, safe operations)
- ✅ **Comprehensive setup** (automatic dependency installation)

## 📦 What's Included

### Core Files
```
├── charm_crush_enhanced.py          # Enhanced main CLI
├── github_bulk_downloader.py        # Bulk GitHub repository downloader
├── disk_cleanup_tool.py             # Intelligent disk cleanup tool
├── repo_sync_organizer.py           # Repository sync & organizer
├── setup_enhanced_cli.py            # Automatic setup script
├── requirements_enhanced.txt        # Python dependencies
├── QUICK_START.md                   # Quick start guide
└── ENHANCED_CLI_README.md           # This file
```

### Configuration Files (Created Automatically)
```
~/.charm_crush_enhanced/
├── config.json                      # Application settings
├── keys.json                        # Encrypted API keys
└── encryption.key                   # Encryption key
```

### Download Locations
```
X:/githubrepo/                       # Default repository location
├── repo1_owner1/
├── repo2_owner2/
└── ...
```

## 🚀 Installation & Setup

### One-Command Setup
```bash
cd C:/Users/karma
python setup_enhanced_cli.py
```

This will:
1. ✅ Check Python version (3.7+ required)
2. ✅ Install all dependencies automatically
3. ✅ Create configuration files
4. ✅ Generate startup scripts
5. ✅ Create documentation

### Manual Installation
```bash
# Install dependencies
pip install -r requirements_enhanced.txt

# Configure
python charm_crush_enhanced.py configure
```

## 🎯 Core Features

### 1. 🤖 AI Assistant (Enhanced)

**Chat & Code Generation:**
```bash
# Interactive chat
python charm_crush_enhanced.py chat "Create a Python web scraper"

# Code generation
python charm_crush_enhanced.py code "Build a React component for Todo app"

# Research and analysis
python charm_crush_enhanced.py research "Latest AI trends in 2024"
```

**Features:**
- ✅ OpenRouter integration (100+ AI models)
- ✅ Smart rate limiting with backoff
- ✅ Cost tracking and budget management
- ✅ Privacy mode with encrypted storage
- ✅ Multiple AI providers support

### 2. 📦 GitHub Repository Management

**Download All Repositories:**
```bash
# Download your repositories
python github_bulk_downloader.py --all --output X:/githubrepo

# Download starred repositories
python github_bulk_downloader.py --starred --output X:/githubrepo

# Download from organization
python github_bulk_downloader.py --org microsoft --output X:/githubrepo
```

**Repository Analysis:**
```bash
# List repositories without downloading
python github_bulk_downloader.py --user yourusername --list-only

# Search for specific repositories
python github_bulk_downloader.py --search "machine learning" --language python
```

### 3. 🧹 Intelligent Disk Cleanup

**Safe System Cleanup:**
```bash
# Dry run - see what would be deleted
python disk_cleanup_tool.py --dry-run

# Live cleanup
python disk_cleanup_tool.py --live

# Clean specific areas
python disk_cleanup_tool.py --live --locations temp cache logs
```

**Large File Analysis:**
```bash
# Find files > 100MB
python disk_cleanup_tool.py --large-files --threshold 100

# Scan specific drives
python disk_cleanup_tool.py --drives C: X: --large-files
```

**Windows-Specific Cleanup:**
```bash
# Clean Windows Update cache
python disk_cleanup_tool.py --windows-specific --live

# Clean user temp files
python disk_cleanup_tool.py --locations temp --live
```

### 4. 🔄 Repository Synchronization & Organization

**Sync Existing Repositories:**
```bash
# Check for updates
python repo_sync_organizer.py --base-path X:/githubrepo --check-updates --token YOUR_TOKEN

# Sync with updates
python repo_sync_organizer.py --base-path X:/githubrepo --sync --token YOUR_TOKEN
```

**Repository Organization:**
```bash
# Find duplicate repositories
python repo_sync_organizer.py --base-path X:/githubrepo --find-duplicates

# Remove duplicates (dry run first)
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates --dry-run
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates
```

**Inventory Management:**
```bash
# Export repository inventory
python repo_sync_organizer.py --base-path X:/githubrepo --export inventory.json

# Analyze repository organization
python repo_sync_organizer.py --base-path X:/githubrepo --scan-only
```

## 🎮 Enhanced CLI Commands

### Configuration & Status
```bash
# Initial configuration
python charm_crush_enhanced.py configure

# Show system status
python charm_crush_enhanced.py status

# Show usage statistics
python charm_crush_enhanced.py usage

# List available models
python charm_crush_enhanced.py models
```

### GitHub Operations
```bash
# Check downloaded repositories
python charm_crush_enhanced.py github --action status

# Download repositories
python charm_crush_enhanced.py github --action download --target yourusername

# Sync repositories
python charm_crush_enhanced.py github --action sync --target X:/githubrepo
```

### Disk Management
```bash
# Dry run cleanup
python charm_crush_enhanced.py cleanup --dry-run

# Live cleanup
python charm_crush_enhanced.py cleanup --live --drives C: X:

# Analyze large files
python charm_crush_enhanced.py analyze --directory C:/ --threshold 50
```

## 🔐 Security Features

### Encrypted Storage
- ✅ API keys encrypted with Fernet encryption
- ✅ Configuration files stored securely
- ✅ No plaintext keys in configuration

### Safe Operations
- ✅ Dry run mode for all destructive operations
- ✅ System file protection (never deletes system files)
- ✅ Permission checking for sensitive operations
- ✅ Rate limiting to prevent API abuse

### Privacy Mode
- ✅ Optional privacy mode for sensitive operations
- ✅ No logging of sensitive content
- ✅ Encrypted context storage

## 📊 Monitoring & Analytics

### Cost Tracking
```bash
# View monthly costs
python charm_crush_enhanced.py usage

# Check budget status
python charm_crush_enhanced.py status

# Cost breakdown by model
python charm_crush_enhanced.py usage --detailed
```

### Repository Analytics
```bash
# Repository organization report
python repo_sync_organizer.py --base-path X:/githubrepo --scan-only

# Size analysis
python repo_sync_organizer.py --base-path X:/githubrepo --analyze-size
```

### Disk Analytics
```bash
# Disk usage by category
python disk_cleanup_tool.py --analyze --drives C:

# Large file analysis
python disk_cleanup_tool.py --large-files --threshold 50
```

## 🎯 Common Workflows

### Workflow 1: Initial Setup & Repository Download
```bash
# 1. Setup
python setup_enhanced_cli.py

# 2. Configure
python charm_crush_enhanced.py configure

# 3. Download all repositories
python github_bulk_downloader.py --all --output X:/githubrepo

# 4. Verify download
python repo_sync_organizer.py --base-path X:/githubrepo --scan-only
```

### Workflow 2: Weekly Maintenance
```bash
# 1. Sync repositories
python repo_sync_organizer.py --base-path X:/githubrepo --sync --token YOUR_TOKEN

# 2. Clean up duplicates
python repo_sync_organizer.py --base-path X:/githubrepo --find-duplicates
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates --dry-run
python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates

# 3. Disk cleanup
python disk_cleanup_tool.py --dry-run
python disk_cleanup_tool.py --live

# 4. Check costs
python charm_crush_enhanced.py status
```

### Workflow 3: Development & Research
```bash
# 1. Research topic
python charm_crush_enhanced.py research "Best practices for React development"

# 2. Generate code
python charm_crush_enhanced.py code "Create a Python Flask API endpoint"

# 3. Review code
python charm_crush_enhanced.py review --file my_code.py

# 4. Scaffolding
python charm_crush_enhanced.py scaffold --type react --name my-app
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Set default API keys
export OPENROUTER_API_KEY="your_key_here"
export GITHUB_TOKEN="your_token_here"

# Set default directories
export GITHUB_DOWNLOAD_DIR="X:/githubrepo"
export CLEANUP_TARGET_DRIVES="C:,X:"
```

### Configuration File (~/.charm_crush_enhanced/config.json)
```json
{
  "rate_limit_per_minute": 60,
  "rate_limit_buffer": 0.2,
  "monthly_budget": 100.0,
  "default_model": "gpt-3.5-turbo",
  "download_directory": "X:/githubrepo",
  "cleanup_min_size": 10240,
  "cleanup_max_age_days": 30
}
```

## 🚨 Important Notes

### Safety First
- ✅ **Always use `--dry-run` first** for cleanup operations
- ✅ **Backup important data** before running cleanup tools
- ✅ **Verify GitHub tokens** have correct permissions
- ✅ **Check disk space** before downloading large repositories

### Performance Tips
- ✅ **Use `--max-repos`** to limit downloads if you have many repositories
- ✅ **Run during off-peak hours** for better performance
- ✅ **Monitor disk space** during large operations
- ✅ **Use specific categories** for targeted cleanup

### Troubleshooting
```bash
# Check Python version
python --version

# Check dependencies
python -c "import aiohttp, cryptography; print('Dependencies OK')"

# Check Git installation
git --version

# Check disk space
python disk_cleanup_tool.py --analyze --drives C:
```

## 📈 Performance & Limits

### GitHub API Limits
- **Without token**: 60 requests/hour
- **With token**: 5000 requests/hour
- **Rate limiting**: Built-in protection
- **Concurrent downloads**: Default 5, configurable

### Disk Operations
- **Timeout**: Default 5 minutes per operation
- **Concurrent operations**: Default 3, configurable
- **Memory usage**: Optimized for large repositories
- **Safety**: Never touches system directories

### AI Operations
- **Rate limiting**: Smart backoff with buffers
- **Cost tracking**: Real-time monitoring
- **Model selection**: 100+ models available
- **Privacy**: Encrypted context storage

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd charm-crush-enhanced
python setup_enhanced_cli.py

# Run tests
python -m pytest tests/

# Check code quality
python -m flake8 .
```

### Adding New Features
1. **Follow existing patterns** for consistency
2. **Add tests** for new functionality
3. **Update documentation** with examples
4. **Test on multiple platforms** (Windows, Linux, macOS)

### Reporting Issues
- Include Python version
- Include OS and platform info
- Provide error messages and stack traces
- Describe expected vs actual behavior

## 📄 License

This software is provided as-is for educational and development purposes. Users are responsible for:

- ✅ Following GitHub's Terms of Service
- ✅ Respecting API rate limits
- ✅ Backing up important data
- ✅ Using safely and responsibly

## 🆘 Support & Help

### Built-in Help
```bash
python charm_crush_enhanced.py --help
python github_bulk_downloader.py --help
python disk_cleanup_tool.py --help
python repo_sync_organizer.py --help
```

### Documentation
- `QUICK_START.md` - Quick start guide
- `ENHANCED_CLI_README.md` - Comprehensive documentation
- Inline help for all commands

### Common Issues
1. **"Python not found"** - Use full path to Python executable
2. **"Git not found"** - Install Git for Windows
3. **"Permission denied"** - Run as administrator
4. **"Module not found"** - Reinstall dependencies

## 🎉 What's New (vs Original)

### 🆕 Enhanced Features
- ✅ **GitHub Integration** - Download, sync, and organize repositories
- ✅ **Disk Cleanup** - Safe system cleanup with Windows optimizations
- ✅ **Repository Sync** - Keep existing repos up to date
- ✅ **Duplicate Detection** - Find and remove duplicate repositories
- ✅ **Large File Analysis** - Identify space-consuming files
- ✅ **Enhanced Security** - Encrypted API keys and safe operations
- ✅ **Comprehensive Setup** - Automatic dependency installation
- ✅ **Better Documentation** - Quick start guides and examples

### 🔧 Technical Improvements
- ✅ **Better Error Handling** - Graceful failure with informative messages
- ✅ **Concurrency Control** - Smart parallel operations
- ✅ **Rate Limiting** - Built-in API rate limit protection
- ✅ **Progress Tracking** - Real-time operation status
- ✅ **Configuration Management** - Persistent settings and keys
- ✅ **Cross-Platform** - Works on Windows, Linux, and macOS

### 📊 Monitoring & Analytics
- ✅ **Cost Tracking** - Real-time AI usage monitoring
- ✅ **Repository Analytics** - Size and organization insights
- ✅ **Disk Analytics** - Space usage by category
- ✅ **Usage Statistics** - Detailed operation logs

## 🚀 Future Enhancements

### Planned Features
- ✅ **Web Dashboard** - Visual interface for all operations
- ✅ **Plugin System** - Extensible functionality
- ✅ **Backup Integration** - Automatic backup before operations
- ✅ **Scheduling** - Automated maintenance tasks
- ✅ **Multi-User** - Team collaboration features

### Community Contributions
We welcome contributions for:
- ✅ New AI model integrations
- ✅ Additional cleanup categories
- ✅ Platform-specific optimizations
- ✅ Enhanced security features
- ✅ Better error handling and reporting

---

## 📞 Getting Help

If you encounter issues or have questions:

1. **Check the documentation** - `QUICK_START.md` and `--help`
2. **Review the examples** - Each tool has comprehensive examples
3. **Use dry-run mode** - Test operations before executing
4. **Check logs** - Detailed logging for troubleshooting
5. **Report issues** - Include system info and error messages

**Happy coding with Enhanced Charm Crush CLI!** 🚀