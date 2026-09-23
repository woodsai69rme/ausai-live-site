@echo off
:: bin/install_ALL_TASKS_AUDIT.bat -- smoke-test runner for the WarRoom
:: install + flag API surface. Runs every T0-T10 case from
:: bin\install_BOTH_TASKS_TEST_LOG.md + cont.16 --status extensions in
:: sequence, accumulates pass/fail, prints a one-line checklist, exits 0
:: only if all PASS.
::
:: Replaces the operator-driven "read the test log + run each command"
:: workflow with an executable one-shot. CI-friendly: returns non-zero on any FAIL.
::
:: Does NOT require elevation; runs only the non-elevated subset.
::
:: Usage:
::     bin\install_ALL_TASKS_AUDIT.bat

setlocal EnableDelayedExpansion

:: Ensure tmp/ exists for probe writes (T0 + T10)
if not exist tmp mkdir tmp

set "PASS_COUNT=0"
set "FAIL_COUNT=0"

echo.
echo ============================================================
echo  WarRoom install + flag API smoke test (T0-T13)
echo ============================================================
echo.

REM === T0: install_BOTH_TASKS.bat parse-probe (post-cont.16-fup migration) ===
echo [T 0] parse-probe install_BOTH_TASKS.bat (default arm)
copy bin\install_BOTH_TASKS.bat tmp\__audit_probe_both.bat >nul
powershell -NoProfile -Command "(Get-Content -Path 'tmp\__audit_probe_both.bat' -Raw) -replace 'setlocal', 'setlocal & exit /b 0' | Set-Content -Path 'tmp\__audit_probe_both.bat' -Encoding Default -NoNewline" >nul 2>&1
cmd /c "tmp\__audit_probe_both.bat" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (post-migration, parse-trip clean)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- migration left a v26 parse-trip
del "tmp\__audit_probe_both.bat" >nul 2>&1

REM === T1: ET parse both XMLs ===
echo [T 1] ET parse bin\nightly_snapshot.xml + bin\daily_trend_compare.xml
python -c "import xml.etree.ElementTree as ET; ET.parse(r'C:\Users\karma\bin\nightly_snapshot.xml'); ET.parse(r'C:\Users\karma\bin\daily_trend_compare.xml')" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- check for XML corruption

REM --- Fix 7 (cont.16-fup): all T2-T9 bat-invocation lines below use `cmd //c "..."` wrapping
REM     so the child bat does NOT replace the parent audit-runner shell (cmd.exe direct bat
REM     invocation replaces the parent -- the audit-runner would otherwise exit after T2
REM     and never run T3-T10). T0 + T10 still use `cmd /c "tmp\__audit_probe_*.bat"`
REM     because the probe stubs live in tmp\ and need cmd /c quote-handling too.
REM === T2: install_daily_trend_compare.bat --help ===
echo [T 2] bin\install_daily_trend_compare.bat --help
cmd //c "bin\install_daily_trend_compare.bat --help" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%)

REM === T3: install_daily_trend_compare.bat --dry-run ===
echo [T 3] bin\install_daily_trend_compare.bat --dry-run
cmd //c "bin\install_daily_trend_compare.bat --dry-run" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%)

REM === T4: install_daily_trend_compare.bat --uninstall (idempotent) ===
echo [T 4] bin\install_daily_trend_compare.bat --uninstall (idempotent 0)
cmd //c "bin\install_daily_trend_compare.bat --uninstall" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --uninstall must always exit 0

REM === T5: install_BOTH_TASKS.bat --help ===
echo [T 5] bin\install_BOTH_TASKS.bat --help
cmd //c "bin\install_BOTH_TASKS.bat --help" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%)

REM === T6: install_BOTH_TASKS.bat --dry-run ===
echo [T 6] bin\install_BOTH_TASKS.bat --dry-run
cmd //c "bin\install_BOTH_TASKS.bat --dry-run" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%)

REM === T7: install_BOTH_TASKS.bat --uninstall (idempotent) ===
echo [T 7] bin\install_BOTH_TASKS.bat --uninstall (idempotent 0)
cmd //c "bin\install_BOTH_TASKS.bat --uninstall" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --uninstall must always exit 0

REM === T8: install_daily_trend_compare.bat --status (NEW cont.16) ===
echo [T 8] bin\install_daily_trend_compare.bat --status (NEW cont.16)
cmd //c "bin\install_daily_trend_compare.bat --status" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --status must always exit 0

REM === T9: install_BOTH_TASKS.bat --status (NEW cont.16) ===
echo [T 9] bin\install_BOTH_TASKS.bat --status (NEW cont.16)
cmd //c "bin\install_BOTH_TASKS.bat --status" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --status must always exit 0

REM === T10: install_nightly_snapshot.bat parse-probe (post-cont.16 migration) ===
echo [T10] install_nightly_snapshot.bat parse-probe (post-cont.16 goto :label migration)
copy bin\install_nightly_snapshot.bat tmp\__audit_probe_nightly.bat >nul
powershell -NoProfile -Command "(Get-Content -Path 'tmp\__audit_probe_nightly.bat' -Raw) -replace 'setlocal', 'setlocal & exit /b 0' | Set-Content -Path 'tmp\__audit_probe_nightly.bat' -Encoding Default -NoNewline" >nul 2>&1
cmd /c "tmp\__audit_probe_nightly.bat" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (post-migration, parse-trip clean)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- migration left a v26 parse-trip
del "tmp\__audit_probe_nightly.bat" >nul 2>&1

REM === T11: install_nightly_snapshot.bat --help (NEW cont.16-fup-2) ===
echo [T11] bin\install_nightly_snapshot.bat --help (NEW cont.16-fup-2)
cmd //c "bin\install_nightly_snapshot.bat --help" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --help must always exit 0

REM === T12: install_nightly_snapshot.bat --dry-run (NEW cont.16-fup-4) ===
echo [T12] bin\install_nightly_snapshot.bat --dry-run (NEW cont.16-fup-4)
cmd //c "bin\install_nightly_snapshot.bat --dry-run" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --dry-run must always exit 0

REM === T13: install_nightly_snapshot.bat --uninstall (NEW cont.16-fup-4; idempotent) ===
echo [T13] bin\install_nightly_snapshot.bat --uninstall (NEW cont.16-fup-4)
cmd //c "bin\install_nightly_snapshot.bat --uninstall" >nul 2>&1
if not errorlevel 1 set /a "PASS_COUNT+=1" & echo         PASS (idempotent)
if     errorlevel 1 set /a "FAIL_COUNT+=1" & echo         FAIL (rc=%errorlevel%) -- --uninstall must always exit 0

REM --- Fix 8 (defensive runtime test-count assertion; codified in DESIGN_NOTES §9.5 candidate). ---
REM     If a future regression silently drops/inserts a T-n case, the runner
REM     would print `AUDIT: X PASS, Y FAIL (out of N tests)` for the wrong N
REM     without exiting non-zero -- masking the enumeration drift. Asserting
REM     the total here makes that future regression FAIL-LOUD instead.
REM     NOTE: cmd.exe `if` does STRING comparison, NOT arithmetic. We must
REM     evaluate `SET /A _TOTAL=!PASS_COUNT!+!FAIL_COUNT!` FIRST, then
REM     `if !_TOTAL! NEQ 11` compares the integer string. (Earlier draft used
REM     `if !PASS_COUNT!+!FAIL_COUNT! NEQ 11` directly which is a string
REM     concat -> ALWAYS trips because "11+0" != "11" → drift path always
REM     fires → wasted DEBUGGING cycles.)
set /a "_TOTAL=!PASS_COUNT!+!FAIL_COUNT!"
if !_TOTAL! NEQ 14 goto :audit_drift

echo.
echo ============================================================
echo  AUDIT: !PASS_COUNT! PASS, !FAIL_COUNT! FAIL (out of 14 tests)
echo ============================================================
echo.

goto :audit_summary_done

:audit_drift
echo.
echo ============================================================
echo  AUDIT: !PASS_COUNT! PASS, !FAIL_COUNT! FAIL (out of !_TOTAL! tests)
echo ============================================================
echo.
echo [FAIL] test enumeration drift -- expected 14 total tests, got !_TOTAL!.
echo        A T-n case was likely removed or added without updating the expected total.
echo        Update the assertion in this bat to match the new test count.
set /a "FAIL_COUNT+=1"

:audit_summary_done

if !FAIL_COUNT!==0 goto :audit_pass
echo [FAIL] !FAIL_COUNT! tests failed (including any enumeration drift). See bin\install_BOTH_TASKS_DESIGN_NOTES.md section 7 + TEST_LOG.md.
endlocal & exit /b 1

:audit_pass
echo [PASS] all non-elevated tests pass.
echo.
echo Elevated-gated cases (NOT run by this harness; see DESIGN_NOTES section 8):
echo   - bin\install_BOTH_TASKS.bat  :: default install (2x UAC prompts)
echo   - bin\verify_nightly_task.bat  :: WarRoomNightlySnapshot registered + enabled
echo   - bin\validate_daily_trend_compare.bat  :: fires WarRoomDailyTrendCompare + checks trend report materializes
echo.
endlocal & exit /b 0
