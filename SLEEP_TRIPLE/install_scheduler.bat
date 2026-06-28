@echo off
REM install_scheduler.bat — register SLEEP_TRIPLE nightly at sleep_window[0].
REM
REM The trigger time is computed in user-local HH:MM from sleep_config.json tz
REM via compute_next_boundary.py, so the nightly run fires at the correct
REM wall-clock moment regardless of what timezone the Windows box is set to.
REM
REM NOTE: the /tr argument is unquoted internally because the install path is
REM hard-coded to "C:\Users\karma\SLEEP_TRIPLE\..." (no spaces). If you ever
REM install into a path with spaces, schtasks /tr arg parsing will mis-fire —
REM either wrap %BIN% in escaped quotes AND rename or take care of the
REM command shell parsing yourself.
REM
REM Run as Administrator if your Windows policy blocks schtasks /create.

setlocal
set TASKNAME=SLEEP_TRIPLE\Nightly
set PY=%~dp0compute_next_boundary.py
set BIN=%~dp0sleep_orchestrator.py

if not exist "%PY%" (
  echo ERROR: compute_next_boundary.py not found in %~dp0 1>&2
  exit /b 1
)
if not exist "%BIN%" (
  echo ERROR: sleep_orchestrator.py not found in %~dp0 1>&2
  exit /b 1
)

REM Capture the next sleep_window[0] in user-local HH:MM
set "BT="
for /f "usebackq delims=" %%t in (`python "%PY%"`) do set "BT=%%t"

if "%BT%"=="" (
  echo ERROR: compute_next_boundary.py failed. Check sleep_config.json. 1>&2
  exit /b 1
)

echo Detected next trigger time: %BT% (system-local, derived from sleep_config.json tz)
echo Registering task "%TASKNAME%" ...
schtasks /create /tn "%TASKNAME%" /tr "python %BIN% --run --force-window" /sc daily /st %BT% /f
if errorlevel 1 (
  echo schtasks /create failed. Try running as Administrator. 1>&2
  exit /b 1
)
echo.
echo Done. Task "%TASKNAME%" fires daily at %BT% system-local.
echo Run uninstall_scheduler.bat to remove.
echo Verify with: schtasks /query /tn "%TASKNAME%"
endlocal
