@echo off
setlocal
set "TASK_NAME=AI Influencer Studio Model Catalog"
set "RUNNER=%~dp0refresh_model_catalog_daily.bat"
set "AISOCIAL=%APPDATA%\Python\Python313\Scripts\aisocial.exe"

if not exist "%AISOCIAL%" (
    where aisocial >nul 2>&1
    if errorlevel 1 (
        echo aisocial was not found. Install the project or add its Scripts directory to PATH.
        exit /b 1
    )
)

schtasks /Create /SC DAILY /TN "%TASK_NAME%" /TR "\"%RUNNER%\"" /ST 03:00 /F
if errorlevel 1 (
    echo Failed to register the daily model catalog task.
    exit /b 1
)

echo Registered "%TASK_NAME%" to run daily at 03:00.
endlocal
exit /b 0
