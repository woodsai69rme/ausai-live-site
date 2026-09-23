@echo off
REM ============================================================================
REM LAUNCH_SLEEP_CASH.bat — Unified launcher for the SLEEP_CASH_SYSTEM
REM ============================================================================
REM Run from any directory. Starts services, runs tests, or installs scheduling.
REM
REM Usage:
REM   LAUNCH_SLEEP_CASH.bat api          — Start the YouTube Transcript API
REM   LAUNCH_SLEEP_CASH.bat test-api     — Run API tests
REM   LAUNCH_SLEEP_CASH.bat test-pod     — Run opt_e POD tests
REM   LAUNCH_SLEEP_CASH.bat test-all     — Run all tests
REM   LAUNCH_SLEEP_CASH.bat dry-run      — SLEEP_TRIPLE full dry-run
REM   LAUNCH_SLEEP_CASH.bat publish      — SLEEP_TRIPLE live (publish)
REM   LAUNCH_SLEEP_CASH.bat schedule     — Install Windows scheduled tasks
REM   LAUNCH_SLEEP_CASH.bat dashboard    — Open revenue dashboard
REM   LAUNCH_SLEEP_CASH.bat tts-test     — Test edge-tts voiceover
REM   LAUNCH_SLEEP_CASH.bat status       — Show service status
REM   LAUNCH_SLEEP_CASH.bat preflight    — Per-Lane readiness (credentials, services)
REM   LAUNCH_SLEEP_CASH.bat monitor      — Poll live API health (Discord webhook optional)
REM   LAUNCH_SLEEP_CASH.bat help         — Show this menu
REM ============================================================================

setlocal

set ROOT=C:\Users\karma
set PYTHON=C:\Program Files\Python313\python.exe

cd /d "%ROOT%"

if "%1"=="" goto :menu
if /i "%1"=="api"           goto :api
if /i "%1"=="test-api"      goto :test_api
if /i "%1"=="test-pod"      goto :test_pod
if /i "%1"=="test-all"      goto :test_all
if /i "%1"=="dry-run"       goto :dry_run
if /i "%1"=="publish"       goto :publish
if /i "%1"=="schedule"      goto :schedule
if /i "%1"=="dashboard"     goto :dashboard
if /i "%1"=="tts-test"      goto :tts_test
if /i "%1"=="status"        goto :status
if /i "%1"=="preflight"     goto :preflight
if /i "%1"=="monitor"       goto :monitor
if /i "%1"=="monitor-probe-all" goto :monitor_probe_all
if /i "%1"=="install-monitor" goto :install_monitor
if /i "%1"=="help"          goto :menu

echo Unknown command: %1
echo.
goto :menu

:menu
echo.
echo ============================================================================
echo SLEEP_CASH_SYSTEM — Unified Launcher
echo ============================================================================
echo.
echo   api          Start the YouTube Transcript API (localhost:8000)
echo   test-api     Run API smoke tests
echo   test-pod     Run Print-on-Demand module tests
echo   test-all     Run all tests
echo   dry-run      SLEEP_TRIPLE full dry-run (no side effects)
echo   publish      SLEEP_TRIPLE live publish (requires API keys configured)
echo   schedule     Install Windows scheduled tasks
echo   dashboard    Open revenue dashboard (port 3144)
echo   tts-test     Test edge-tts voiceover
echo   status       Show service status
echo   preflight    Per-Lane readiness (credentials, services)
echo   monitor      Poll live API health (set DISCORD_WEBHOOK_URL to alert)
echo   monitor-probe-all  Single-shot multi-service probe (live API + ComfyUI :8188 + Ollama :11434)
echo   install-monitor  Install Windows scheduled task (admin required)
echo   help         Show this menu
echo.
echo Run: LAUNCH_SLEEP_CASH.bat [command]
echo.
goto :eof

:api
echo.
echo [LAUNCH_SLEEP_CASH] Starting YouTube Transcript API on port 8000...
echo [LAUNCH_SLEEP_CASH] Swagger docs will be at http://localhost:8000/docs
echo [LAUNCH_SLEEP_CASH] Press Ctrl+C to stop
echo.
cd /d "%ROOT%\SLEEP_CASH_API"
"%PYTHON%" -m uvicorn youtube_transcript_api_service:app --host 0.0.0.0 --port 8000 --reload
goto :eof

:test_api
echo.
echo [LAUNCH_SLEEP_CASH] Running YouTube Transcript API tests...
echo.
cd /d "%ROOT%"
"%PYTHON%" -m pytest SLEEP_CASH_API/test_yt_transcript_api.py -v 2>nul
if errorlevel 1 (
    echo pytest not available, falling back to direct test...
    "%PYTHON%" SLEEP_CASH_API/test_yt_transcript_api.py
)
goto :eof

:test_pod
echo.
echo [LAUNCH_SLEEP_CASH] Running Print-on-Demand module tests...
echo.
cd /d "%ROOT%"
"%PYTHON%" SLEEP_TRIPLE/opt_e_pod.py --dry-run --niche ai_humor --kind tshirt
"%PYTHON%" SLEEP_TRIPLE/opt_e_pod.py --dry-run --niche dev_memes --kind hoodie
"%PYTHON%" SLEEP_TRIPLE/opt_e_pod.py --dry-run --niche crypto_lifestyle --kind poster
goto :eof

:test_all
echo.
echo [LAUNCH_SLEEP_CASH] Running all tests...
echo.
call :test_api
echo.
call :test_pod
echo.
cd /d "%ROOT%"
"%PYTHON%" SLEEP_TRIPLE/_smoke_retry.py
goto :eof

:dry_run
echo.
echo [LAUNCH_SLEEP_CASH] Running SLEEP_TRIPLE dry-run (all 4 modules)...
echo.
cd /d "%ROOT%"
"%PYTHON%" SLEEP_TRIPLE/sleep_orchestrator.py --force-window
goto :eof

:publish
echo.
echo [LAUNCH_SLEEP_CASH] Running SLEEP_TRIPLE LIVE publish...
echo [LAUNCH_SLEEP_CASH] WARNING: This will hit real APIs and upload content.
echo.
cd /d "%ROOT%"
"%PYTHON%" SLEEP_TRIPLE/sleep_orchestrator.py --run --force-window --publish published 2>nul
if errorlevel 1 (
    echo.
    echo Direct --publish not supported by orchestrator; using per-module calls:
    "%PYTHON%" SLEEP_TRIPLE/opt_a_digital_factory.py --run --publish staged
    "%PYTHON%" SLEEP_TRIPLE/opt_b_faceless_shorts.py --run --publish
    "%PYTHON%" SLEEP_TRIPLE/opt_c_crypto_yield.py --run
    "%PYTHON%" SLEEP_TRIPLE/opt_d_alerts.py --run --trigger morning_digest
    "%PYTHON%" SLEEP_TRIPLE/opt_e_pod.py --run --publish staged
)
goto :eof

:schedule
echo.
echo [LAUNCH_SLEEP_CASH] Installing Windows scheduled tasks (admin required)...
echo.
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This command must be run as Administrator.
    echo Right-click LAUNCH_SLEEP_CASH.bat and "Run as administrator"
    goto :eof
)
"%ROOT%\SLEEP_TRIPLE\install_scheduler.bat"
"%ROOT%\SLEEP_TRIPLE\install_aggregator_scheduler.bat"
echo.
echo Scheduled tasks installed:
schtasks /query /tn "SLEEP_TRIPLE\Nightly" /fo LIST 2>nul | findstr "TaskName Next Run Time Status"
schtasks /query /tn "SLEEP_TRIPLE\MorningDigest" /fo LIST 2>nul | findstr "TaskName Next Run Time Status"
schtasks /query /tn "SLEEP_TRIPLE\WeeklyRollup" /fo LIST 2>nul | findstr "TaskName Next Run Time Status"
goto :eof

:dashboard
echo.
echo [LAUNCH_SLEEP_CASH] Starting revenue dashboard on port 3144...
echo.
start "" "%ROOT%\SLEEP_TRIPLE\launch_dashboard.bat"
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:3144
goto :eof

:tts_test
echo.
echo [LAUNCH_SLEEP_CASH] Testing edge-tts voiceover (Australian English)...
echo.
"%PYTHON%" -c "import edge_tts, asyncio; asyncio.run(edge_tts.Communicate('Testing edge TTS for faceless YouTube shorts', 'en-AU-NatashaNeural').save('SLEEP_TRIPLE/outbox/test_tts.wav')); print('OK - saved SLEEP_TRIPLE/outbox/test_tts.wav')"
goto :eof
:status
echo.
echo ============================================================================
echo SLEEP_CASH_SYSTEM — Service Status
echo ============================================================================
echo.
echo --- API Service (Vercel) ---
curl -s https://yt-transcript-api-ebon.vercel.app/healthz 2>nul | findstr "status"
echo.
echo --- Local Tests ---
"%PYTHON%" -c "from fastapi.testclient import TestClient; from SLEEP_CASH_API.youtube_transcript_api_service import app; c = TestClient(app); print('  API service: PASS (200 OK on /)' if c.get('/').status_code == 200 else '  API service: FAIL')" 2>nul
echo.
echo --- Config Status ---
echo  opt_a gumroad_api_key:
"%PYTHON%" -c "import json; d=json.load(open('SLEEP_TRIPLE/opt_a_config.json',encoding='utf-8')); print('    REPLACE_WITH_GUMROAD_API_KEY (not configured)' if 'REPLACE' in d.get('gumroad_api_key','') else '    CONFIGURED ✓')"
echo  opt_b youtube_upload_dry_run:
"%PYTHON%" -c "import json; d=json.load(open('SLEEP_TRIPLE/opt_b_config.json',encoding='utf-8')); print('    true (safe default, need OAuth to go live)' if d.get('youtube_upload_dry_run') else '    false (LIVE mode)')"
echo  opt_e printful_api_key:
"%PYTHON%" -c "import json; d=json.load(open('SLEEP_TRIPLE/opt_e_config.json',encoding='utf-8')); print('    REPLACE (not configured)' if 'REPLACE' in d.get('printful_api_key','') else '    CONFIGURED ✓')"
echo.
echo --- Latest Audit Log Entry ---
powershell -command "Get-Content '%ROOT%\SLEEP_TRIPLE\SLEEP_TRIPLE_AUDIT.jsonl' -Tail 1" 2>nul
echo.
goto :eof

:preflight
echo.
echo [LAUNCH_SLEEP_CASH] Running per-Lane readiness pre-flight...
echo [LAUNCH_SLEEP_CASH] Use --strict to fail on any non-[OK] Lane (CI gate).
echo.
cd /d "%ROOT%"
shift
"%PYTHON%" SLEEP_TRIPLE/preflight.py %*
goto :eof

:install_monitor
echo.
echo [LAUNCH_SLEEP_CASH] Forwarding install-monitor to standalone installer...
echo [LAUNCH_SLEEP_CASH] (Standalone installer auto-elevates; supports --dry-run / --uninstall.)
echo.
cd /d "%ROOT%"
shift /1
call "%ROOT%\install_monitor_scheduler.bat" %*
goto :eof

:monitor_probe_all
echo.
echo [LAUNCH_SLEEP_CASH] Running multi-service probe (live API + ComfyUI :8188 + Ollama :11434)...
echo [LAUNCH_SLEEP_CASH] Single-shot; exits 0 if all OK, 1 if any unreachable.
echo.
cd /d "%ROOT%"
"%PYTHON%" SLEEP_CASH_API/monitor.py --probe-all
goto :eof

:monitor
echo.
echo [LAUNCH_SLEEP_CASH] Starting API monitor (Ctrl+C to stop)...
echo [LAUNCH_SLEEP_CASH] Set DISCORD_WEBHOOK_URL env var to enable Discord alerts.
echo.
cd /d "%ROOT%"
shift
"%PYTHON%" SLEEP_CASH_API/monitor.py %*
goto :eof
