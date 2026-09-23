@echo off
REM ============================================================================
REM install_monitor_scheduler.bat - Standalone installer for BOTH:
REM   SLEEP_CASH\Monitor     (live_api /healthz, every MONITOR_INTERVAL seconds)
REM   SLEEP_CASH\ProbeAll    (--probe-all multi-service, every 15 minutes)
REM
REM Usage:
REM   install_monitor_scheduler.bat
REM     Install (or re-install) BOTH scheduler entries. Auto-elevates to admin.
REM   install_monitor_scheduler.bat --uninstall
REM     Remove BOTH scheduler entries. Auto-elevates to admin.
REM   install_monitor_scheduler.bat --dry-run
REM     Show the would-be schtasks /create invocations without invoking them.
REM
REM Polished rounds:
REM   - --uninstall + --dry-run switches (first positional arg)
REM   - MONITOR_INTERVAL digit-only validation (non-digits reset to 120)
REM   - endlocal before both error exits and --uninstall branch
REM   - Pre-flight Python + monitor.py guards re-used in --dry-run
REM   - Dual install: SLEEP_CASH\Monitor + SLEEP_CASH\ProbeAll
REM ============================================================================

setlocal

set ROOT=C:\Users\karma
set PYTHON=C:\Program Files\Python313\python.exe
if not defined MONITOR_INTERVAL set "MONITOR_INTERVAL=120"

REM ---- Validate MONITOR_INTERVAL is digit-only; reset to 120 if not ----
for /f "delims=0123456789" %%i in ("%MONITOR_INTERVAL%") do goto :bad_interval
goto :ok_interval
:bad_interval
echo [install_monitor_scheduler] WARNING: MONITOR_INTERVAL="%MONITOR_INTERVAL%" is not a positive integer; resetting to 120.
set "MONITOR_INTERVAL=120"
:ok_interval

REM ---- --dry-run branch (BOTH tasks preview) ----
if /i not "%1"=="--dry-run" goto :skip_dry_run
    echo [install_monitor_scheduler] DRY-RUN: showing the would-be scheduled tasks, NOT installing.
    echo.

    REM Pre-flight: mirror the install-path checks so the preview is honest.
    if not exist "%PYTHON%" goto :no_python
    if not exist "%ROOT%\SLEEP_CASH_API\monitor.py" goto :no_monitor

    echo   python:       %PYTHON%
    echo   script:       %ROOT%\SLEEP_CASH_API\monitor.py
echo.
echo Would install two scheduler entries (BOTH auto-elevated above):
echo.
echo   [1] SLEEP_CASH\Monitor
echo       interval:   %MONITOR_INTERVAL% seconds (default 120)
echo       cadence:    every 2 minutes (Windows /sc minute /mo 2)
echo       invocation: schtasks /create /tn "SLEEP_CASH\Monitor" ^
echo                   /tr "\"%PYTHON%\" \"%ROOT%\SLEEP_CASH_API\monitor.py\" --interval %MONITOR_INTERVAL%" ^
echo                   /sc minute /mo 2 /f
echo.
echo   [2] SLEEP_CASH\ProbeAll
echo       flag:       --probe-all (live API + ComfyUI :8188 + Ollama :11434)
echo       cadence:    every 15 minutes (Windows /sc minute /mo 15)
echo       invocation: schtasks /create /tn "SLEEP_CASH\ProbeAll" ^
echo                   /tr "\"%PYTHON%\" \"%ROOT%\SLEEP_CASH_API\monitor.py\" --probe-all" ^
echo                   /sc minute /mo 15 /f
echo.
echo No registry / Task Scheduler change has been made.
endlocal
exit /b 0

:skip_dry_run

REM ---- Self-elevate to Administrator if not already (skipped by --dry-run above; required for --uninstall + install) ----
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [install_monitor_scheduler] Not running as Administrator; re-launching elevated...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0' -ArgumentList '%*'"
    endlocal
    EXIT /b
)

REM ---- --uninstall branch (BOTH tasks) ----
if /i "%1"=="--uninstall" (
    echo [install_monitor_scheduler] Removing BOTH scheduler entries (Monitor + ProbeAll)...
    schtasks /delete /tn "SLEEP_CASH\Monitor" /f >nul 2>&1
    set "RC_M=%ERRORLEVEL%"
    schtasks /delete /tn "SLEEP_CASH\ProbeAll" /f >nul 2>&1
    set "RC_P=%ERRORLEVEL%"
    echo [install_monitor_scheduler] Monitor delete rc=%RC_M%, ProbeAll delete rc=%RC_P%.
    if %RC_M% EQU 0 if %RC_P% NEQ 0 (
        echo [install_monitor_scheduler] ProbeAll was not installed; nothing to remove there.
    )
    if %RC_M% NEQ 0 if %RC_P% EQU 0 (
        echo [install_monitor_scheduler] Monitor was not installed; nothing to remove there.
    )
    if %RC_M% NEQ 0 if %RC_P% NEQ 0 (
        echo [install_monitor_scheduler] NOTE: neither task was installed; nothing to remove.
        endlocal
        exit /b 0
    )
    echo [install_monitor_scheduler] Removed. Verify:
    schtasks /query /tn "SLEEP_CASH\Monitor" 2>&1 | findstr /c="ERROR"
    schtasks /query /tn "SLEEP_CASH\ProbeAll" 2>&1 | findstr /c="ERROR"
    echo (no ERROR lines above = both tasks are gone)
    endlocal
    exit /b 0
)
REM ---- Pre-flight checks ----
echo [install_monitor_scheduler] Running pre-flight checks...
if not exist "%PYTHON%" goto :no_python
if not exist "%ROOT%\SLEEP_CASH_API\monitor.py" goto :no_monitor
echo [install_monitor_scheduler] Python + monitor.py found.

REM ---- Install scheduled task ----
echo [install_monitor_scheduler] Installing scheduled task SLEEP_CASH\Monitor
echo [install_monitor_scheduler]   python:    %PYTHON%
echo [install_monitor_scheduler]   script:    %ROOT%\SLEEP_CASH_API\monitor.py
echo [install_monitor_scheduler]   interval:  %MONITOR_INTERVAL% seconds
echo.

schtasks /create ^
  /tn "SLEEP_CASH\Monitor" ^
  /tr "\"%PYTHON%\" \"%ROOT%\SLEEP_CASH_API\monitor.py\" --interval %MONITOR_INTERVAL%" ^
  /sc minute /mo 2 /f

REM Not wrapped in ( ... ) for the same parser-colon-confusion reason as the dry-run block.
if not errorlevel 1 goto :monitor_ok
echo.
echo [install_monitor_scheduler] ERROR: schtasks /create failed.
echo Run manually to see the failure detail:
echo     schtasks /create /tn "SLEEP_CASH\Monitor" /tr "\"%PYTHON%\" \"%ROOT%\SLEEP_CASH_API\monitor.py\" --interval %MONITOR_INTERVAL%" /sc minute /mo 2 /f
endlocal
exit /b 1

:monitor_ok
echo.
echo.
echo [install_monitor_scheduler] SLEEP_CASH\Monitor scheduled task installed. Verifying:
schtasks /query /tn "SLEEP_CASH\Monitor" /fo LIST 2>nul | findstr "TaskName Next Run Time Status"
echo.

REM ---- Install ProbeAll task (every 15 min, --probe-all flag, does NOT auto-Discord-post) ----
echo [install_monitor_scheduler] Installing scheduled task SLEEP_CASH\ProbeAll
echo [install_monitor_scheduler]   python:   %PYTHON%
echo [install_monitor_scheduler]   script:   %ROOT%\SLEEP_CASH_API\monitor.py --probe-all
echo [install_monitor_scheduler]   cadence:  every 15 minutes
echo.

schtasks /create ^
  /tn "SLEEP_CASH\ProbeAll" ^
  /tr "\"%PYTHON%\" \"%ROOT%\SLEEP_CASH_API\monitor.py\" --probe-all" ^
  /sc minute /mo 15 /f

REM Not wrapped in ( ... ) for the same parser-colon-confusion reason as the dry-run block.
if not errorlevel 1 goto :probeall_ok
echo.
echo [install_monitor_scheduler] ERROR: schtasks /create for ProbeAll failed.
echo  Run manually:
echo     schtasks /create /tn "SLEEP_CASH\ProbeAll" /tr "\"%PYTHON%\" \"%ROOT%\SLEEP_CASH_API\monitor.py\" --probe-all" /sc minute /mo 15 /f
endlocal
exit /b 1

:probeall_ok

echo.
echo [install_monitor_scheduler] SLEEP_CASH\ProbeAll scheduled task installed. Verifying:
schtasks /query /tn "SLEEP_CASH\ProbeAll" /fo LIST 2>nul | findstr "TaskName Next Run Time Status"
echo.

REM ---- Discord webhook hint ----
if defined DISCORD_WEBHOOK_URL (
    echo [install_monitor_scheduler] DISCORD_WEBHOOK_URL is set in your user env.
    echo   To thread it into the scheduled task, set it as a SYSTEM env var instead:
    echo     setx DISCORD_WEBHOOK_URL "https://discord.com/api/webhooks/..." /M
    echo   then re-run this installer.
) else (
    echo [install_monitor_scheduler] DISCORD_WEBHOOK_URL not set.
    echo   To enable Discord alerts after 3 consecutive failures:
    echo     setx DISCORD_WEBHOOK_URL "https://discord.com/api/webhooks/..." /M
    echo   then re-run this installer.
)
echo.
echo [install_monitor_scheduler] Next steps:
echo   - Wait ~2 minutes for first probe to fire
echo   - Verify probe output: python %ROOT%\SLEEP_CASH_API\monitor.py --once
echo   - Uninstall: install_monitor_scheduler.bat --uninstall
echo.

endlocal
exit /b 0

:no_python
echo.
echo [install_monitor_scheduler] ERROR: Python not found at "%PYTHON%".
echo Edit the set PYTHON= line at the top of this script to match your install
echo location (e.g. C:\Users\karma\python\.venv\Scripts\python.exe).
endlocal
exit /b 1

:no_monitor
echo.
echo [install_monitor_scheduler] ERROR: monitor.py not found at
echo "%ROOT%\SLEEP_CASH_API\monitor.py".
echo Verify the SLEEP_CASH_API folder is present at %ROOT%.
endlocal
exit /b 1
