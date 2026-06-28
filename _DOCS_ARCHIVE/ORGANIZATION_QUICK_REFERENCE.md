# Quick Reference Guide: Organized Drive Structure

## C:\Users\karma Directory Structure

### Main Categories:
- **CONFIG/** - All configuration files and settings
  - .bash_profile, .gitconfig, .qwenignore, etc.
  - .vscode, .config, and other configuration directories

- **PROJECTS/** - All projects organized by status
  - ACTIVE/ - Currently active projects
  - ARCHIVED/ - Completed projects
  - BACKUPS/ - Project backups

- **DOCUMENTATION/** - All documentation files
  - .md, .txt, .pdf files
  - Project documentation, guides, etc.

- **SCRIPTS/** - All executable scripts
  - .py, .js, .bat files
  - Organized by function (AI, automation, utilities)

- **AI_TOOLS/** - AI-related tools and configurations
  - CHATGPT/ - ChatGPT related tools
  - CLAUDE/ - Claude related tools
  - GEMINI/ - Gemini related tools
  - GENERAL/ - General AI tools

- **TOOLS/** - Various utilities and tools
  - Development tools, utilities, etc.

- **MEDIA/** - Media files
  - Images, videos, audio files

- **TEMP/** - Temporary files (regular cleanup)
  - Files for temporary storage

- **PERSONAL/** - Personal files unrelated to work
  - Private/personal content

## X: Drive Structure

### Main Categories:
- **AI_MODELS/** - All AI models and related tools
  - LMSTUDIO_MODELS/ - Models for LM Studio
  - OLLAMA_MODELS/ - Models for Ollama
  - MODEL_SCRIPTS/ - Scripts for model management

- **DEVELOPMENT/** - Development environments and projects
  - ENVIRONMENTS/ - Virtual environments (CODENV, venv)
  - ACTIVE_PROJECTS/ - Currently active projects
  - ARCHIVED_PROJECTS/ - Archived projects
  - BACKUPS/ - Project backups

- **CONTENT_CREATION/** - Content creation resources
  - DOCUMENTS/ - Written content
  - MEDIA/ - Images, videos, audio
  - DOWNLOADS/ - Downloaded content

- **TOOLS/** - Various tools and utilities
  - AUTOMATION/ - Automation scripts and tools
  - AI_MANAGEMENT/ - AI model management tools
  - UTILITIES/ - General utility tools

- **VIRTUAL_MACHINES/** - VM images and configurations
  - .vdi, .ova, .iso files

- **ARCHIVES/** - Long-term storage and archives
  - Old projects, backups, etc.

## Best Practices for Maintaining Organization

### Daily:
- Place new files in the appropriate category directory
- Move temporary files to the TEMP directory
- Clean up the TEMP directory regularly

### Weekly:
- Review the TEMP directory for files to delete
- Check if any active projects should be moved to ARCHIVED

### Monthly:
- Review disk space usage
- Archive old projects that are no longer active
- Back up critical directories

## Quick Access Shortcuts
To quickly navigate to common directories, you can use these paths:
- C:\Users\karma\PROJECTS\ACTIVE
- C:\Users\karma\DOCUMENTATION
- C:\Users\karma\SCRIPTS
- X:\DEVELOPMENT\ACTIVE_PROJECTS
- X:\CONTENT_CREATION\MEDIA
- X:\AI_MODELS\OLLAMA_MODELS

## Maintenance Script
Run the maintenance_script.bat file to perform regular cleanup tasks.