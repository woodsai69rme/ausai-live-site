@echo off
REM run_nightly.bat — wrapper invoked by SLEEP_TRIPLE\Nightly scheduled task.
REM Calls sleep_orchestrator.py with --run --force-window.
REM This wrapper exists so that install_scheduler.bat can register the task
REM with `schtasks /create /tr "<path-to-this-bat>"` — a single clean path
REM string. Embedding `python "<orchestrator-path>" --run --force-window`
REM inside /tr's quoted argument hits cmd/schtasks quoting bugs (backslash
REM escapes inside the path), so we wrap the long invocation in this file.

setlocal
set BIN=%~dp0sleep_orchestrator.py
if not exist "%BIN%" (
  echo run_nightly: missing %BIN% 1>&2
  exit /b 1
)
python "%BIN%" --run --force-window
exit /b %ERRORLEVEL%
endlocal
