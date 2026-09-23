@echo off
:: Install AI Influencer Studio scheduler as a Windows service using NSSM.
:: Run as Administrator.
:: Usage: install_windows_service.bat [path_to_python.exe]

set "SERVICE_NAME=AIInfluencerStudioScheduler"
set "PROJECT_DIR=%~dp0.."

if "%~1"=="" (
    for /f "delims=" %%P in ('where python') do set "PYTHON=%%P"
) else (
    set "PYTHON=%~1"
)

if not exist "%PYTHON%" (
    echo Python not found at "%PYTHON%". Pass the path as the first argument.
    exit /b 1
)

where nssm >nul 2>nul
if errorlevel 1 (
    echo NSSM is required but not found. Download from https://nssm.cc/
    exit /b 1
)

sc query %SERVICE_NAME% >nul 2>nul
if %errorlevel% == 0 (
    echo Service %SERVICE_NAME% already exists. Remove it first with:
    echo   sc delete %SERVICE_NAME%
    exit /b 1
)

nssm install %SERVICE_NAME% "%PYTHON%"
nssm set %SERVICE_NAME% Application "%PYTHON%"
nssm set %SERVICE_NAME% AppDirectory "%PROJECT_DIR%"
nssm set %SERVICE_NAME% AppParameters "-m ai_influencer_studio.cli daemon --interval 60"
nssm set %SERVICE_NAME% DisplayName "AI Influencer Studio Scheduler"
nssm set %SERVICE_NAME% Description "Background scheduler for AI Influencer Studio social media posts"
:: Set AISTUDIO_API_KEY here or pass it via the Windows Services UI after install.
echo Service installed. Start with: net start %SERVICE_NAME%
echo If you use AISTUDIO_API_KEY, set it via:
echo   nssm set %SERVICE_NAME% AppEnvironmentExtra "AISTUDIO_API_KEY=your-key"
pause
