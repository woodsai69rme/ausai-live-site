@echo off
setlocal

echo ===========================================================
echo   Aggressive shell repair (taskbar + Start menu both gone)
echo ===========================================================
echo   This calls cvd_repair_shell.ps1 which:
echo     * ends transl/startallback/displayfusion
echo     * hard-kills explorer.exe
echo     * resets StartMenuExperienceHost / ShellExperienceHost /
echo       SearchApp / Cortana via Reset-AppxPackage
echo     * re-launches explorer.exe
echo     * verifies Shell_TrayWnd is visible
echo.
echo   REQUIRES an elevated (Run-as-administrator) PowerShell.
echo ===========================================================

REM NET SESSION is the right cmd-only elevation detector: it succeeds ONLY
REM when this process is running with a real Administrator token, not just
REM an un-elevated token from a member of Administrators group. (We
REM deliberately don't use `whoami /groups` + findstr here because the SID
REM is printed on a separate line from the name and string-mismatch any
REM naive filter.)
net session >nul 2>&1
if errorlevel 1 (
    echo Not elevated -- re-launching self as Administrator...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -Wait"
    exit /b 0
)

set "PS1=%~dp0cvd_repair_shell.ps1"
echo Running elevated.    Path: %PS1%
echo.

REM We are already elevated; no further UAC prompt needed.
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
if errorlevel 1 (
    echo.
    echo   Script reported an error. See above.
    pause
    exit /b 1
)
echo.
echo Done. Check the desktop for the taskbar and Start menu.
pause
endlocal
