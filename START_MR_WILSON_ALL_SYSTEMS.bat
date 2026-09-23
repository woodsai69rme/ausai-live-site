@echo off
title Mr. Wilson // Sovereign 24/7 Master Deployment
echo ========================================================================
echo  MR. WILSON // SOVEREIGN 24/7 UNIFIED WORKSTATION DEPLOYMENT (v3.0)
echo ========================================================================
echo.

echo [1/6] Launching Mr. Wilson Command API on port 6971...
start "Mr Wilson API" /min cmd /c "python C:\Users\karma\JARVIS\mr_wilson_api.py"

echo [2/6] Launching JARVIS Holographic HUD on port 6970...
start "JARVIS HUD" /min cmd /c "python C:\Users\karma\JARVIS\web_hud\server.py"

echo [3/6] Launching Mr. Wilson System Tray Daemon...
start "Mr Wilson Tray" /min cmd /c "python C:\Users\karma\JARVIS\mr_wilson_tray_daemon.py"

echo [4/6] Launching Live Avatar Desktop Companion...
start "Mr Wilson Avatar" cmd /c "python C:\Users\karma\JARVIS\desktop_companion_mr_wilson.py"

echo [5/6] Launching Always-On Voice Listener (LCS USB Audio Priority)...
start "Mr Wilson Listener" cmd /c "python C:\Users\karma\JARVIS\always_on_mr_wilson_listener.py"

timeout /t 2 > nul

echo [6/6] Opening Master Control Dashboard...
start "" "C:\Users\karma\Desktop\MR_WILSON_MASTER_DASHBOARD.html"

echo.
echo ========================================================================
echo  ALL MR. WILSON SYSTEMS ONLINE & OPERATIONAL FOR WOODS.
echo ========================================================================
timeout /t 4 > nul
exit
