@echo off
REM Master AI Applications Startup Script
REM This script allows users to select which AI application to run

setlocal

echo.
echo =====================================================
echo Welcome to the AI Applications Suite
echo =====================================================
echo.
echo Please select an application to run:
echo.
echo 1. Enhanced AI Voice Assistant (with RAG memory, computer use, browser automation)
echo 2. Basic AI Voice Assistant
echo 3. GitHub Repo Downloader
echo 4. ChatGPT Sorter
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    call :run_enhanced_assistant
) else if "%choice%"=="2" (
    call :run_basic_assistant
) else if "%choice%"=="3" (
    call :run_github_downloader
) else if "%choice%"=="4" (
    call :run_chatgpt_sorter
) else if "%choice%"=="5" (
    echo.
    echo Exiting...
    pause
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please select 1-5.
    timeout /t 2 >nul
    cls
    goto :start
)

goto :eof

:run_enhanced_assistant
cd /d "C:\Users\karma\ai-voice-assistant-enhanced"
if exist "start_enhanced_assistant.bat" (
    call start_enhanced_assistant.bat
) else (
    echo Enhanced AI Voice Assistant not found in expected location.
    pause
)
goto :eof

:run_basic_assistant
cd /d "C:\Users\karma\ai-voice-assistant"
if exist "start_basic_assistant.bat" (
    call start_basic_assistant.bat
) else (
    echo Basic AI Voice Assistant not found in expected location.
    pause
)
goto :eof

:run_github_downloader
cd /d "C:\Users\karma\github-repo-downloader"
if exist "start_github_downloader.bat" (
    call start_github_downloader.bat
) else (
    echo GitHub Repo Downloader not found in expected location.
    pause
)
goto :eof

:run_chatgpt_sorter
cd /d "C:\Users\karma\chatgpt-sorter"
if exist "start_chatgpt_sorter.bat" (
    call start_chatgpt_sorter.bat
) else (
    echo ChatGPT Sorter not found in expected location.
    pause
)
goto :eof