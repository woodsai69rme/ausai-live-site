@echo off
title Deploy AutoMonetize AI Studio to Cloud
cd /d "%~dp0"
echo ========================================================
echo  AutoMonetize AI Cloud Deployment Manager
echo ========================================================
echo 1. Deploying to Vercel via CLI (if installed)...
call npx -y vercel --prod --yes
echo ========================================================
echo Deployment command complete.
pause
