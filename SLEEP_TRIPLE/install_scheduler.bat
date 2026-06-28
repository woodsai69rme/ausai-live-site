@echo off
REM install_scheduler.bat — register SLEEP_TRIPLE nightly at 23:00.
REM
REM Honours Rule #8 — no installs into Documents/Downloads etc., only
REM registers a Task Scheduler entry under %WINDIR%\System32\Tasks.
REM
REM Run as Administrator if your Windows policy blocks schtasks /create.

setlocal
set TASKNAME=SLEEP_TRIPLE\Nightly
set XML=%~dp0sleep_task.xml

if not exist "%XML%" (
  echo ERROR: sleep_task.xml not found in %~dp0 1>&2
  exit /b 1
)

echo Registering task "%TASKNAME%" from "%XML%" ...
schtasks /create /tn "%TASKNAME%" /xml "%XML%" /f
if errorlevel 1 (
  echo schtasks /create failed. Try running as Administrator. 1>&2
  exit /b 1
)
echo.
echo Done. Task "%TASKNAME%" will fire daily at 23:00 Australia/Sydney with --run --force-window.
echo Run uninstall_scheduler.bat to remove.
echo Verify with: schtasks /query /tn "%TASKNAME%"
endlocal
