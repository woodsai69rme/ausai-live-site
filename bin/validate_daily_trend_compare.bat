@echo off
:: bin/validate_daily_trend_compare.bat -- verify the daily war_room trend-compare task
::                                                actually fires + writes a trend report
::
:: Operator runs after bin\install_daily_trend_compare.bat + bin\verify_nightly_task.bat
:: confirm the task is registered. This is a WRITE-ONLY validator -- it fires a real
:: scheduled task (schtasks /Run) but does NOT install or modify the task itself.
::
:: Steps:
::   1. Check task is installed (fail fast if not)
::   2. Record current report count in SLEEP_TRIPLE\outbox\trend_reports\
::   3. Fire the task via `schtasks /Run`
::   4. Wait ~30s for the task to execute + write its report
::   5. List reports and check for a new one
::   6. Exit 0 if the task actually fired + wrote a report; exit 1 if not
::
:: Pre-req: bin\install_daily_trend_compare.bat has been run from an ELEVATED cmd.exe.
:: Also requires bin\verify_nightly_task.bat to confirm the task is registered.

setlocal

set "TASK_NAME=WarRoomDailyTrendCompare"
if not defined WAIT_SECONDS set "WAIT_SECONDS=30"
set "REPORT_DIR=%USERPROFILE%\SLEEP_TRIPLE\outbox\trend_reports"

echo.
echo ===========================================================
echo  Validating scheduled task "%TASK_NAME%"
echo ===========================================================
echo.

REM 1. Check task is installed (fail fast if not).
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Task "%TASK_NAME%" is NOT installed.
  echo        Run bin\install_daily_trend_compare.bat from an ELEVATED cmd.exe first.
  exit /b 1
)
echo [PASS] Task is installed.

REM 2. Record current report count (so we can detect a new one).
set "BEFORE_COUNT=0"
if exist "%REPORT_DIR%" (
  for /f %%N in ('dir /b /a-d "%REPORT_DIR%\report__*.md" 2^>nul ^| find /c /v ""') do set "BEFORE_COUNT=%%N"
)
echo   reports before: %BEFORE_COUNT%

REM 3. Fire the task immediately.
echo   firing task via `schtasks /Run`...
schtasks /Run /TN "%TASK_NAME%" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] schtasks /Run returned errorlevel %errorlevel%.
  exit /b 1
)
echo   task fired.

REM 4. Wait for the task to execute + write its report.
echo   waiting %WAIT_SECONDS%s for the task to execute + write its report...
timeout /t %WAIT_SECONDS% /nobreak >nul

REM 5. Re-count reports + compare.
set "AFTER_COUNT=0"
if exist "%REPORT_DIR%" (
  for /f %%N in ('dir /b /a-d "%REPORT_DIR%\report__*.md" 2^>nul ^| find /c /v ""') do set "AFTER_COUNT=%%N"
)
echo   reports after:  %AFTER_COUNT%

REM 6. Verdict.
if %AFTER_COUNT% gtr %BEFORE_COUNT% (
  echo.
  echo [PASS] Task fired + wrote a new trend report. Validation successful.
  echo        Latest report: dir /od /b "%REPORT_DIR%\report__*.md" works interactively.
  echo        Or run: python war_room.py launch-trend-compare --json
  exit /b 0
) else (
  echo.
  echo [FAIL] No new trend report was written after %WAIT_SECONDS%s.
  echo        Possible causes:
  echo          - PowerShell substitution failed silently (check task history)
  echo          - Working directory issue (task expects C:\Users\karma but operator's home is elsewhere)
  echo          - File system permission issue
  echo          - Task ran but launch-trend-compare hit a hard failure
  echo.
  echo        To debug:
  echo          schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
  echo          schtasks /Run /TN "%TASK_NAME%"   (then check Last Run Time + Result)
  exit /b 1
)

endlocal
