@echo off
REM Organization script for C:\Users\karma directory
REM This script creates the new directory structure and moves files according to the organization plan

echo Starting organization of C:\Users\karma directory...
echo Creating new directory structure...

REM Create main directories
if not exist "CONFIG" mkdir "CONFIG"
if not exist "PROJECTS" mkdir "PROJECTS"
if not exist "PROJECTS\ACTIVE" mkdir "PROJECTS\ACTIVE"
if not exist "PROJECTS\ARCHIVED" mkdir "PROJECTS\ARCHIVED"
if not exist "PROJECTS\BACKUPS" mkdir "PROJECTS\BACKUPS"
if not exist "TOOLS" mkdir "TOOLS"
if not exist "DOCUMENTATION" mkdir "DOCUMENTATION"
if not exist "AI_TOOLS" mkdir "AI_TOOLS"
if not exist "AI_TOOLS\CHATGPT" mkdir "AI_TOOLS\CHATGPT"
if not exist "AI_TOOLS\CLAUDE" mkdir "AI_TOOLS\CLAUDE"
if not exist "AI_TOOLS\GEMINI" mkdir "AI_TOOLS\GEMINI"
if not exist "AI_TOOLS\GENERAL" mkdir "AI_TOOLS\GENERAL"
if not exist "SCRIPTS" mkdir "SCRIPTS"
if not exist "MEDIA" mkdir "MEDIA"
if not exist "TEMP" mkdir "TEMP"
if not exist "PERSONAL" mkdir "PERSONAL"

echo Created directory structure.

REM Move configuration files
echo Moving configuration files...
move ".bash_profile" "CONFIG\" 2>nul
move ".bash_history" "CONFIG\" 2>nul
move ".gitconfig" "CONFIG\" 2>nul
move ".qwenignore" "CONFIG\" 2>nul
move ".secure_env" "CONFIG\" 2>nul
move ".vercelignore" "CONFIG\" 2>nul
move ".git-for-windows-updater" "CONFIG\" 2>nul
move ".lmstudio-home-pointer" "CONFIG\" 2>nul
move ".codexrc" "CONFIG\" 2>nul
move ".ctsystem" "CONFIG\" 2>nul
move ".augment-guidelines" "CONFIG\" 2>nul

REM Move configuration directories
robocopy ".config" "CONFIG\.config" /E /MOVE
robocopy ".vscode" "CONFIG\.vscode" /E /MOVE
robocopy ".qwen" "CONFIG\.qwen" /E /MOVE

REM Move documentation files
echo Moving documentation files...
move "*.md" "DOCUMENTATION\" 2>nul
move "*.txt" "DOCUMENTATION\" 2>nul

REM Move script files
echo Moving script files...
move "*.py" "SCRIPTS\" 2>nul
move "*.js" "SCRIPTS\" 2>nul
move "*.bat" "SCRIPTS\" 2>nul
move "*.ts" "SCRIPTS\" 2>nul
move "*.tsx" "SCRIPTS\" 2>nul

REM Move AI-related files to appropriate directories
echo Moving AI tool files...
move "ai_*.py" "AI_TOOLS\GENERAL\" 2>nul
move "*chatgpt*" "AI_TOOLS\CHATGPT\" 2>nul
move "*claude*" "AI_TOOLS\CLAUDE\" 2>nul
move "*gemini*" "AI_TOOLS\GEMINI\" 2>nul

REM Move project-related files
echo Moving project files...
move "PROJECT_*" "PROJECTS\ACTIVE\" 2>nul
move "*project*" "PROJECTS\ACTIVE\" 2>nul
move "*PROJECT*" "PROJECTS\ACTIVE\" 2>nul
move "*Project*" "PROJECTS\ACTIVE\" 2>nul

REM Move tool-related files
echo Moving tool files...
move "*tool*" "TOOLS\" 2>nul
move "*TOOL*" "TOOLS\" 2>nul
move "*Tool*" "TOOLS\" 2>nul

REM Move media files
echo Moving media files...
move "*.jpg" "MEDIA\" 2>nul
move "*.jpeg" "MEDIA\" 2>nul
move "*.png" "MEDIA\" 2>nul
move "*.gif" "MEDIA\" 2>nul
move "*.mp4" "MEDIA\" 2>nul
move "*.mp3" "MEDIA\" 2>nul
move "*.wav" "MEDIA\" 2>nul
move "*.mov" "MEDIA\" 2>nul

REM Move temporary files
echo Moving temporary files...
move "*temp*" "TEMP\" 2>nul
move "*TEMP*" "TEMP\" 2>nul
move "*Temp*" "TEMP\" 2>nul
move "*tmp*" "TEMP\" 2>nul
move "*TMP*" "TEMP\" 2>nul

REM Move JSON, YAML, and other config files
echo Moving remaining configuration files...
move "*.json" "CONFIG\" 2>nul
move "*.yaml" "CONFIG\" 2>nul
move "*.yml" "CONFIG\" 2>nul
move "*.conf" "CONFIG\" 2>nul
move "*.ini" "CONFIG\" 2>nul

echo Organization of C:\Users\karma directory complete.
echo Please review the new structure and verify all files are in appropriate locations.
echo Remember to check that all tools and scripts still function correctly with the new file locations.