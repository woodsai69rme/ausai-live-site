# Organized Drive System - Complete User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Directory Structure Overview](#directory-structure-overview)
3. [Maintenance Script](#maintenance-script)
4. [Auto-Sort Script](#auto-sort-script)
5. [Archive Old Projects Script](#archive-old-projects-script)
6. [System Dashboard](#system-dashboard)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction
This manual provides comprehensive guidance on using the organized drive system implemented for your C:\Users\karma and X: drives. The system consists of a logical directory structure and automated tools to maintain organization.

## Directory Structure Overview

### C:\Users\karma Organization
- **CONFIG/** - All configuration files and settings
- **PROJECTS/** - All projects organized by status
  - ACTIVE/ - Currently active projects
  - ARCHIVED/ - Completed projects
  - BACKUPS/ - Project backups
- **DOCUMENTATION/** - All documentation files
- **SCRIPTS/** - All executable scripts
- **AI_TOOLS/** - AI-related tools and configurations
  - CHATGPT/ - ChatGPT related tools
  - CLAUDE/ - Claude related tools
  - GEMINI/ - Gemini related tools
  - GENERAL/ - General AI tools
- **TOOLS/** - Various utilities and tools
- **MEDIA/** - Media files
- **TEMP/** - Temporary files (regular cleanup)
- **PERSONAL/** - Personal files unrelated to work

### X: Drive Organization
- **AI_MODELS/** - All AI models and related tools
  - LMSTUDIO_MODELS/ - Models for LM Studio
  - OLLAMA_MODELS/ - Models for Ollama
  - MODEL_SCRIPTS/ - Scripts for model management
- **DEVELOPMENT/** - Development environments and projects
  - ENVIRONMENTS/ - Virtual environments
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
- **ARCHIVES/** - Long-term storage and archives

## Maintenance Script
### Purpose
Performs regular cleanup and monitoring tasks to keep your organized drives running smoothly.

### How to Use
1. Double-click `maintenance_script.bat` to run it
2. The script will clean TEMP directories and check disk space
3. Review the recommendations at the end

### Scheduling
Schedule weekly for optimal maintenance:
1. Open Task Scheduler
2. Create Basic Task named "Drive Maintenance"
3. Set to run weekly
4. Action: Start a program -> browse to `maintenance_script.bat`

## Auto-Sort Script
### Purpose
Automatically organizes files from your Downloads folder into the appropriate directories in your organized system.

### How to Use
1. Place files in your Downloads folder
2. Run `auto_sort_script.bat` by double-clicking it
3. The script will move files to appropriate directories

### Supported File Types
- Documents: PDF, DOC, TXT, RTF, MD
- Media: JPG, PNG, MP4, MP3, etc.
- Scripts: PY, JS, BAT, SH, TS, TSX
- Tools: EXE, MSI, ZIP, RAR, etc.

### Scheduling
Schedule daily for automatic organization:
1. Open Task Scheduler
2. Create Basic Task named "Auto-Sort Downloads"
3. Set to run daily
4. Action: Start a program -> browse to `auto_sort_script.bat`

## Archive Old Projects Script
### Purpose
Identifies projects that haven't been modified recently and offers to move them to archived directories.

### How to Use
1. Run `archive_old_projects.bat` by double-clicking it
2. The script will scan for projects older than 90 days
3. For each old project found, confirm archiving with 'y' or skip with 'n'

### Configuration
Change the age threshold by modifying the "-90" values in the script to your desired number of days.

### Scheduling
Schedule monthly for periodic cleanup:
1. Open Task Scheduler
2. Create Basic Task named "Archive Old Projects"
3. Set to run monthly
4. Action: Start a program -> browse to `archive_old_projects.bat`

## System Dashboard
### Purpose
Provides an overview of your organized drive system including directory status and disk space information.

### How to Use
1. Run `system_dashboard.bat` by double-clicking it
2. Review the status of all organizational directories
3. Check disk space information
4. Review available maintenance scripts and recommendations

### Scheduling
Schedule weekly for system monitoring:
1. Open Task Scheduler
2. Create Basic Task named "System Dashboard"
3. Set to run weekly
4. Action: Start a program -> browse to `system_dashboard.bat`

## Best Practices

### Daily
- Place new files in the appropriate category directory
- Run the auto-sort script for files in Downloads
- Keep temporary files in the TEMP directory

### Weekly
- Run the maintenance script
- Check the system dashboard
- Clean up the TEMP directory if needed

### Monthly
- Run the archive old projects script
- Review disk space usage
- Check for any files that need manual organization

### General
- Follow the organizational structure consistently
- Create subdirectories within categories if needed
- Use descriptive names for files and directories
- Regularly back up critical data

## Troubleshooting

### Script won't run
- Make sure you're running as administrator if needed
- Check that file paths in the script are correct
- Ensure all destination directories exist

### Files not sorting correctly
- Verify that destination directories exist
- Check file extensions match what the script expects
- Review the script for any typos

### Disk space still low
- Run the maintenance script to clean TEMP directories
- Use the archive script to move old projects
- Check for large files that might need special handling

### Missing directories
- Re-run the organization scripts to recreate missing directories
- Check that the original organization was completed successfully

For additional help, refer to the individual documentation files in the docs directory.