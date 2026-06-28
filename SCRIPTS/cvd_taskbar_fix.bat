@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ===============================================================
REM  Chrome Remote Desktop + Taskbar fixer / verifier
REM  Safe to re-run. Designed to survive being called from bash.
REM
REM  !! WARNING -- THIS SCRIPT RESTARTS explorer.exe !!
REM    Restarting the shell closes every open File Explorer window
REM    in your session, not just the taskbar. Save any open Folder
REM    views first if you care about them. CRD STAYS CONNECTED
REM    because it runs as a SYSTEM service, independent of explorer.
REM
REM  For a non-destructive alternative that does NOT kill explorer,
REM  use  cvd_recover.bat  instead.
REM ===============================================================

echo.
echo ============================================================
echo   STEP 1 -- Chrome Remote Desktop service state
echo ============================================================
sc query chromoting
echo.
echo --- Startup configuration (BINARY_PATH_NAME / START_TYPE) ---
sc qc chromoting
echo.
echo --- Service startup configuration (START_TYPE / BINARY_PATH_NAME) ---
REM Use delims=':' so we can fetch everything after the first colon cleanly,
REM stripping the parenthesis / stray leading whitespace. (Avoid the
REM 'tokens=2,*' / 'tokens=3,*' trap -- reviewer's note #2.)
for /f "tokens=2 delims=:" %%a in ('sc qc chromoting ^| findstr /B /C:"        BINARY_PATH_NAME"') do (
    for /f "tokens=*" %%b in ("%%a") do set "CRD_BIN=%%b"
)
echo CRD service binary path: !CRD_BIN!
if exist "!CRD_BIN!" (
    echo   EXISTS: yes
) else (
    echo   EXISTS: NO   -- service registration is misconfigured; reinstall Chrome Remote Desktop host
)
echo.

echo ============================================================
echo   STEP 2 -- Taskbar CURRENT registry state (before fix)
echo ============================================================
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAutoHide
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v MMTaskbarEnabled
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarSd
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3" /v Settings

echo.
echo ============================================================
echo   STEP 3 -- Apply fix
echo   - TaskbarAutoHide  = 0  (visible, never auto-hide)
echo   - StuckRects3 / StuckRects2 cleared -> explorer rebuilds
echo     the bar at the bottom of the primary monitor.
echo ============================================================
reg add    "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAutoHide    /t REG_DWORD /d 0 /f
reg add    "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v MMTaskbarEnabled /t REG_DWORD /d 1 /f
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3" /v Settings /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects2" /v Settings /f 2>nul
echo Registry patched.

echo.
echo ============================================================
echo   STEP 4 -- Restart Windows Explorer (task-safe -- CRD stays up)
echo ============================================================
echo Killing explorer.exe... (Desktop will flicker briefly, then return.)
taskkill /IM explorer.exe /F >nul 2>&1
ping -n 3 127.0.0.1 >nul
echo Starting explorer.exe...
start "" explorer.exe
ping -n 4 127.0.0.1 >nul
echo Explorer restarted.

echo.
echo ============================================================
echo   STEP 5 -- POST-fix registry state
echo ============================================================
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAutoHide
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v MMTaskbarEnabled
echo.
echo StuckRects3 after fix (explorer recreates here on first launch):
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3" /v Settings

echo.
echo ============================================================
echo   STEP 6 -- CRD service still healthy?
echo ============================================================
sc query chromoting

echo.
echo ============================================================
echo   Done. Your taskbar should be visible again. If you reboot
echo   the machine, the Chrome Remote Desktop service will come
echo   back automatically and you can reconnect the same way.
echo ============================================================
endlocal
