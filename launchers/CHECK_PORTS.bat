@echo off
title Port Status Check
cd /d "%~dp0.."
python TOOLS\fast_port_check.py --hub
pause