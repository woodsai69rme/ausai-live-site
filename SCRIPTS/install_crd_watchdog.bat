@echo off
setlocal

echo ===========================================================
echo   CRD AutoStart Watchdog -- installer
echo ===========================================================
echo   This creates a SYSTEM-elevated scheduled task that runs
echo   every 5 minutes and re-asserts:
echo       sc.exe config chromoting start= auto
echo   so the auto-start value cannot silently regress.
echo.
echo   REQUIRES an elevated (Administrator) cmd window.
echo   If you launched this from File Explorer, right-click and
echo   "Run as administrator" instead.
echo ===========================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_crd_watchdog.ps1"
if errorlevel 1 (
    echo.
    echo   Registration did not complete.
    echo   Most likely cause: this window was not elevated.
    echo   Retry: right-click this .bat and choose "Run as administrator".
    exit /b 1
)

echo.
echo ===========================================================
echo   Verifying:
echo ===========================================================
schtasks /query /tn "CRD AutoStart Watchdog" /v /fo LIST
echo.
echo To remove later:
echo   schtasks /delete /tn "CRD AutoStart Watchdog" /f
echo   -- or run scripts\remove_crd_watchdog.bat
echo.
endlocal
