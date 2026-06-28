@echo off
REM run_weekly_rollup.bat - wrapper invoked by SLEEP_TRIPLE\WeeklyRollup.
REM Aggregates the project-local REVENUE_LEDGER.jsonl into REVENUE_SUMMARY.md
REM via Append-RevenueAggregator.ps1 (now BOM-free since the BOM fix in this
REM commit). Fires weekly (Sunday 23:55 user-local) per install_aggregator_
REM scheduler.bat.
REM
REM This wrapper exists so install_aggregator_scheduler.bat can register
REM the task with `schtasks /create /tr "<path-to-this-bat>"` - a single
REM clean path string. Embedding the long powershell.exe invocation inside
REM /tr's quoted argument hits cmd/schtasks quoting bugs (backslash escapes
REM inside the PS1 path), so we wrap it here.

setlocal
set PS1=C:\Users\karma\Append-RevenueAggregator.ps1
set LEDGER=C:\Users\karma\SLEEP_TRIPLE\REVENUE_LEDGER.jsonl
set SUMMARY=C:\Users\karma\SLEEP_TRIPLE\REVENUE_SUMMARY.md

if not exist "%PS1%" (
  echo run_weekly_rollup: missing %PS1% 1>&2
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -LedgerPath "%LEDGER%" -SummaryPath "%SUMMARY%"
exit /b %ERRORLEVEL%
endlocal
