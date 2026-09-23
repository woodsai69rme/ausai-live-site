@echo off
title Auto Beat-Synced Shorts & Reels Generator
color 0C
cls
echo ===============================================================================
echo   🎬 AUTO BEAT-SYNCED SHORTS & REELS VIDEO GENERATOR (2026 PRO)
echo   Target Aspect: 9:16 Vertical (1080x1920) for YouTube Shorts, TikTok & Reels
echo   Source: C:\Users\karma\Downloads\dll
echo   Output: C:\Users\karma\OUTPUT_SHORTS
echo ===============================================================================
echo.
echo  [1] Generate 15-Second Fast Montage (7 Cuts @ 2.1s each)
echo  [2] Generate 30-Second Extended Montage (14 Cuts @ 2.1s each)
echo  [3] Open Output Shorts Folder in File Explorer
echo  [4] Exit
echo.
set /p opt="Select option (1-4): "
if "%opt%"=="1" (
    python -X utf8 C:\Users\karma\TOOLS\auto_shorts_beat_sync_generator.py --clips 7 --duration 2.1
    start "" "C:\Users\karma\OUTPUT_SHORTS"
    pause
    exit /b 0
)
if "%opt%"=="2" (
    python -X utf8 C:\Users\karma\TOOLS\auto_shorts_beat_sync_generator.py --clips 14 --duration 2.1
    start "" "C:\Users\karma\OUTPUT_SHORTS"
    pause
    exit /b 0
)
if "%opt%"=="3" (
    start "" "C:\Users\karma\OUTPUT_SHORTS"
    exit /b 0
)
exit /b 0
