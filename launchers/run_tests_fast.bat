@echo off
title DevMonitor — Fast Tests
cd /d "%USERPROFILE%\Desktop\DevMonitorWidget"
python scripts\run_pytest.py %*
if errorlevel 1 exit /b 1