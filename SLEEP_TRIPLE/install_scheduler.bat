@echo off
REM install_scheduler.bat — register two SLEEP_TRIPLE scheduled tasks.
REM
REM Task #1: SLEEP_TRIPLE\Nightly       - fires at sleep_window[0] (default 23:00)
REM         Runs: python sleep_orchestrator.py --run --force-window
REM Task #2: SLEEP_TRIPLE\MorningDigest - fires at sleep_window[1] (default 07:00)
REM         Runs: python opt_d_alerts.py --run --trigger morning_digest
REM                --audit-window-hours 8  (covers the 23:00->07:00 sleep window).
REM
REM Both trigger times are computed in user-local HH:MM from sleep_config.json
REM tz via compute_next_boundary.py --boundary=start|end, so each task fires
REM at the correct wall-clock moment regardless of what timezone the Windows
REM box is set to. DST spring-forward gaps are auto-detected and the install
REM refuses with a clear message instead of silently mis-firing.
REM
REM The /tr arguments are unquoted internally because the install path is
REM hard-coded to "C:\Users\karma\SLEEP_TRIPLE\..." (no spaces). If you ever
REM install into a path with spaces, schtasks /tr arg parsing will mis-fire.
REM
REM Run as Administrator if your Windows policy blocks schtasks /create.

setlocal
set TASK_NIGHTLY=SLEEP_TRIPLE\Nightly
set TASK_DIGEST=SLEEP_TRIPLE\MorningDigest
set PY=%~dp0compute_next_boundary.py
set BIN_NIGHTLY=%~dp0sleep_orchestrator.py
set BIN_DIGEST=%~dp0opt_d_alerts.py

if not exist "%PY%" (
  echo ERROR: compute_next_boundary.py not found in %~dp0 1>&2
  exit /b 1
)
if not exist "%BIN_NIGHTLY%" (
  echo ERROR: sleep_orchestrator.py not found in %~dp0 1>&2
  exit /b 1
)
if not exist "%BIN_DIGEST%" (
  echo ERROR: opt_d_alerts.py not found in %~dp0 1>&2
  exit /b 1
)

REM --- Compute the next nightly trigger time (sleep_window[0]) ---
set "BT_NIGHTLY="
for /f "usebackq delims=" %%t in (`python "%PY%" --boundary start`) do set "BT_NIGHTLY=%%t"
if "%BT_NIGHTLY%"=="" (
  echo ERROR: compute_next_boundary.py --boundary start failed. Check sleep_config.json. 1>&2
  exit /b 1
)

REM --- Compute the next morning-digest trigger time (sleep_window[1]) ---
set "BT_DIGEST="
for /f "usebackq delims=" %%t in (`python "%PY%" --boundary end`) do set "BT_DIGEST=%%t"
if "%BT_DIGEST%"=="" (
  echo ERROR: compute_next_boundary.py --boundary end failed. Check sleep_config.json. 1>&2
  exit /b 1
)

echo Detected nightly trigger:  %BT_NIGHTLY% (sleep_window[0] in user-local)
echo Detected morning digest:   %BT_DIGEST% (sleep_window[1] in user-local)
echo.
echo Registering task "%TASK_NIGHTLY%" ...
schtasks /create /tn "%TASK_NIGHTLY%" /tr "python %BIN_NIGHTLY% --run --force-window" /sc daily /st %BT_NIGHTLY% /f
if errorlevel 1 (
  echo schtasks /create (nightly) failed. Try running as Administrator. 1>&2
  exit /b 1
)

echo Registering task "%TASK_DIGEST%" ...
schtasks /create /tn "%TASK_DIGEST%" /tr "python %BIN_DIGEST% --run --trigger morning_digest --audit-window-hours 8" /sc daily /st %BT_DIGEST% /f
if errorlevel 1 (
  echo schtasks /create (morning digest) failed. Try running as Administrator. 1>&2
  exit /b 1
)

echo.
echo Done. Both tasks registered:
echo   "%TASK_NIGHTLY%"   daily at %BT_NIGHTLY%
echo   "%TASK_DIGEST%" daily at %BT_DIGEST%
echo Run uninstall_scheduler.bat to remove either.
echo Verify with:
echo   schtasks /query /tn "%TASK_NIGHTLY%"
echo   schtasks /query /tn "%TASK_DIGEST%"
endlocal
