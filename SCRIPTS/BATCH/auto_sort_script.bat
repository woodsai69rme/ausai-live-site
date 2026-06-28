@echo off
REM Auto-sort script for incoming files
REM This script sorts files in the Downloads folder to appropriate organized directories

echo Auto-sorting files to organized directories...
echo =============================================

REM Create timestamp for logging
set TIMESTAMP=%DATE:~-4%_%DATE:~4,2%_%DATE:~7,2%_%TIME:~0,2%_%TIME:~3,2%_%TIME:~6,2%

REM Sort files from Downloads to appropriate directories
echo Sorting Downloads...

REM Create temp directory for processing if it doesn't exist
if not exist "%USERPROFILE%\Downloads\processed" mkdir "%USERPROFILE%\Downloads\processed"

REM Move different file types to appropriate organized directories
echo Moving documents to DOCUMENTATION...
for %%f in ("%USERPROFILE%\Downloads\*.pdf") do (
    if exist "C:\Users\karma\DOCUMENTATION" (
        move "%%f" "C:\Users\karma\DOCUMENTATION" 2>nul
    )
)

for %%f in ("%USERPROFILE%\Downloads\*.doc", "%USERPROFILE%\Downloads\*.docx", "%USERPROFILE%\Downloads\*.txt", "%USERPROFILE%\Downloads\*.rtf") do (
    if exist "C:\Users\karma\DOCUMENTATION" (
        move "%%f" "C:\Users\karma\DOCUMENTATION" 2>nul
    )
)

for %%f in ("%USERPROFILE%\Downloads\*.md") do (
    if exist "C:\Users\karma\DOCUMENTATION" (
        move "%%f" "C:\Users\karma\DOCUMENTATION" 2>nul
    )
)

echo Moving images to MEDIA...
for %%f in ("%USERPROFILE%\Downloads\*.jpg", "%USERPROFILE%\Downloads\*.jpeg", "%USERPROFILE%\Downloads\*.png", "%USERPROFILE%\Downloads\*.gif", "%USERPROFILE%\Downloads\*.bmp", "%USERPROFILE%\Downloads\*.svg") do (
    if exist "C:\Users\karma\MEDIA" (
        move "%%f" "C:\Users\karma\MEDIA" 2>nul
    )
)

echo Moving videos to MEDIA...
for %%f in ("%USERPROFILE%\Downloads\*.mp4", "%USERPROFILE%\Downloads\*.avi", "%USERPROFILE%\Downloads\*.mov", "%USERPROFILE%\Downloads\*.wmv", "%USERPROFILE%\Downloads\*.mkv") do (
    if exist "C:\Users\karma\MEDIA" (
        move "%%f" "C:\Users\karma\MEDIA" 2>nul
    )
)

echo Moving audio to MEDIA...
for %%f in ("%USERPROFILE%\Downloads\*.mp3", "%USERPROFILE%\Downloads\*.wav", "%USERPROFILE%\Downloads\*.flac", "%USERPROFILE%\Downloads\*.aac") do (
    if exist "C:\Users\karma\MEDIA" (
        move "%%f" "C:\Users\karma\MEDIA" 2>nul
    )
)

echo Moving scripts to SCRIPTS...
for %%f in ("%USERPROFILE%\Downloads\*.py", "%USERPROFILE%\Downloads\*.js", "%USERPROFILE%\Downloads\*.bat", "%USERPROFILE%\Downloads\*.sh", "%USERPROFILE%\Downloads\*.ts", "%USERPROFILE%\Downloads\*.tsx") do (
    if exist "C:\Users\karma\SCRIPTS" (
        move "%%f" "C:\Users\karma\SCRIPTS" 2>nul
    )
)

echo Moving executables and archives to TOOLS...
for %%f in ("%USERPROFILE%\Downloads\*.exe", "%USERPROFILE%\Downloads\*.msi", "%USERPROFILE%\Downloads\*.zip", "%USERPROFILE%\Downloads\*.rar", "%USERPROFILE%\Downloads\*.7z", "%USERPROFILE%\Downloads\*.tar", "%USERPROFILE%\Downloads\*.gz") do (
    if exist "C:\Users\karma\TOOLS" (
        move "%%f" "C:\Users\karma\TOOLS" 2>nul
    )
)

REM Move processed files to temporary folder to prevent re-processing
for %%f in ("%USERPROFILE%\Downloads\*.*") do (
    if not exist "%USERPROFILE%\Downloads\processed\%%~nxf" (
        move "%%f" "%USERPROFILE%\Downloads\processed" 2>nul
    )
)

REM Clean up the processed folder after moving files to organized directories
rmdir /s /q "%USERPROFILE%\Downloads\processed" 2>nul

echo.
echo Auto-sorting completed.
echo Files have been moved to their appropriate organized directories.
echo.
echo Remember to check the directories to ensure files were sorted correctly.
echo You may need to manually adjust some files that didn't match the criteria.

pause