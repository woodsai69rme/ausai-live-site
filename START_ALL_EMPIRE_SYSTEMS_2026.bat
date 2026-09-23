@echo off
setlocal enabledelayedexpansion
title EMPIRE MASTER CONTROL CENTER 2026 - BRISBANE AI ^& IT SUITE
color 0B

echo ===============================================================================
echo     🇦🇺 BRISBANE AI ^& IT AGENCY — EMPIRE MASTER LAUNCHER (AUG/SEP 2026) 🇦🇺
echo ===============================================================================
echo.
echo  [1] Launch ALL Empire Systems (Agency Server + YouTube Agent + Browser Hub + Crypto)
echo  [2] Start Brisbane AI Agency FastAPI Server (Port 8010)
echo  [3] Start Lumen YouTube Automation Agent (Port 3456)
echo  [4] Run Quad Browser Vision Swarm (Playwright 4-Worker)
echo  [5] Open Master Command Portal (EMPIRE_MASTER_PORTAL.html)
echo  [6] Run Brisbane IT Audit Generator (tools/brisbane_it_auditor.py)
echo  [7] Test OpenRouter Free Model Fleet
echo  [8] 📜 Open All Saved Conversations Archive (C:\Users\karma\ALL_SAVED_CHATS)
echo  [9] 📡 Start FINDRADAR Search ^& Video Engine (Port 5173)
echo  [10] ⌨️ Start Global Hotkey Daemon (Ctrl+Alt+G / F / R / C)
echo  [11] 🪙 Start Unified Crypto Top Buyer ^& Whale Copy-Trade Suite (Port 8088 / 3142)
echo  [12] 🎬 Start Media Vault ^& Studio Dashboards (Downloads/dll ^& X: Drive - Port 8686)
echo  [13] 👁️ Start Vision Media Sorter Studio (Port 8765)
echo  [14] Exit
echo.
echo ===============================================================================
set opt=%~1
if "%opt%"=="" set /p opt="Select an option (1-14): "

if "%opt%"=="1" goto launch_all
if "%opt%"=="2" goto start_agency
if "%opt%"=="3" goto start_youtube
if "%opt%"=="4" goto run_swarm
if "%opt%"=="5" goto open_portal
if "%opt%"=="6" goto run_audit
if "%opt%"=="7" goto test_fleet
if "%opt%"=="8" goto open_chats
if "%opt%"=="9" goto start_findradar
if "%opt%"=="10" goto start_hotkeys
if "%opt%"=="11" goto start_crypto
if "%opt%"=="12" goto start_media_vault
if "%opt%"=="13" goto start_visual_sorter
if "%opt%"=="14" goto end

:launch_all
echo.
echo [*] Starting Media Vault Daemon on Port 8686...
start "Media Vault Daemon" /min cmd /c "python C:\Users\karma\TOOLS\media_vault_server.py"
ping -n 2 127.0.0.1 >nul

echo [*] Starting Vision Media Sorter Studio on Port 8765...
start "Vision Media Sorter" /min cmd /c "python -u C:\Users\karma\TOOLS\visual_sorter_web_app.py"
ping -n 2 127.0.0.1 >nul

echo [*] Starting JARVIS Holographic HUD on Port 6970...
start "JARVIS HUD Server" /min cmd /c "cd /d C:\Users\karma\JARVIS && python web_hud\server.py"
ping -n 2 127.0.0.1 >nul

echo [*] Starting Brisbane AI Agency Backend on Port 8010...
start "Brisbane AI Agency API" /min cmd /c "cd /d C:\Users\karma\AI_AGENCY && python -X utf8 server.py"
ping -n 2 127.0.0.1 >nul

echo [*] Starting Lumen YouTube Automation Agent on Port 3456...
start "Lumen YouTube Agent" /min cmd /c "cd /d C:\Users\karma\github_repos\youtube-automation-agent\youtube-automation-agent-master && node index.js"
ping -n 2 127.0.0.1 >nul

echo [*] Starting 24/7 Persistent Crypto Master Engine ^& Supervisor on Port 8088...
wscript "C:\Users\karma\START_CRYPTO_24_7_SERVICE.vbs"
ping -n 2 127.0.0.1 >nul

echo [*] Starting God-Mode AI Command Center on Port 3142...
start "God-Mode Command Center" /min cmd /c "cd /d C:\Users\karma\ACTIVE_PROJECTS\ai-tools-suite && npm run dev"
ping -n 3 127.0.0.1 >nul

echo [*] Opening Master Command Portal and Cockpits in Browser...
start "" "http://localhost:8989"
start "" "file:///C:/Users/karma/EMPIRE_MASTER_PORTAL.html"
start "" "http://localhost:8765"
start "" "http://localhost:8686/unified"
start "" "file:///C:/Users/karma/ULTIMATE_CRYPTO_PLATFORM.html"
start "" "http://localhost:6970"
start "" "http://localhost:3142"
echo.
echo [OK] All Empire Systems Successfully Launched!
if "%~1"=="" pause
goto end

:start_agency
cd /d C:\Users\karma\AI_AGENCY
python -X utf8 server.py
pause
goto end

:start_youtube
cd /d C:\Users\karma\github_repos\youtube-automation-agent\youtube-automation-agent-master
node index.js
pause
goto end

:run_swarm
cd /d C:\Users\karma\TOOLS
python quad_browser_swarm.py --mode parallel
pause
goto end

:open_portal
start msedge "file:///C:/Users/karma/EMPIRE_MASTER_PORTAL.html"
goto end

:run_audit
cd /d C:\Users\karma\AI_AGENCY
python tools/brisbane_it_auditor.py
pause
goto end

:open_chats
start "" "C:\Users\karma\ALL_SAVED_CHATS\index.md"
start "" "C:\Users\karma\ALL_SAVED_CHATS"
goto end

:start_findradar
cd /d C:\Users\karma\findradar
npm run dev
goto end

:start_hotkeys
cd /d C:\Users\karma\TOOLS
python empire_desktop_hud.py
goto end

:start_crypto
call "C:\Users\karma\START_CRYPTO_TOP_BUYER_SUITE.bat"
goto end

:start_media_vault
call "C:\Users\karma\START_MEDIA_VAULT_MASTER.bat"
goto end

:start_visual_sorter
call "C:\Users\karma\START_VISUAL_SORTER_STUDIO.bat"
goto end

:end
exit /b 0
