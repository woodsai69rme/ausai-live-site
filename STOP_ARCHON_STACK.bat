@echo off
REM ============================================================
REM  STOP_ARCHON_STACK.bat
REM  Cleanly stops Archon services (MCP :8051, archon-server :8181,
REM  agents :8052) on bare Windows (without Docker Compose).
REM
REM  Uses netstat + taskkill — avoids PowerShell TCP enumeration
REM  which can fail when the paging file is too small.
REM ============================================================

setlocal EnableDelayedExpansion

echo === STOP_ARCHON_STACK: stopping archon-server (8181), MCP (8051), agents (8052) ===

call :kill_port 8181
call :kill_port 8051
call :kill_port 8052

REM Give the OS a moment to release the ports (ping avoids timeout stdin redirect error)
ping 127.0.0.1 -n 4 >nul

echo.
echo === Verifying ports are free ===
set "BOUND=0"
call :check_port 8181
call :check_port 8051
call :check_port 8052
if !BOUND! EQU 0 (
    echo   All 3 ports are FREE.
) else (
    echo   !BOUND! ports still bound.
)

echo.
echo === STOP_ARCHON_STACK complete.
endlocal
exit /b 0

:kill_port
set "PORT=%~1"
for /f "tokens=5" %%I in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    if not "%%I"=="0" (
        echo   Killing PID %%I on port %PORT%
        taskkill /PID %%I /T /F >nul 2>&1
    )
)
exit /b 0

:check_port
set "PORT=%~1"
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    set /a BOUND+=1
    echo   Port %PORT% still bound
)
exit /b 0