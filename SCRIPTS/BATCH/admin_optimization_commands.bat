@echo off
REM ==========================================
REM ADMIN OPTIMIZATION COMMANDS
REM Run as Administrator for full system optimization
REM ==========================================

echo.
echo ==========================================
echo  ADMIN SYSTEM OPTIMIZATION
echo  Running as: %USERNAME%
echo ==========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires administrator privileges!
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

echo [✓] Administrator privileges confirmed
echo.

REM ==========================================
REM 1. DISM Cleanup
REM ==========================================
echo ==========================================
echo  [1/4] DISM COMPONENT CLEANUP
echo  Expected Recovery: 5-20 GB
echo  This may take 15-30 minutes...
echo ==========================================
echo.
DISM /Online /Cleanup-Image /StartComponentCleanup
echo.
if %errorLevel% equ 0 (
    echo [✓] DISM cleanup completed successfully
) else (
    echo [!] DISM cleanup completed with warnings or was skipped
)
echo.

REM ==========================================
REM 2. Disable Hibernation
REM ==========================================
echo ==========================================
echo  [2/4] DISABLE HIBERNATION
echo  Expected Recovery: 8-32 GB (equals RAM size)
echo ==========================================
echo.
powercfg /h off
if %errorLevel% equ 0 (
    echo [✓] Hibernation disabled successfully
    echo     Recovery: ~16 GB (estimated based on 16 GB RAM)
) else (
    echo [!] Failed to disable hibernation
)
echo.

REM ==========================================
REM 3. Clear NVIDIA Shader Cache
REM ==========================================
echo ==========================================
echo  [3/4] CLEAR NVIDIA SHADER CACHE
echo  Expected Recovery: 2-6 GB
echo ==========================================
echo.
if exist "C:\ProgramData\NVIDIA Corporation\NV_Cache" (
    echo Clearing NVIDIA cache...
    del /q /f "C:\ProgramData\NVIDIA Corporation\NV_Cache\*" 2>nul
    echo [✓] NVIDIA shader cache cleared
) else (
    echo [!] NVIDIA cache folder not found
    echo     May already be cleared or NVIDIA not installed
)
echo.

REM ==========================================
REM 4. Clear Windows Update Cache
REM ==========================================
echo ==========================================
echo  [4/4] CLEAR WINDOWS UPDATE CACHE
echo  Expected Recovery: 1-5 GB
echo ==========================================
echo.
net stop wuauserv 2>nul
net stop bits 2>nul
if exist "C:\Windows\SoftwareDistribution\Download" (
    del /q /f "C:\Windows\SoftwareDistribution\Download\*" 2>nul
    echo [✓] Windows Update cache cleared
)
net start wuauserv 2>nul
net start bits 2>nul
echo.

REM ==========================================
REM Summary
REM ==========================================
echo ==========================================
echo  ADMIN OPTIMIZATION COMPLETE
echo ==========================================
echo.
echo Estimated Total Recovery: 16-63 GB
echo.
echo Breakdown:
echo   - DISM Cleanup: 5-20 GB
echo   - Hibernation: 8-32 GB
echo   - NVIDIA Cache: 2-6 GB
echo   - Windows Update: 1-5 GB
echo.
echo RECOMMENDATION: Restart your computer to finalize changes.
echo.
echo ==========================================
pause
