@echo off
REM uninstall_scheduler.bat — remove all SLEEP_TRIPLE scheduled tasks.

setlocal
set TASK_NIGHTLY=SLEEP_TRIPLE\Nightly
set TASK_DIGEST=SLEEP_TRIPLE\MorningDigest

echo Removing task "%TASK_NIGHTLY%"...
schtasks /delete /tn "%TASK_NIGHTLY%" /f
if errorlevel 1 (
  echo   "%TASK_NIGHTLY%" not present or already removed. Continuing.
)

echo Removing task "%TASK_DIGEST%"...
schtasks /delete /tn "%TASK_DIGEST%" /f
if errorlevel 1 (
  echo   "%TASK_DIGEST%" not present or already removed. Continuing.
)

echo Done.
endlocal
