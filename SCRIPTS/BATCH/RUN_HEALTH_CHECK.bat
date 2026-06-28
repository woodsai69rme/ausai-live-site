@echo off
REM AI Applications Suite - System Health Check
REM This script performs a comprehensive health check of the system

setlocal

REM Set the script directory
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

echo.
echo =====================================================
echo AI Applications Suite - System Health Check
echo =====================================================
echo.

echo Performing system health check...
echo.

REM Check Python installation
echo 1. Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Python is not installed or not in PATH
    set PYTHON_OK=false
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo    OK: %PYTHON_VERSION%
    set PYTHON_OK=true
)
echo.

REM Check required packages
echo 2. Checking required packages...
set PACKAGES_CHECKED=0
set PACKAGES_MISSING=0

for %%p in (speech_recognition, pyttsx3, requests, cryptography, psutil, sqlite3) do (
    set /a PACKAGES_CHECKED+=1
    python -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        echo    MISSING: %%p
        set /a PACKAGES_MISSING+=1
    ) else (
        echo    OK: %%p
    )
)
echo.

REM Check audio libraries
echo 3. Checking audio libraries...
python -c "import pyaudio" >nul 2>&1
if errorlevel 1 (
    echo    WARNING: PyAudio not found (needed for speech recognition)
    set PYAUDIO_OK=false
) else (
    echo    OK: PyAudio is installed
    set PYAUDIO_OK=true
)
echo.

REM Check application directories
echo 4. Checking application directories...
set APPS_CHECKED=0
set APPS_MISSING=0

for %%d in ("github-repo-downloader", "chatgpt-sorter", "ai-voice-assistant", "ai-voice-assistant-enhanced") do (
    set /a APPS_CHECKED+=1
    if exist "C:\Users\karma\%%~d" (
        echo    OK: %%~d directory exists
    ) else (
        echo    MISSING: %%~d directory
        set /a APPS_MISSING+=1
    )
)
echo.

REM Check configuration files
echo 5. Checking configuration files...
set CONFIGS_CHECKED=0
set CONFIGS_MISSING=0

for %%f in (
    "C:\Users\karma\ai-voice-assistant-enhanced\config.json",
    "C:\Users\karma\ai-voice-assistant-enhanced\security_config.json",
    "C:\Users\karma\github-repo-downloader\requirements.txt",
    "C:\Users\karma\chatgpt-sorter\requirements.txt",
    "C:\Users\karma\ai-voice-assistant\requirements.txt",
    "C:\Users\karma\ai-voice-assistant-enhanced\requirements.txt"
) do (
    set /a CONFIGS_CHECKED+=1
    if exist "%%f" (
        echo    OK: %%f exists
    ) else (
        echo    MISSING: %%f
        set /a CONFIGS_MISSING+=1
    )
)
echo.

REM Check executable scripts
echo 6. Checking executable scripts...
set SCRIPTS_CHECKED=0
set SCRIPTS_MISSING=0

for %%s in (
    "C:\Users\karma\START_AI_APPLICATIONS_SUITE.bat",
    "C:\Users\karma\SETUP_WIZARD.bat",
    "C:\Users\karma\github-repo-downloader\start_github_downloader.bat",
    "C:\Users\karma\chatgpt-sorter\start_chatgpt_sorter.bat",
    "C:\Users\karma\ai-voice-assistant\start_basic_assistant.bat",
    "C:\Users\karma\ai-voice-assistant-enhanced\start_enhanced_assistant.bat"
) do (
    set /a SCRIPTS_CHECKED+=1
    if exist "%%s" (
        echo    OK: %%s exists
    ) else (
        echo    MISSING: %%s
        set /a SCRIPTS_MISSING+=1
    )
)
echo.

REM Check disk space
echo 7. Checking disk space...
for /f "skip=1 tokens=2,3,4" %%a in ('wmic logicaldisk get size,freespace,caption ^| findstr C:') do (
    set TOTAL_SPACE=%%a
    set FREE_SPACE=%%b
    REM Convert to MB for easier reading
    set /a TOTAL_MB=!TOTAL_SPACE:~0,-3! / 1024 / 1024
    set /a FREE_MB=!FREE_SPACE:~0,-3! / 1024 / 1024
    echo    Total disk space: !TOTAL_MB! GB
    echo    Free disk space: !FREE_MB! GB
    if !FREE_MB! lss 500 (
        echo    WARNING: Less than 500 MB free space
    ) else (
        echo    OK: Sufficient disk space
    )
)
echo.

REM Check system resources
echo 8. Checking system resources...
python -c "import psutil; print('    CPU Usage:', psutil.cpu_percent(interval=1), '%'); print('    Memory Usage:', psutil.virtual_memory().percent, '%')" 2>nul
if errorlevel 1 (
    echo    INFO: psutil not available, skipping resource check
)
echo.

REM Generate health report
echo 9. Generating health report...
echo. > system_health_report.txt
echo AI Applications Suite - System Health Report >> system_health_report.txt
echo =========================================== >> system_health_report.txt
echo Generated on: %date% at %time% >> system_health_report.txt
echo. >> system_health_report.txt
echo Python Status: %PYTHON_VERSION% (%PYTHON_OK%) >> system_health_report.txt
echo Packages: %PACKAGES_CHECKED% checked, %PACKAGES_MISSING% missing >> system_health_report.txt
echo PyAudio: %PYAUDIO_OK% >> system_health_report.txt
echo Applications: %APPS_CHECKED% checked, %APPS_MISSING% missing >> system_health_report.txt
echo Configurations: %CONFIGS_CHECKED% checked, %CONFIGS_MISSING% missing >> system_health_report.txt
echo Scripts: %SCRIPTS_CHECKED% checked, %SCRIPTS_MISSING% missing >> system_health_report.txt
echo. >> system_health_report.txt
echo Recommendations: >> system_health_report.txt

if "%PYTHON_OK%"=="false" (
    echo - Install Python 3.8+ from python.org >> system_health_report.txt
)
if %PACKAGES_MISSING% gtr 0 (
    echo - Run 'pip install -r requirements.txt' in each application directory >> system_health_report.txt
)
if "%PYAUDIO_OK%"=="false" (
    echo - Install PyAudio: pip install pipwin && pipwin install pyaudio >> system_health_report.txt
)
if %APPS_MISSING% gtr 0 (
    echo - Verify all application directories are present >> system_health_report.txt
)
if %CONFIGS_MISSING% gtr 0 (
    echo - Verify all configuration files are present >> system_health_report.txt
)
if %SCRIPTS_MISSING% gtr 0 (
    echo - Verify all startup scripts are present >> system_health_report.txt
)

echo. >> system_health_report.txt
echo Health check completed.
echo Report saved to system_health_report.txt
echo.

REM Display summary
echo SUMMARY:
echo ========
echo Python: %PYTHON_OK%
echo Packages: %PACKAGES_MISSING% missing out of %PACKAGES_CHECKED%
echo PyAudio: %PYAUDIO_OK%
echo Applications: %APPS_MISSING% missing out of %APPS_CHECKED%
echo Configurations: %CONFIGS_MISSING% missing out of %CONFIGS_CHECKED%
echo Scripts: %SCRIPTS_MISSING% missing out of %SCRIPTS_CHECKED%
echo.

if %PACKAGES_MISSING% equ 0 if %APPS_MISSING% equ 0 if %CONFIGS_MISSING% equ 0 if %SCRIPTS_MISSING% equ 0 if "%PYTHON_OK%"=="true" (
    echo OVERALL STATUS: HEALTHY
    echo Congratulations! Your system is properly configured for the AI Applications Suite.
) else (
    echo OVERALL STATUS: NEEDS ATTENTION
    echo Please address the issues listed in the report above.
    echo Check system_health_report.txt for detailed recommendations.
)

echo.
echo Press any key to close this window...
pause >nul