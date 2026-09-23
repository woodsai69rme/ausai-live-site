@echo off
:: bin/install_BOTH_TASKS.bat -- one-shot cascade installer for both WarRoom scheduled
:: tasks, with flag API mirroring bin\install_daily_trend_compare.bat (v27 migrate:
:: goto :label form throughout the cascade -- including the 2 PASS/FAIL gates in :do_install;
:: mirrors the sibling bat's documented v26 lesson that `(...)` blocks trip cmd.exe parse).
::
:: Operator runs from any cmd.exe (does not need to be elevated up-front -- each
:: sub-install handles its own UAC prompt internally via PowerShell Start-Process -Verb
:: RunAs in the individual installers).
::
:: Flag API (all goto :label form; no `(...)` parse-trip):
::     (no args)      -> cascade install (daily THEN nightly) with PASS/FAIL gate.
::     --dry-run      -> print WOULD-BE invocations for both sub-installs + a
::                       copy-pasteable PowerShell one-liner to exercise the
::                       nightly schema pre-flight from an ELEVATED cmd.exe. No
::                       scheduler changes made.
::     --uninstall    -> call install_daily_trend_compare.bat --uninstall +
::                       raw schtasks /Delete /TN "WarRoomNightlySnapshot" /F.
::                       Idempotent: silently no-op on tasks already absent.
::     --help         -> print this header + flag inventory.
::
:: To verify after install:
::     bin\verify_nightly_task.bat
::     bin\validate_daily_trend_compare.bat
::
:: Why this exists (cont.14 followup): the operator had to manually chain the 2
:: installs in the runbook, plus remember the UAC prompt flow + verify + uninstall
:: commands. The dispatcher consolidates the cascade so the operator only needs to
:: click 'Yes' on each UAC prompt as it appears. Failure of either sub-install
:: aborts the cascade so a half-installed state is never confused with a
:: fully-installed state.

setlocal

:: --- Dispatch on first arg BEFORE any side-effects ---
if /i "%~1"=="--help"      goto :show_help
if /i "%~1"=="--status"    goto :do_status
if /i "%~1"=="--dry-run"   goto :do_dry_run
if /i "%~1"=="--uninstall" goto :do_uninstall
goto :do_install

:: ============================================================
:: DEFAULT :: cascade install (daily THEN nightly) with PASS/FAIL gate
:: ============================================================
:do_install
echo.
echo ============================================================
echo  Cascade: install both WarRoom scheduled tasks
echo ============================================================
echo.
echo  Step 1/2: WarRoomDailyTrendCompare (23:59 daily, trend-compare report)
echo           A UAC prompt will appear. Click 'Yes'.
echo.

call bin\install_daily_trend_compare.bat
if not errorlevel 1 goto :after_daily_install

echo.
echo [FAIL] daily install failed; aborting cascade.
echo        To retry just daily:     bin\install_daily_trend_compare.bat
echo        To uninstall:            bin\install_daily_trend_compare.bat --uninstall
exit /b 1

:after_daily_install

echo.
echo  Step 2/2: WarRoomNightlySnapshot (23:55 daily, snapshot-doctor)
echo           A UAC prompt will appear. Click 'Yes'.
echo.

call bin\install_nightly_snapshot.bat
if not errorlevel 1 goto :after_nightly_install

echo.
echo [FAIL] nightly install failed; the DAILY task IS already installed.
echo        To uninstall daily:       bin\install_daily_trend_compare.bat --uninstall
echo        Raw fallback (if --uninstall.bat is broken):
echo                                  schtasks /Delete /TN "WarRoomDailyTrendCompare" /F
echo        Then re-run this bat for the cascade to complete.
exit /b 1

:after_nightly_install

echo.
echo ============================================================
echo  [PASS] both tasks installed.
echo ============================================================
echo.
echo  Verify:
echo    bin\verify_nightly_task.bat              :: WarRoomNightlySnapshot registered + enabled
echo    bin\validate_daily_trend_compare.bat     :: fires WarRoomDailyTrendCompare + checks trend report materializes
echo.
echo  Live test-fire (does NOT wait for 23:55 / 23:59 triggers):
echo    schtasks /Run /TN "WarRoomNightlySnapshot"
echo    schtasks /Run /TN "WarRoomDailyTrendCompare"
echo.
echo  Uninstall (symmetric + idempotent; --uninstall flag does both in one go):
echo    bin\install_BOTH_TASKS.bat --uninstall
echo.
endlocal
exit /b 0

:: ============================================================
:: --status :: read-only idempotent Query both tasks (cont.16)
:: ============================================================
:do_status
echo.
echo [STATUS] cascade (both WarRoom tasks)
echo.
echo   Step 1/2: WarRoomDailyTrendCompare
schtasks /Query /TN "WarRoomDailyTrendCompare" /V /FO LIST
set "STATUS_DAILY_RC=%errorlevel%"
echo.
echo   Step 2/2: WarRoomNightlySnapshot
schtasks /Query /TN "WarRoomNightlySnapshot" /V /FO LIST
set "STATUS_NIGHTLY_RC=%errorlevel%"
echo.
echo   [INFO] daily rc=%STATUS_DAILY_RC% (0=present, non-zero=absent)
echo          nightly rc=%STATUS_NIGHTLY_RC% (same)
echo          both rc=0 + install verified; both rc!=0 + uninstall verified; mixed + half-state.
echo          --status always exits 0 (idempotent read-only).
endlocal
exit /b 0

:: ============================================================
:: --dry-run :: safe preview; no scheduler changes
:: ============================================================
:do_dry_run
echo.
echo [DRY-RUN] cascade install (no scheduler changes will happen)
echo.
echo ------------------------------------------------------------
echo  Step 1/2 (real --dry-run via sub-bat)
echo ------------------------------------------------------------
call bin\install_daily_trend_compare.bat --dry-run
if errorlevel 1 goto :dry_daily_fail

echo.
echo ------------------------------------------------------------
echo  Step 2/2 (synthetic preview -- nightly bat has NO --dry-run flag)
echo ------------------------------------------------------------
echo.
echo   template:   bin\nightly_snapshot.xml
echo   USERPROFILE: %USERPROFILE%
echo   action:     substitute hardcoded C:\Users\karma
echo                 with %USERPROFILE% in the XML template
echo                 then run schtasks /Create.
echo.
echo   WOULD-BE invocation (after substitution):
echo     schtasks /Create /XML "<TEMP>\war_room_nightly_snapshot_*.xml" /TN "WarRoomNightlySnapshot"
echo.
echo   Schedule:  23:55 daily (4 min BEFORE WarRoomDailyTrendCompare at 23:59)
echo   Action:    python war_room.py snapshot-doctor --emit-diff-then-trend
echo.
echo ------------------------------------------------------------
echo  OPTIONAL: exercise the actual schema pre-flight (only from
echo  an ELEVATED cmd.exe; the bat itself runs this in the real
echo  install arm before `schtasks /Create`). Paste these 2 lines:
echo ------------------------------------------------------------
echo    $xml = Join-Path $env:TEMP 'preview_nightly.xml'; Copy-Item bin\nightly_snapshot.xml $xml
echo    $tn = 'PreviewNightly_' + [Guid]::NewGuid().ToString('N'); schtasks /Create /XML $xml /TN $tn /F; schtasks /Delete /TN $tn /F
echo.
echo [PASS] dry-run OK -- no scheduler changes made. Re-run WITHOUT
echo        --dry-run from an ELEVATED cmd.exe (each sub-install
echo        self-elevates; only one operator UAC click per task).
endlocal
exit /b 0

:dry_daily_fail
echo [FAIL] daily --dry-run returned non-zero; aborting dry-run cascade.
endlocal
exit /b 1

:: ============================================================
:: --uninstall :: symmetric, idempotent
:: ============================================================
:do_uninstall
echo.
echo [UNINSTALL] cascade (deletes both tasks)
echo.

echo   Step 1/2: WarRoomDailyTrendCompare
call bin\install_daily_trend_compare.bat --uninstall
set "DAILY_DEL_RC=%errorlevel%"

echo.
echo   Step 2/2: WarRoomNightlySnapshot
schtasks /Delete /TN "WarRoomNightlySnapshot" /F
set "NIGHTLY_DEL_RC=%errorlevel%"

echo.
if "%DAILY_DEL_RC%"=="0"   goto :uninstall_daily_ok
echo [INFO] daily rc=%DAILY_DEL_RC%; nightly rc=%NIGHTLY_DEL_RC%
echo        (rc=1 from either is expected in non-elevated shells; re-run from
echo         an ELEVATED cmd.exe for full cleanup.)
goto :uninstall_after_status

:uninstall_daily_ok
if "%NIGHTLY_DEL_RC%"=="0" goto :uninstall_both_deleted
echo [INFO] daily deleted (rc=0); nightly rc=%NIGHTLY_DEL_RC% (often rc=1 because nightly /Delete needs elevation; run uninstall from an ELEVATED cmd.exe for the raw /Delete to actually succeed).
goto :uninstall_after_status

:uninstall_both_deleted
echo [PASS] both tasks deleted.

:uninstall_after_status
endlocal
exit /b 0

:: ============================================================
:: --help :: flag inventory
:: ============================================================
:show_help
echo.
echo bin\install_BOTH_TASKS.bat -- one-shot cascade for WarRoom scheduled tasks
echo.
echo Usage:
echo     bin\install_BOTH_TASKS.bat            :: cascade install (daily then nightly)
echo     bin\install_BOTH_TASKS.bat --status   :: read-only Query both tasks (always rc=0)
echo     bin\install_BOTH_TASKS.bat --dry-run  :: preview; no scheduler changes
echo     bin\install_BOTH_TASKS.bat --uninstall :: delete both tasks
echo     bin\install_BOTH_TASKS.bat --help     :: this message
echo.
echo See bin\install_BOTH_TASKS_TEST_LOG.md for the testable-subset verification log.
echo See CHANGELOG.md ## 2026-07-09 (cont.14) for the upstream context.
endlocal
exit /b 0
