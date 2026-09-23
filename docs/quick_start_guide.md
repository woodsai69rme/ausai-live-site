# Quick Start Guide: Organized Drive System

## Overview
This guide provides a quick introduction to using your newly organized drive system for C:\Users\karma and X: drives.

## Immediate Actions

### 1. Familiarize Yourself with the New Structure
- Open File Explorer and navigate to C:\Users\karma
- Notice the new organizational directories: CONFIG, PROJECTS, DOCUMENTATION, SCRIPTS, etc.
- Navigate to X: drive to see the new structure: AI_MODELS, DEVELOPMENT, CONTENT_CREATION, etc.

### 2. Run the System Dashboard
- Double-click `system_dashboard.bat` in C:\Users\karma
- Review the status of all directories
- Check disk space information

## Daily Usage

### 1. File Placement
- New configuration files → `C:\Users\karma\CONFIG`
- New projects → `C:\Users\karma\PROJECTS\ACTIVE`
- New documents → `C:\Users\karma\DOCUMENTATION`
- New scripts → `C:\Users\karma\SCRIPTS`
- New media → `C:\Users\karma\MEDIA`
- Temporary files → `C:\Users\karma\TEMP`

### 2. Using the Auto-Sort Feature
- Place downloaded files in your Downloads folder
- Run `auto_sort_script.bat` to automatically organize them
- Or schedule it to run automatically (recommended daily)

## Weekly Maintenance

### 1. Run Maintenance Script
- Double-click `maintenance_script.bat`
- This cleans TEMP directories and checks disk space
- Or schedule it to run automatically (recommended weekly)

### 2. Check System Status
- Run `system_dashboard.bat` to review system health
- Look for recommendations at the end of the report

## Monthly Maintenance

### 1. Archive Old Projects
- Run `archive_old_projects.bat`
- This identifies projects not modified in 90+ days
- Move them to archived directories to keep active areas clean

## Setting Up Automation

### 1. Schedule Maintenance Tasks
For each script, set up automatic scheduling:
1. Press Win+R, type "taskschd.msc", press Enter
2. Click "Create Basic Task" in the right panel
3. Name it appropriately (e.g., "Weekly Drive Maintenance")
4. Set schedule (daily for auto-sort, weekly for maintenance, monthly for archiving)
5. Action: "Start a program" → browse to the appropriate .bat file

## Quick Reference

### Key Directories
- **Active Projects**: `C:\Users\karma\PROJECTS\ACTIVE` or `X:\DEVELOPMENT\ACTIVE_PROJECTS`
- **Documentation**: `C:\Users\karma\DOCUMENTATION`
- **Scripts**: `C:\Users\karma\SCRIPTS`
- **Media**: `C:\Users\karma\MEDIA` or `X:\CONTENT_CREATION\MEDIA`
- **AI Tools**: `C:\Users\karma\AI_TOOLS`
- **Temporary Files**: `C:\Users\karma\TEMP` or `X:\TEMP`

### Maintenance Scripts Location
All scripts are located in `C:\Users\karma`:
- `maintenance_script.bat` - Weekly cleanup
- `auto_sort_script.bat` - Daily file sorting
- `archive_old_projects.bat` - Monthly project archiving
- `system_dashboard.bat` - System status overview

## Need More Help?

Refer to these documentation files in `C:\Users\karma\docs`:
- `complete_user_manual.md` - Full system documentation
- `troubleshooting_guide.md` - Solutions to common problems
- Individual script documentation files

## Important Notes
- The system is designed to be intuitive and maintainable
- Always run scripts as administrator for best results
- Regular maintenance keeps the system running optimally
- The organization structure can be customized to fit your needs