@echo off
REM ============================================================
REM  GODSEYE 1.0 - Awesome Dashboard Launcher (AusAI Edition)
REM  Repo: https://github.com/VrushankPatel/godseye
REM  Local: C:\Users\karma\godseye-app
REM ============================================================
setlocal
cd /d C:\Users\karma\godseye-app

echo.
echo  [GODSEYE] Geospatial Intelligence Dashboard
echo  ------------------------------------------
echo  [1] Dev mode  (Vite + backend proxy, http://localhost:5173)
echo  [2] Prod mode (build + serve on http://localhost:3001)
echo  [3] Env check (BYOK capability matrix)
echo  [4] Feed smoke test
echo.
set /p MODE=" Select 1-4 [1]: "
if "%MODE%"=="" set MODE=1

if "%MODE%"=="1" (
  echo  Starting DEV server...
  if exist scripts\local-secrets.sh (
    echo  NOTE: copy scripts\local-secrets.example.sh values to .env.local for keys
  )
  npm run dev
) else if "%MODE%"=="2" (
  echo  Building + serving PROD...
  npm run build && npm run serve
) else if "%MODE%"=="3" (
  npm run env:check
  pause
) else if "%MODE%"=="4" (
  npm run feed:audit:smoke
  pause
) else (
  npm run dev
)
