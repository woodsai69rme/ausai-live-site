@echo off
setlocal
echo ===========================================================
echo   CRD Manager -- launching WinForms GUI.
echo ===========================================================
echo.
echo   - Status / path panel refreshes from chromoting service.
echo   - Start / Stop / Restart need an elevated token;
echo     right-click this .bat and "Run as administrator" if
echo     service-control actions return "Access is denied".
echo   - The watchdog log opens in Notepad if present.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%~dp0crd_manager.ps1" %*
if errorlevel 1 (
    echo.
    echo   GUI exited with error code %errorlevel%.
    pause
    exit /b 1
)
endlocal
