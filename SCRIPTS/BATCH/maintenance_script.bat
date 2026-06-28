@echo off
REM Maintenance script for organized drives
REM Performs regular cleanup, monitoring, and maintenance tasks

echo Running system maintenance for organized drives...
echo ===============================================

REM Clean up temporary files in TEMP directories
echo Cleaning TEMP directories...
if exist "C:\Users\karma\TEMP" (
    del /q "C:\Users\karma\TEMP\*" 2>nul
    echo Cleaned C:\Users\karma\TEMP
)

if exist "X:\TEMP" (
    del /q "X:\TEMP\*" 2>nul
    echo Cleaned X:\TEMP
)

REM Check disk space
echo.
echo Checking disk space...
echo C: drive:
dir "C:\" /-C | find "bytes"
echo.
echo X: drive:
dir "X:\" /-C | find "bytes"

REM Archive old files in projects (optional - uncomment to enable)
REM echo Archiving old projects...
REM powershell "Get-ChildItem 'X:\DEVELOPMENT\ACTIVE_PROJECTS' -Directory | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Move-Item -Destination 'X:\DEVELOPMENT\ARCHIVED_PROJECTS'"

echo.
echo Maintenance tasks completed.
echo.
echo Recommendations:
echo 1. Review the PROJECTS directory for any projects that can be archived
echo 2. Check the MEDIA directory for any large files that could be compressed
echo 3. Verify that all new files are being placed in appropriate directories
echo 4. Consider backing up critical directories if not already done

pause