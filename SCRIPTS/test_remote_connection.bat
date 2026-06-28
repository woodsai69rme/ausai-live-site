@echo off
setlocal
echo ===========================================================
echo   Chrome Remote Desktop  -  Readiness Probe
echo   (read-only, no elevation required)
echo ===========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_remote_connection.ps1" %*
set "RC=%errorlevel%"

echo.
echo ===========================================================
echo   Probe finished. Exit code: %RC%
echo   0 = ready    non-zero = see findings above
echo ===========================================================
exit /b %RC%
