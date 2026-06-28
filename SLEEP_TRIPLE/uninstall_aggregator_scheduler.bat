@echo off
REM uninstall_aggregator_scheduler.bat - remove the weekly rollup task.
REM
REM Symmetric with install_aggregator_scheduler.bat. Run as Administrator
REM if your Windows policy blocks schtasks /delete.

setlocal
set TASK=SLEEP_TRIPLE\WeeklyRollup
schtasks /delete /tn "%TASK%" /f
if errorlevel 1 (
  echo schtasks delete failed - try running as Administrator, or task may not exist 1>&2
  exit /b 1
)
echo Removed task %TASK%
endlocal
