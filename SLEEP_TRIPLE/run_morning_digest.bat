@echo off
REM run_morning_digest.bat — wrapper invoked by SLEEP_TRIPLE\MorningDigest task.
REM Fires at sleep_window[1] (07:00 user-local by default) and sends the
REM morning digest aggregating the previous night's audit-log rows.
REM Window length 8h covers the default 23:00->07:00 sleep window.

setlocal
set BIN=%~dp0opt_d_alerts.py
if not exist "%BIN%" (
  echo run_morning_digest: missing %BIN% 1>&2
  exit /b 1
)
python "%BIN%" --run --trigger morning_digest --audit-window-hours 8
exit /b %ERRORLEVEL%
endlocal
