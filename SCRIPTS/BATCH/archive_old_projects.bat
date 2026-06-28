@echo off
REM Project archiving script
REM Identifies and moves old projects to archived directories

echo Scanning for projects to archive...
echo ================================

REM Check for old projects in C:\Users\karma\PROJECTS\ACTIVE
echo Checking C:\Users\karma\PROJECTS\ACTIVE for projects older than 90 days...
for /f "delims=" %%i in ('powershell "Get-ChildItem -Path 'C:\Users\karma\PROJECTS\ACTIVE' -Directory | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-90)} | Select-Object -ExpandProperty FullName"') do (
    echo Found old project: %%~nxi
    set /p CONFIRM="Do you want to archive this project? (y/n): "
    if /i "!CONFIRM!"=="y" (
        if exist "C:\Users\karma\PROJECTS\ARCHIVED" (
            move "%%i" "C:\Users\karma\PROJECTS\ARCHIVED" 2>nul
            if !ERRORLEVEL! equ 0 (
                echo Project moved to archive: %%~nxi
            ) else (
                echo Failed to move project: %%~nxi
            )
        ) else (
            echo Archive directory does not exist: C:\Users\karma\PROJECTS\ARCHIVED
        )
    )
)

echo.
REM Check for old projects in X:\DEVELOPMENT\ACTIVE_PROJECTS
echo Checking X:\DEVELOPMENT\ACTIVE_PROJECTS for projects older than 90 days...
for /f "delims=" %%i in ('powershell "Get-ChildItem -Path 'X:\DEVELOPMENT\ACTIVE_PROJECTS' -Directory | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-90)} | Select-Object -ExpandProperty FullName"') do (
    echo Found old project: %%~nxi
    set /p CONFIRM="Do you want to archive this project? (y/n): "
    if /i "!CONFIRM!"=="y" (
        if exist "X:\DEVELOPMENT\ARCHIVED_PROJECTS" (
            move "%%i" "X:\DEVELOPMENT\ARCHIVED_PROJECTS" 2>nul
            if !ERRORLEVEL! equ 0 (
                echo Project moved to archive: %%~nxi
            ) else (
                echo Failed to move project: %%~nxi
            )
        ) else (
            echo Archive directory does not exist: X:\DEVELOPMENT\ARCHIVED_PROJECTS
        )
    )
)

echo.
echo Project archiving scan completed.
echo.
echo Note: Projects are considered old if they haven't been modified in the last 90 days.
echo Adjust the day count in the script if you want a different timeframe.

pause