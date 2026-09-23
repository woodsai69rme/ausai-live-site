@echo off
:: bin/install_AUDIT_scheduler.bat -- install daily WarRoomDailyAuditPreFlight scheduled task
::
:: Operator runs ONCE interactively from an ELEVATED cmd.exe (Administrator):
::     cd C:\Users\karma
::     bin\install_AUDIT_scheduler.bat
::
:: To uninstall:
::     schtasks /Delete /TN "WarRoomDailyAuditPreFlight" /F
::
:: To verify install:
::     schtasks /Query /TN "WarRoomDailyAuditPreFlight" /V /FO LIST
::
:: Actions (all goto :label form per v26 fix; no ( ... ) blocks):
::     (no args)      -> install (requires elevated cmd)
::     --dry-run      -> print the WOULD-BE schtasks /Create invocation + exit 0
::     --uninstall    -> schtasks /Delete the task + exit 0  (idempotent; rc=0 even if task absent)
::     --status       -> read-only Query task (idempotent; always rc=0)
::     --help         -> flag inventory + exit 0
::
:: Task summary (cont.16-fup-5):
::   Name:    WarRoomDailyAuditPreFlight
::   Trigger: Daily at 06:00 (morning coffee pre-flight, BEFORE WarRoomDailyTrendCompare at 23:59)
::            and BEFORE WarRoomNightlySnapshot at 23:55 so failures surface during the day.
::   Action:  bin\dist\run_audit_subprocess.exe --cmd "bin\install_ALL_TASKS_AUDIT.bat" --log-timestamp
::            (logging + deadlock avoidance inherited from fup-3 wrapper.
::             The .exe is built once via `bin\build_audit_exe.bat --rebuild`
::             via PyInstaller --onefile; does NOT require Python at runtime.
::             Manual `python bin\run_audit_subprocess.py ...` invocations still
::             work as a drop-in for ad-hoc operator use.)
::   Prereq:  audit_scheduler.xml sits next to this .bat (in C:\Users\karma\bin\).
::
:: Parameterization (cont.17 + cont.18 MINOR #3, mirror install_nightly_snapshot.bat):
:: this .bat reads bin/audit_scheduler.xml and substitutes the hardcoded
:: `C:\Users\karma` with the actual %USERPROFILE% via PowerShell's `.Replace()`
:: (the .NET String literal-replace method) before passing to `schtasks /Create /XML`.

setlocal

set "TEMPLATE=%~dp0audit_scheduler.xml"
set "TMP_XML=%TEMP%\war_room_audit_scheduler_%RANDOM%.xml"
set "TMP_PS_OUT=%TEMP%\war_room_ps_sub_%RANDOM%.txt"
set "TASK_NAME=WarRoomDailyAuditPreFlight"

:: --- Flag dispatch (cont.16+; --help / --status / --dry-run / --uninstall) ---
if /i "%~1"=="--help"      goto :show_help
if /i "%~1"=="--status"    goto :do_status
if /i "%~1"=="--dry-run"   goto :do_dry_run
if /i "%~1"=="--uninstall" goto :do_uninstall

:: --- Self-elevate to Administrator if not already elevated (cont.16-fup-3+fup-5 followup; mirror of install_monitor_scheduler.bat v24) ---
:: Skipped for --help / --status / --dry-run / --uninstall (the 4 goto arms above exit before reaching this block, EXCEPT :do_uninstall which redundantly re-checks below).
:: Required for the install path (default invocation without flags) since schtasks /Create needs admin.
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [install_AUDIT_scheduler] Not running as Administrator; re-launching elevated...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0' -ArgumentList '%*'"
    endlocal
    exit /b
)

if not exist "%TEMPLATE%" goto :no_template

echo.
echo Installing scheduled task "%TASK_NAME%":
echo   template:   %TEMPLATE%
echo   USERPROFILE: %USERPROFILE%
echo   (substituting hardcoded C:\Users\karma with %USERPROFILE% for portability)
echo.

REM MINOR #1 (cont.18): PowerShell error capture. Redirect stdout+stderr to a file so
REM we can surface PowerShell's actual error message; capture %errorlevel% to a variable
REM IMMEDIATELY (before any subsequent command resets it). Do NOT pipe (`powershell ... |`)
REM because cmd.exe pipe spawns a subshell that can mask the left-hand process's exit code.
powershell -NoProfile -Command "(Get-Content -Path '%TEMPLATE%' -Raw -Encoding Unicode).Replace('C:\Users\karma', '%USERPROFILE%') | Set-Content -Path '%TMP_XML%' -Encoding Unicode -NoNewline" > "%TMP_PS_OUT%" 2>&1
set "PS_RC=%errorlevel%"
if not "%PS_RC%"=="0" goto :ps_fail
if exist "%TMP_PS_OUT%" del "%TMP_PS_OUT%"

REM MINOR #2 (cont.18): validate temp XML actually exists before schtasks call. Catches
REM silent PowerShell failures (e.g. if .Replace() returned an empty string for some reason).
if not exist "%TMP_XML%" goto :no_tmp_xml

REM --- Pre-flight schema validation (cont.14, mirror install_nightly_snapshot.bat) ---
REM Task Scheduler v1.2 schema enforces a strict node-order sequence. Without this pre-flight,
REM a hidden template-level schema error would surface AT the real install as a confusing
REM rc=1 hint that masks the failure mode. With it, schema errors surface BEFORE any elevation
REM check with the literal schtasks error message visible. The test task uses
REM %TASK_NAME%.SchemaTest.%RANDOM% and is deleted on success; on rejection the cleanup
REM hint is printed in the :schema_fail banner (see below).
set "TEST_TASK_NAME=%TASK_NAME%.SchemaTest.%RANDOM%"
schtasks /Create /XML "%TMP_XML%" /TN "%TEST_TASK_NAME%" /F > "%TMP_PS_OUT%" 2>&1
set "TEST_RC=%errorlevel%"
if not "%TEST_RC%"=="0" goto :schema_fail
schtasks /Delete /TN "%TEST_TASK_NAME%" /F >nul 2>&1
echo [PASS] XML schema validation OK (test task created + cleaned up).

schtasks /Create /XML "%TMP_XML%" /TN "%TASK_NAME%"
set "SCHTASKS_RC=%errorlevel%"
if exist "%TMP_XML%" del "%TMP_XML%"

if not "%SCHTASKS_RC%"=="0" goto :schtasks_fail

echo.
echo [PASS] installed. Verify with:
echo   schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
echo.
echo To test immediately (does NOT wait for 06:00 trigger):
echo   schtasks /Run /TN "%TASK_NAME%"
echo.
echo To see the captured stdout afterwards:
echo   type tmp\_wrap_out.txt
echo.
endlocal
exit /b 0

:no_template
echo [FAIL] %TEMPLATE% not found
echo        Hint: audit_scheduler.xml should sit next to this .bat
endlocal
exit /b 1

:ps_fail
echo [FAIL] PowerShell substitution failed (errorlevel %PS_RC%):
if exist "%TMP_PS_OUT%" type "%TMP_PS_OUT%"
if exist "%TMP_XML%" del "%TMP_XML%"
if exist "%TMP_PS_OUT%" del "%TMP_PS_OUT%"
endlocal
exit /b 1

:no_tmp_xml
echo [FAIL] temp XML %TMP_XML% was not written; PowerShell substitution may have failed silently.
endlocal
exit /b 1

:schtasks_fail
echo.
echo [FAIL] schtasks /Create returned errorlevel %SCHTASKS_RC%.
echo        Hint: re-run from an ELEVATED cmd.exe (Administrator).
endlocal
exit /b 1

:do_dry_run
echo.
echo [DRY-RUN] WarRoomDailyAuditPreFlight (no install will happen)
echo.
echo   template:   %TEMPLATE%
echo   USERPROFILE: %USERPROFILE%
echo   action:     substitute hardcoded C:\Users\karma
echo                 with %USERPROFILE% in the XML template
echo                 then run schtasks /Create.
echo.
echo   WOULD-BE invocation (after substitution):
echo     schtasks /Create /XML "%TEMPLATE%" /TN "%TASK_NAME%"
echo.
echo   Schedule:   06:00 daily (morning coffee pre-flight,
echo                 BEFORE WarRoomNightlySnapshot 23:55 and
echo                 WarRoomDailyTrendCompare 23:59)
echo   Action:   bin\dist\run_audit_subprocess.exe --cmd "bin\install_ALL_TASKS_AUDIT.bat" --log-timestamp
echo            (uses the fup-3 cross-platform wrapper packaged via PyInstaller
echo            --onefile in cont.16-fup-6; --log-timestamp prepends an ISO
echo            timestamp to tmp\_wrap_out.txt so daily traces are chrono-sorted.)
echo.
echo [PASS] dry-run OK -- no scheduler changes made. Re-run WITHOUT
echo        --dry-run from an ELEVATED cmd.exe (Administrator) to install.
endlocal
exit /b 0

:: ============================================================
:: --uninstall branch (symmetric idempotent UX like --dry-run)
:: ============================================================
:: NOTE (cont.16-fup-3+fup-5 followup): self-elevate check is duplicated here because
:: --uninstall does `goto :do_uninstall` from the dispatcher, which jumps past the
:: post-dispatcher auto-elevate block above. Re-checking at the top of :do_uninstall
:: ensures --uninstall also auto-elevates BEFORE invoking schtasks /Delete (which
:: also requires admin).
:do_uninstall
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [install_AUDIT_scheduler] Not running as Administrator; re-launching elevated...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0' -ArgumentList '%*'"
    endlocal
    exit /b
)
echo.
echo [UNINSTALL] WarRoomDailyAuditPreFlight
echo.
schtasks /Delete /TN "%TASK_NAME%" /F
set "DEL_RC=%errorlevel%"
if "%DEL_RC%"=="0" goto :uninstall_audit_passed

echo [INFO] task was not installed or not deletable; rc=%DEL_RC%
echo        (no install was removed; this is symmetric with --dry-run's idempotent UX)
goto :uninstall_audit_after

:uninstall_audit_passed
echo [PASS] task deleted.

:uninstall_audit_after
endlocal
exit /b 0

:do_status
echo.
echo [STATUS] WarRoomDailyAuditPreFlight
echo.
schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
set "QUERY_RC=%errorlevel%"
if "%QUERY_RC%"=="0" goto :status_registered_audit

echo.
echo [INFO] task not currently registered (rc=%QUERY_RC% -- task absent is idempotent-success).
endlocal
exit /b 0

:status_registered_audit
echo.
echo [INFO] task registered (rc=0). Use schtasks /Run to test-fire.
endlocal
exit /b 0


:schema_fail
echo.
echo [FAIL] XML schema validation failed; schtasks rejected with rc=%TEST_RC%:
if exist "%TMP_PS_OUT%" type "%TMP_PS_OUT%"
echo        This is a TEMPLATE-level error in bin\audit_scheduler.xml; fix the
echo        XML node-ordering (Task Scheduler v1.2 expects: RegistrationInfo ^
echo        Triggers ^> Principals ^> Settings ^> Actions) before re-installing.
echo        If the error says "value which is incorrectly formatted or out of range",
echo        schtasks is rejecting a value inside the XML (UserId / Task version attribute).
echo        See CHANGELOG ## 2026-07-09 (cont.13+) for the recent value-validation rounds;
echo        cont.16-fup-3 added bin\run_audit_subprocess.py as a cross-platform
echo        deadlock-free wrapper which is what this task's action invokes.
echo        FALLBACK: open Task Scheduler GUI, click "Import Task...", select
echo        bin\audit_scheduler.xml, then in "Security Options" set "Run as" to your
echo        actual operator user. Save with name "%TASK_NAME%". This bypasses
echo        schtasks static-XML value checking.
echo        Test task "%TEST_TASK_NAME%" may still exist; cleanup with:
echo          schtasks /Delete /TN "%TEST_TASK_NAME%" /F
if exist "%TMP_XML%" del "%TMP_XML%"
if exist "%TMP_PS_OUT%" del "%TMP_PS_OUT%"

endlocal

:: ============================================================
:: --help branch (cont.16+; safe read-only idempotent UX)
:: ============================================================
:show_help
echo.
echo bin\install_AUDIT_scheduler.bat -- install daily WarRoomDailyAuditPreFlight task
echo.
echo Usage:
echo     bin\install_AUDIT_scheduler.bat             :: install (auto-elevates; requires admin consent at UAC prompt)
echo     bin\install_AUDIT_scheduler.bat --status    :: read-only Query (always rc=0)
echo     bin\install_AUDIT_scheduler.bat --dry-run   :: preview; no scheduler changes
echo     bin\install_AUDIT_scheduler.bat --uninstall :: delete task (auto-elevates; idempotent; rc=0 even if absent)
echo     bin\install_AUDIT_scheduler.bat --help      :: this message
echo.
echo Execution-time budget: 5 minutes (PT5M) -- the WarRoomDailyAuditPreFlight task
echo Action runs `bin\dist\run_audit_subprocess.exe --cmd "bin\install_ALL_TASKS_AUDIT.bat"
echo --log-timestamp --keep`, which completes in ~25-30s on this MINGW host (vs ~0.91s
echo native cmd /c; wrapper adds ~25s of internal cmd //c overhead). 5 minutes gives
echo ~10x margin for slower hosts.
echo.
echo See bin\install_AUDIT_scheduler_RUNBOOK.md for the operator runbook.
echo See bin\install_BOTH_TASKS_DESIGN_NOTES.md section 7 for design context.
echo.
echo Build prerequisite (cont.16-fup-6): the action requires bin\dist\run_audit_subprocess.exe
echo to exist. Build it ONCE via `bin\build_audit_exe.bat --rebuild` (PyInstaller --onefile).
echo Until then, the legacy `python bin\run_audit_subprocess.py` invocation works as fallback.
endlocal
exit /b 0
