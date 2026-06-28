@echo off
REM uninstall_scheduler.bat — remove the nightly task.

setlocal
set TASKNAME=SLEEP_TRIPLE\Nightly

echo Removing task "%TASKNAME%"...
schtasks /delete /tn "%TASKNAME%" /f
if errorlevel 1 (
  echo Task not present or removal already done. Continuing.
)
echo Done.
endlocal
