@echo off
REM Organization script for X: drive
REM This script organizes the X: drive according to the organization plan

echo Starting organization of X: drive...
echo Checking if X: drive is available...

REM Check if X: drive exists
if not exist "X:\" (
    echo ERROR: X: drive not found. Please ensure the drive is connected and accessible.
    pause
    exit /b 1
)

echo X: drive found. Proceeding with organization...

REM Change to X: drive
X:

echo Creating new directory structure on X: drive...

REM Create main directories
if not exist "AI_MODELS\LMSTUDIO_MODELS" mkdir "AI_MODELS\LMSTUDIO_MODELS"
if not exist "AI_MODELS\OLLAMA_MODELS" mkdir "AI_MODELS\OLLAMA_MODELS"
if not exist "AI_MODELS\MODEL_SCRIPTS" mkdir "AI_MODELS\MODEL_SCRIPTS"

if not exist "DEVELOPMENT\ENVIRONMENTS" mkdir "DEVELOPMENT\ENVIRONMENTS"
if not exist "DEVELOPMENT\ACTIVE_PROJECTS" mkdir "DEVELOPMENT\ACTIVE_PROJECTS"
if not exist "DEVELOPMENT\ARCHIVED_PROJECTS" mkdir "DEVELOPMENT\ARCHIVED_PROJECTS"
if not exist "DEVELOPMENT\BACKUPS" mkdir "DEVELOPMENT\BACKUPS"

if not exist "CONTENT_CREATION\DOCUMENTS" mkdir "CONTENT_CREATION\DOCUMENTS"
if not exist "CONTENT_CREATION\MEDIA" mkdir "CONTENT_CREATION\MEDIA"
if not exist "CONTENT_CREATION\DOWNLOADS" mkdir "CONTENT_CREATION\DOWNLOADS"

if not exist "TOOLS\AUTOMATION" mkdir "TOOLS\AUTOMATION"
if not exist "TOOLS\AI_MANAGEMENT" mkdir "TOOLS\AI_MANAGEMENT"
if not exist "TOOLS\UTILITIES" mkdir "TOOLS\UTILITIES"

if not exist "VIRTUAL_MACHINES" mkdir "VIRTUAL_MACHINES"
if not exist "ARCHIVES" mkdir "ARCHIVES"
if not exist "TEMP" mkdir "TEMP"

echo Created directory structure on X: drive.

REM Move existing AI model directories to new structure
echo Moving AI model directories...
if exist "AI_MODELS\LMStudioModels" robocopy "AI_MODELS\LMStudioModels" "AI_MODELS\LMSTUDIO_MODELS" /E /MOVE
if exist "AI_MODELS\OllamaModels" robocopy "AI_MODELS\OllamaModels" "AI_MODELS\OLLAMA_MODELS" /E /MOVE
if exist "AI_MODELS\model-management-scripts" robocopy "AI_MODELS\model-management-scripts" "AI_MODELS\MODEL_SCRIPTS" /E /MOVE

REM Move development environments
echo Moving development environments...
if exist "DEVELOPMENT_ENVIRONMENTS\CODENV" robocopy "DEVELOPMENT_ENVIRONMENTS\CODENV" "DEVELOPMENT\ENVIRONMENTS" /E /MOVE
if exist "DEVELOPMENT_ENVIRONMENTS\venv" robocopy "DEVELOPMENT_ENVIRONMENTS\venv" "DEVELOPMENT\ENVIRONMENTS" /MOVE

REM Move projects to appropriate categories
echo Moving projects...
if exist "projects\ACTIVE" robocopy "projects\ACTIVE" "DEVELOPMENT\ACTIVE_PROJECTS" /E /MOVE
if exist "projects\ARCHIVED" robocopy "projects\ARCHIVED" "DEVELOPMENT\ARCHIVED_PROJECTS" /E /MOVE
if exist "projects\BACKUPS" robocopy "projects\BACKUPS" "DEVELOPMENT\BACKUPS" /E /MOVE

REM Move content to new structure
echo Moving content files...
if exist "CONTENT\DOCUMENTS" robocopy "CONTENT\DOCUMENTS" "CONTENT_CREATION\DOCUMENTS" /E /MOVE
if exist "CONTENT\MEDIA" robocopy "CONTENT\MEDIA" "CONTENT_CREATION\MEDIA" /E /MOVE
if exist "CONTENT\DOWNLOADS" robocopy "CONTENT\DOWNLOADS" "CONTENT_CREATION\DOWNLOADS" /E /MOVE

REM Move tools to appropriate categories
echo Moving tools...
if exist "TOOLS\automation-scripts" robocopy "TOOLS\automation-scripts" "TOOLS\AUTOMATION" /E /MOVE
if exist "TOOLS\model-managers" robocopy "TOOLS\model-managers" "TOOLS\AI_MANAGEMENT" /E /MOVE

REM Move large VM files to VIRTUAL_MACHINES (if they exist in root)
echo Moving virtual machine files...
if exist "*.vdi" move "*.vdi" "VIRTUAL_MACHINES\" 2>nul
if exist "*.ova" move "*.ova" "VIRTUAL_MACHINES\" 2>nul
if exist "*.iso" move "*.iso" "VIRTUAL_MACHINES\" 2>nul
if exist "*.vmdk" move "*.vmdk" "VIRTUAL_MACHINES\" 2>nul

REM Move archive-type directories
echo Moving archive directories...
if exist "BU" robocopy "BU" "ARCHIVES" /E /MOVE
if exist "claudebu" robocopy "claudebu" "ARCHIVES" /E /MOVE
if exist "Claude_Backup_" robocopy "Claude_Backup_" "ARCHIVES" /E /MOVE
if exist "project_backup_*" robocopy "project_backup_*" "ARCHIVES" /E /MOVE

echo Organization of X: drive complete.
echo Please review the new structure and verify all files are in appropriate locations.
echo Note: Large files like VM images may take additional time to move completely.
echo Remember to update any scripts or applications that reference the old file locations.