@echo off
REM install_scheduler.bat - register two SLEEP_TRIPLE scheduled tasks.
REM
REM Task 1: SLEEP_TRIPLE\Nightly       - fires at sleep_window[0] (default 23:00)
REM         Runs: run_nightly.bat           (wraps sleep_orchestrator.py --run --force-window)
REM Task 2: SLEEP_TRIPLE\MorningDigest - fires at sleep_window[1] (default 07:00)
REM         Runs: run_morning_digest.bat    (wraps opt_d_alerts.py --run --trigger morning_digest)
REM
REM Both trigger times computed in user-local HH:MM from sleep_config.json tz
REM via compute_next_boundary.py --boundary=start|end, so each task fires at
REM the correct wall-clock moment regardless of Windows box timezone.
REM
REM The /tr arguments are SINGLE-COMMAND WRAPPER-PATH strings - no embedded
REM python invocations, no arg lists, no backslashes-to-escape problems.
REM
REM Run as Administrator if your Windows policy blocks schtasks /create.

setlocal
set TASK_NIGHTLY=SLEEP_TRIPLE\Nightly
set TASK_DIGEST=SLEEP_TRIPLE\MorningDigest
set PY=%~dp0compute_next_boundary.py
set WRAP_NIGHTLY=%~dp0run_nightly.bat
set WRAP_DIGEST=%~dp0run_morning_digest.bat

if not exist "%PY%" (
  echo ERROR: compute_next_boundary.py missing in %~dp0 1>&2
  exit /b 1
)
if not exist "%WRAP_NIGHTLY%" (
  echo ERROR: run_nightly.bat missing in %~dp0 1>&2
  exit /b 1
)
if not exist "%WRAP_DIGEST%" (
  echo ERROR: run_morning_digest.bat missing in %~dp0 1>&2
  exit /b 1
)

REM --- Compute the next nightly trigger time (sleep_window[0]) ---
set "BT_NIGHTLY="
for /f "usebackq delims=" %%t in (`python "%PY%" --boundary start`) do set "BT_NIGHTLY=%%t"
if "%BT_NIGHTLY%"=="" (
  echo ERROR: boundary compute start failed - check sleep_config.json 1>&2
  exit /b 1
)

REM --- Compute the next morning-digest trigger time (sleep_window[1]) ---
set "BT_DIGEST="
for /f "usebackq delims=" %%t in (`python "%PY%" --boundary end`) do set "BT_DIGEST=%%t"
if "%BT_DIGEST%"=="" (
  echo ERROR: boundary compute end failed - check sleep_config.json 1>&2
  exit /b 1
)

echo Detected nightly trigger: %BT_NIGHTLY%
echo Detected morning digest:  %BT_DIGEST%
echo.

REM Install path has NO SPACES (hard-coded C:\Users\karma\SLEEP_TRIPLE\...), so a
REM single quote pair is sufficient. Do NOT use escaped quotes (\"%WRAP%\") as
REM some schtasks/cmd combos interpret the trailing backslash as an escape and
REM silently mangle the registered command path.

echo Registering task %TASK_NIGHTLY% ...
schtasks /create /tn "%TASK_NIGHTLY%" /tr "%WRAP_NIGHTLY%" /sc daily /st %BT_NIGHTLY% /f
if errorlevel 1 (
  echo schtasks nightly failed - try running as Administrator 1>&2
  exit /b 1
)

echo Registering task %TASK_DIGEST% ...
schtasks /create /tn "%TASK_DIGEST%" /tr "%WRAP_DIGEST%" /sc daily /st %BT_DIGEST% /f
if errorlevel 1 (
  echo schtasks morning-digest failed - try running as Administrator 1>&2
  exit /b 1
)

echo.
echo Done. Tasks registered:
echo   %TASK_NIGHTLY%   daily at %BT_NIGHTLY%
echo   %TASK_DIGEST% daily at %BT_DIGEST%
echo Run uninstall_scheduler.bat to remove.
echo Verify with: schtasks /query /tn "%TASK_NIGHTLY%" /fo LIST /v
echo              schtasks /query /tn "%TASK_DIGEST%" /fo LIST /v
endlocal
