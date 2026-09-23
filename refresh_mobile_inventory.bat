@echo off
REM ============================================================
REM refresh_mobile_inventory.bat
REM Idempotent mobile-inventory refresh.
REM
REM Usage:
REM   refresh_mobile_inventory.bat           (full pipeline: scan + filter)
REM   refresh_mobile_inventory.bat --smoke   (smoke-test: skip scan, use most recent RAW CSV)
REM   refresh_mobile_inventory.bat --no-scan (skip scan, use most recent RAW CSV)
REM
REM Flow:
REM   1. Re-run scan_pc_apps.ps1 with output to a timestamped RAW CSV
REM      (skipped if --smoke or --no-scan).
REM   2. Filter against mobile terms (adb / apktool / jadx / frida / etc)
REM      and emit MOBILE_FILTERED.csv at workspace root
REM      (or MOBILE_FILTERED_SMOKE.csv in --smoke mode).
REM   3. Emit refresh_status.json to %USERPROFILE% for the morning digest
REM      (SLEEP_TRIPLE opt_d_alerts scans this file).
REM
REM Operator can invoke manually:  refresh_mobile_inventory.bat
REM Or schedule weekly via the mobile_inventory_refresh.xml Task Scheduler XML.
REM
REM Designed under Karma's Golden Rules:
REM   - regular run (no stealth; explicit invocation; append-style outputs)
REM   - one CSV emitted per run (no overwrite guesswork via timestamped name)
REM   - never touches Documents / Downloads / Desktop / OneDrive / Pictures /
REM     Videos / Music / ARCHIVE_OLD (Rule #8 personal-folder fence)
REM ============================================================

setlocal EnableExtensions

REM ============================================================
REM Parse args
REM ============================================================
set FORCE_SCAN=1
set MODE=FULL
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--smoke" (
    set MODE=SMOKE
    set FORCE_SCAN=0
    shift
    goto parse_args
)
if /i "%~1"=="--no-scan" (
    set FORCE_SCAN=0
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    echo Usage: refresh_mobile_inventory.bat [--smoke ^| --no-scan]
    echo   --smoke    skip scan; emit to MOBILE_FILTERED_SMOKE.csv (no overwrite)
    echo   --no-scan  skip scan; emit to MOBILE_FILTERED.csv
    endlocal
    exit /b 0
)
shift
goto parse_args
:args_done

REM ============================================================
REM Locale-safe timestamp via PowerShell Get-Date (%%a inside for-loop)
REM ============================================================
for /f "tokens=*" %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set TS_HDR=%%a
if "%MODE%"=="SMOKE" set TS_HDR=SMOKE_TEST

set RAW_CSV=%USERPROFILE%\RAW_PC_APPS_INVENTORY__%TS_HDR%.csv
set OUT_CSV=%USERPROFILE%\MOBILE_FILTERED.csv
if "%MODE%"=="SMOKE" set OUT_CSV=%USERPROFILE%\MOBILE_FILTERED_SMOKE.csv
set STATUS_JSON=%USERPROFILE%\refresh_status.json

echo ============================================================
echo refresh_mobile_inventory.bat  [%TS_HDR%]  mode=%MODE%
echo ============================================================
echo user profile: %USERPROFILE%
echo raw CSV    : %RAW_CSV%
echo mobile CSV : %OUT_CSV%
echo status JSON: %STATUS_JSON%
echo.

REM ============================================================
REM Step 1: scan (skipped in --smoke / --no-scan)
REM ============================================================
if "%FORCE_SCAN%"=="1" (
    echo [1/3] Re-running scan_pc_apps.ps1 ...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scan_pc_apps.ps1" -OutputPath "%RAW_CSV%"
    set SCAN_RC=%ERRORLEVEL%
    if not %SCAN_RC% == 0 (
        echo [WARN] scan_pc_apps.ps1 exited with code %SCAN_RC% -- continuing with previous raw CSV if present.
    )
) else (
    echo [1/3] Skipping scan (mode=%MODE%); refresh_mobile_inventory.ps1 will pick the most recent RAW CSV.
    set SCAN_RC=0
)

echo.
REM ============================================================
REM Step 2: filter -> MOBILE_FILTERED.csv (or _SMOKE.csv in --smoke mode).
REM In --smoke / --no-scan mode, omit -RawCsv so the .ps1 fallback picks the
REM most recent RAW_PC_APPS_INVENTORY__*.csv (avoids passing a non-existent
REM placeholder path that would make the .ps1 fail with Test-Path).
REM ============================================================
echo [2/3] Filtering mobile terms and emitting %OUT_CSV% ...
if "%FORCE_SCAN%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0refresh_mobile_inventory.ps1" -RawCsv "%RAW_CSV%" -OutCsv "%OUT_CSV%"
) else (
    echo       (--smoke/--no-scan: -RawCsv omitted; .ps1 picks most recent RAW CSV)
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0refresh_mobile_inventory.ps1" -OutCsv "%OUT_CSV%"
)
set FILT_RC=%ERRORLEVEL%

echo.
REM ============================================================
REM Step 3: emit refresh_status.json (single-line JSON; readable by ConvertFrom-Json)
REM ============================================================
echo [3/3] Emitting refresh_status.json ...
echo {"timestamp":"%TS_HDR%","mode":"%MODE%","raw_csv":"%RAW_CSV%","out_csv":"%OUT_CSV%","scan_rc":%SCAN_RC%,"filter_rc":%FILT_RC%} > "%STATUS_JSON%"

echo.
if %FILT_RC% == 0 (
    echo PASS: mobile-inventory refresh succeeded.
    if "%MODE%"=="SMOKE" (
        echo       (smoke mode: review %OUT_CSV% then re-run without --smoke for production)
    ) else (
        echo       trigger `python war_room.py validate-mobile` to see dynamic tile count.
    )
) else (
    echo FAIL: filter step exited with code %FILT_RC% -- %OUT_CSV% may be stale.
)
echo       status JSON: %STATUS_JSON%
echo.
echo Done.
endlocal
