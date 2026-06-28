@echo off
REM install_aggregator_scheduler.bat - register SLEEP_TRIPLE\WeeklyRollup.
REM
REM Task: SLEEP_TRIPLE\WeeklyRollup - fires WEEKLY (Sunday) at 23:55
REM         Runs: run_weekly_rollup.bat
REM         Aggregator: Powershell Append-RevenueAggregator.ps1
REM           Reads:  SLEEP_TRIPLE\REVENUE_LEDGER.jsonl  (read-only)
REM           Writes: SLEEP_TRIPLE\REVENUE_SUMMARY.md    (append, BOM-free)
REM
REM The /tr argument is a single WRAPPER-PATH string - no embedded
REM powershell invocations, no arg lists, no backslash-escape problems.
REM Mirrors install_scheduler.bat's proven single-quote /tr form. Hardcoded
REM 23:55 is fine for a weekly aggregator; we do NOT need to compute the
REM wall-clock moment via Python (unlike the two daily tasks that bind to
REM the user's actual sleep window).
REM
REM Run as Administrator if your Windows policy blocks schtasks /create.

setlocal
set TASK=SLEEP_TRIPLE\WeeklyRollup
set WRAP=%~dp0run_weekly_rollup.bat

if not exist "%WRAP%" (
  echo ERROR: run_weekly_rollup.bat missing in %~dp0 1>&2
  exit /b 1
)

echo Registering task %TASK% ...
schtasks /create /tn "%TASK%" /tr "%WRAP%" /sc WEEKLY /d SUN /st 23:55 /f
if errorlevel 1 (
  echo schtasks weekly-rollup failed - try running as Administrator 1>&2
  exit /b 1
)

echo.
echo Done. Task registered:
echo   %TASK%   weekly (Sunday) at 23:55 user-local
echo Run uninstall_aggregator_scheduler.bat to remove.
echo Verify with: schtasks /query /tn "%TASK%" /fo LIST /v
endlocal
