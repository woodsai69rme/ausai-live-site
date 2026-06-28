@echo off
REM launch_dashboard.bat — start the SLEEP_TRIPLE dashboard in background.
REM
REM 1) Starts dashboard_server.py in a minimised console window.
REM 2) Waits a moment for it to bind.
REM 3) Opens http://127.0.0.1:3144 in your default browser.

setlocal
cd /d C:\Users\karma\SLEEP_TRIPLE

echo Starting dashboard server ...
start "SLEEP_TRIPLE-Dashboard" /min python dashboard_server.py

ping -n 3 127.0.0.1 > nul

echo Opening browser to http://127.0.0.1:3144 ...
start "" http://127.0.0.1:3144

echo.
echo Dashboard running in the background. Stop it with:
echo   taskkill /FI "WINDOWTITLE eq SLEEP_TRIPLE-Dashboard*"
echo Or close the minimised console window.
endlocal
