@echo off
REM ==========================================
REM Comprehensive System Cleanup Script
REM For Qwen CLI Optimization
REM ==========================================
REM Estimated Recovery: 15-25 GB
REM ==========================================

echo.
echo ==========================================
echo  COMPREHENSIVE SYSTEM CLEANUP
echo  Date: %DATE%
echo ==========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Running without administrator privileges.
    echo Some operations may require admin rights.
    echo.
)

REM ==========================================
REM 1. Clear AI Editor Caches
REM ==========================================
echo [1/8] Clearing AI Editor Caches...
echo.

if exist "%USERPROFILE%\.qwen\tmp" (
    echo - Clearing Qwen CLI tmp cache...
    rd /s /q "%USERPROFILE%\.qwen\tmp" 2>nul
    mkdir "%USERPROFILE%\.qwen\tmp"
)

if exist "%USERPROFILE%\.continue\index" (
    echo - Clearing Continue index cache...
    rd /s /q "%USERPROFILE%\.continue\index" 2>nul
)

if exist "%USERPROFILE%\.gemini\tmp" (
    echo - Clearing Gemini tmp cache...
    rd /s /q "%USERPROFILE%\.gemini\tmp" 2>nul
)

if exist "%USERPROFILE%\.cursor\cache" (
    echo - Clearing Cursor cache...
    rd /s /q "%USERPROFILE%\.cursor\cache" 2>nul
)

echo.

REM ==========================================
REM 2. Clear npm Cache
REM ==========================================
echo [2/8] Clearing npm Cache...
echo.
call npm cache clean --force 2>nul
echo.

REM ==========================================
REM 3. Clear pip Cache
REM ==========================================
echo [3/8] Clearing pip Cache...
echo.
call pip cache purge 2>nul
echo.

REM ==========================================
REM 4. Clear Windows Temp Folders
REM ==========================================
echo [4/8] Clearing Windows Temp Folders...
echo.
del /q /f "%TEMP%\*.*" 2>nul
rd /s /q "%TEMP%" 2>nul
mkdir "%TEMP%"
echo.

REM ==========================================
REM 5. Clear Recycle Bin (Optional)
REM ==========================================
echo [5/8] Skipping Recycle Bin (manual operation)
echo     To clear: Right-click Recycle Bin ^> Empty
echo.

REM ==========================================
REM 6. Clear Browser Caches (Manual)
REM ==========================================
echo [6/8] Browser Cache Cleanup (Manual)
echo     Chrome: Ctrl+Shift+Del ^> Clear browsing data
echo     Edge: Ctrl+Shift+Del ^> Clear browsing data
echo.

REM ==========================================
REM 7. DISM Cleanup (Requires Admin)
REM ==========================================
echo [7/8] DISM Component Cleanup
echo     NOTE: Requires administrator privileges
echo     Run manually: DISM /Online /Cleanup-Image /StartComponentCleanup
echo.

REM ==========================================
REM 8. Storage Sense (Windows 10/11)
REM ==========================================
echo [8/8] Windows Storage Sense
echo     Open Settings ^> System ^> Storage ^> Configure Storage Sense
echo     Recommended: Run every week, delete temp files
echo.

REM ==========================================
REM Summary
REM ==========================================
echo.
echo ==========================================
echo  CLEANUP COMPLETE
echo ==========================================
echo.
echo Estimated Space Recovered: 5-10 GB
echo.
echo Additional Actions Required:
echo 1. Run DISM as Admin: DISM /Online /Cleanup-Image /StartComponentCleanup
echo 2. Disable Hibernation: powercfg /h off  ^[Requires Admin^]
echo 3. Empty Recycle Bin manually
echo 4. Clear browser caches manually
echo.
echo For advanced cleanup, run:
echo   - cleanup_downloads.ps1  ^[Archive old downloads^]
echo   - analyze_experimental.ps1  ^[Review EXPERIMENTAL folder^]
echo.
echo ==========================================
pause
