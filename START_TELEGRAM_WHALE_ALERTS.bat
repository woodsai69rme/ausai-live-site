@echo off
title Crypto VIP Telegram Alpha Broadcaster
color 0E
cls
echo ===============================================================================
echo   🪙 CRYPTO VIP TELEGRAM ALPHA BROADCASTER — MR. WILSON HIGH-CONVICTION SIGNALS
echo   Watching: C:\Users\karma\CRYPTO_SUITE_DATA\realtime_transactions_stream.json
echo   Daemon: Port 8088 Whale Copy-Trade Engine
echo ===============================================================================
echo.
echo  [1] Start Live Broadcaster Daemon (Watches 24/7 for new Whale Buys)
echo  [2] Send Single Test Signal (Format verification)
echo  [3] Edit Telegram Configuration (notepad telegram_config.json)
echo  [4] Exit
echo.
set /p opt="Select option (1-4): "
if "%opt%"=="1" (
    python -X utf8 C:\Users\karma\TOOLS\crypto_vip_telegram_broadcaster.py --daemon
    pause
    exit /b 0
)
if "%opt%"=="2" (
    python -X utf8 C:\Users\karma\TOOLS\crypto_vip_telegram_broadcaster.py --test
    pause
    exit /b 0
)
if "%opt%"=="3" (
    notepad "C:\Users\karma\JARVIS\telegram_config.json"
    exit /b 0
)
exit /b 0
