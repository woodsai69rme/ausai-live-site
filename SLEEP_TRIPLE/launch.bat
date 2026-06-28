@echo off
REM SLEEP_TRIPLE launcher — runs the three-option sleep-money orchestrator.
REM Default: --dry-run (safe). Pass --run for live operations.
REM Honour Rule #8: never touch Documents, Downloads, Pictures, Videos,
REM Music, Desktop, OneDrive, ARCHIVE_OLD.

setlocal
cd /d C:\Users\karma\SLEEP_TRIPLE

if "%1"=="--run" goto :run_mode
if "%1"=="--list" goto :list_mode

:default_mode
echo.
echo === SLEEP_TRIPLE (dry-run) ===
python sleep_orchestrator.py %2 %3 %4 %5 %6 %7 %8 %9
goto :end

:run_mode
echo.
echo === SLEEP_TRIPLE (LIVE ^- side effects allowed) ===
python sleep_orchestrator.py --run %2 %3 %4 %5 %6 %7 %8 %9
goto :end

:list_mode
echo.
echo === SLEEP_TRIPLE audit log ===
python sleep_orchestrator.py --list
goto :end

:end
endlocal
