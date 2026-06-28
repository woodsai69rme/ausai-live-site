@echo off
setlocal EnableExtensions

REM ===============================================================
REM  cvd_recover.bat -- minimal, idempotent recovery
REM  Re-run-safe. Does NOT kill explorer. Only starts it if missing.
REM  Designed for chrome-remote-desktop connectivity.
REM ===============================================================

echo.
echo ============================================================
echo   STEP A -- Is explorer.exe alive?
echo ============================================================
tasklist /fi "imagename eq explorer.exe" 2>nul | find /i "explorer.exe" >nul
if errorlevel 1 (
    echo   explorer.exe is NOT running. Starting it now (no kill needed).
    start "" explorer.exe
    timeout /t 6 /nobreak >nul
    tasklist /fi "imagename eq explorer.exe" 2>nul | find /i "explorer.exe" >nul
    if errorlevel 1 (
        echo   ERROR: explorer failed to relaunch. Try Alt+Tab or open Task Manager.
        exit /b 1
    ) else (
        echo   explorer.exe relaunched OK.
    )
) else (
    echo   explorer.exe is running.
)

echo.
echo ============================================================
echo   STEP B -- Force taskbar visibility flags (idempotent)
echo ============================================================
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAutoHide    /t REG_DWORD /d 0 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v MMTaskbarEnabled /t REG_DWORD /d 1 /f
echo   TaskbarAutoHide=0, MMTaskbarEnabled=1 written.

REM If StuckRects3 is missing AND explorer is now alive, explorer will
REM regenerate it on its own with default bottom placement. Nothing
REM to delete here -- that may have already been cleared by the
REM earlier run and a missing value is the desired clean slate.

echo.
echo ============================================================
echo   STEP C -- Final verification
echo ============================================================
echo --- CRD service ---
sc query chromoting | findstr /B /C:"        STATE" /C:"        TYPE"

echo.
echo --- explorer.exe ---
tasklist /fi "imagename eq explorer.exe" | findstr /I explorer.exe

echo.
echo --- Taskbar flag values ---
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAutoHide
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v MMTaskbarEnabled

echo.
echo --- StuckRects3 (explorer auto-creates this on first start) ---
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3" /v Settings 2>nul
if errorlevel 1 (
    echo   (StuckRects3 not yet present -- it will appear at next logon/explorer rebuild)
)

echo.
echo ============================================================
echo   Done. Taskbar should now be visible at the bottom of the
echo   primary monitor. CRD will auto-start after every reboot.
echo ============================================================
endlocal
