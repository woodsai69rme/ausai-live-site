@echo off
title Autonomous Media Auto-Tagger & Contact Sheet Daemon
color 0B
cls
echo ===============================================================================
echo   🎬 AUTONOMOUS AI MEDIA AUTO-TAGGER & CONTACT SHEET GENERATOR (2026 PRO)
echo   Pool: C:\Users\karma\Downloads\dll (26.6k takes)
echo   Target Database: C:\Users\karma\TOOLS\media_vault.db
echo ===============================================================================
echo.
echo  [1] Run Quick Batch Pass (Tag next 500 untagged files)
echo  [2] Run Continuous Background Daemon (Auto-watch every 30s)
echo  [3] Exit
echo.
set /p opt="Select option (1-3): "
if "%opt%"=="1" (
    python -X utf8 C:\Users\karma\TOOLS\autonomous_media_tagger_daemon.py --once --batch 500
    pause
    exit /b 0
)
if "%opt%"=="2" (
    python -X utf8 C:\Users\karma\TOOLS\autonomous_media_tagger_daemon.py --batch 100 --interval 30
    pause
    exit /b 0
)
exit /b 0
