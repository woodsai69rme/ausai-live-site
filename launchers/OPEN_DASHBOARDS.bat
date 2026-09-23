@echo off
setlocal EnableExtensions
title Open All Dashboards
cd /d "%~dp0.."
set PY=C:\Program Files\Python313\python.exe
if not exist "%PY%" set PY=python

echo Refreshing status JSON...
"%PY%" "TOOLS\regenerate_live_status.py"
"%PY%" "TOOLS\write_todo_board_status.py"
"%PY%" "TOOLS\write_setup_status.py"

start "" "%CD%\LIVE_SYSTEM_STATUS.html"
start "" "%CD%\TODO_BOARD_DASHBOARD.html"
start "" "%CD%\SETUP_DASHBOARD.html"
start "" "%CD%\MASTER_ALL_DASHBOARD.html"
start "" "%CD%\AI_TOOLS_DASHBOARD.html"
start "" "%CD%\UNIFIED_MASTER_DASHBOARD.html"
start "" "%CD%\PORTAL_WAR_ROOM.html"
start "" "%CD%\WAR_ROOM_CONTROL_DASHBOARD.html"
start "" "%CD%\MONEY_REPORT_AUD.html"
start "" http://localhost:3199/
exit /b 0