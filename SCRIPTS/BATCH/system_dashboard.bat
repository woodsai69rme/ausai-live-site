@echo off
REM Dashboard script for organized drives
REM Provides an overview of the organized system status

echo ===============================================
echo       Organized Drive System Dashboard
echo ===============================================
echo.

echo C:\Users\karma Status:
echo ----------------------
if exist "C:\Users\karma\CONFIG" (
    for /f %%a in ('dir "C:\Users\karma\CONFIG" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo CONFIG directory: Exists - !COUNT! items
) else (
    echo CONFIG directory: Missing
)

if exist "C:\Users\karma\PROJECTS" (
    for /f %%a in ('dir "C:\Users\karma\PROJECTS" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo PROJECTS directory: Exists - !COUNT! items
) else (
    echo PROJECTS directory: Missing
)

if exist "C:\Users\karma\DOCUMENTATION" (
    for /f %%a in ('dir "C:\Users\karma\DOCUMENTATION" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo DOCUMENTATION directory: Exists - !COUNT! items
) else (
    echo DOCUMENTATION directory: Missing
)

if exist "C:\Users\karma\SCRIPTS" (
    for /f %%a in ('dir "C:\Users\karma\SCRIPTS" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo SCRIPTS directory: Exists - !COUNT! items
) else (
    echo SCRIPTS directory: Missing
)

if exist "C:\Users\karma\AI_TOOLS" (
    for /f %%a in ('dir "C:\Users\karma\AI_TOOLS" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo AI_TOOLS directory: Exists - !COUNT! items
) else (
    echo AI_TOOLS directory: Missing
)

if exist "C:\Users\karma\TEMP" (
    for /f %%a in ('dir "C:\Users\karma\TEMP" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo TEMP directory: Exists - !COUNT! items (consider cleaning)
) else (
    echo TEMP directory: Missing
)

echo.
echo X: Drive Status:
echo ----------------
if exist "X:\AI_MODELS" (
    for /f %%a in ('dir "X:\AI_MODELS" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo AI_MODELS directory: Exists - !COUNT! items
) else (
    echo AI_MODELS directory: Missing
)

if exist "X:\DEVELOPMENT" (
    for /f %%a in ('dir "X:\DEVELOPMENT" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo DEVELOPMENT directory: Exists - !COUNT! items
) else (
    echo DEVELOPMENT directory: Missing
)

if exist "X:\CONTENT_CREATION" (
    for /f %%a in ('dir "X:\CONTENT_CREATION" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo CONTENT_CREATION directory: Exists - !COUNT! items
) else (
    echo CONTENT_CREATION directory: Missing
)

if exist "X:\TOOLS" (
    for /f %%a in ('dir "X:\TOOLS" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo TOOLS directory: Exists - !COUNT! items
) else (
    echo TOOLS directory: Missing
)

if exist "X:\VIRTUAL_MACHINES" (
    for /f %%a in ('dir "X:\VIRTUAL_MACHINES" /s /b ^| find /c /v ""') do set COUNT=%%a
    echo VIRTUAL_MACHINES directory: Exists - !COUNT! items
) else (
    echo VIRTUAL_MACHINES directory: Missing
)

echo.
echo Disk Space Information:
echo -----------------------
echo C: Drive:
dir "C:\" /-C | find "bytes"
echo.
echo X: Drive:
dir "X:\" /-C | find "bytes"

echo.
echo Available Maintenance Scripts:
echo ------------------------------
echo 1. maintenance_script.bat - Regular cleanup and monitoring
echo 2. auto_sort_script.bat - Sort files from Downloads to organized directories
echo 3. archive_old_projects.bat - Identify and archive old projects
echo 4. This dashboard script - View system status

echo.
echo Recommendations:
echo - Run maintenance_script.bat regularly
echo - Use auto_sort_script.bat for incoming files
echo - Periodically run archive_old_projects.bat
echo - Review and clean TEMP directories monthly

pause