@echo off
:: bin/install_daily_trend_compare.bat -- install daily war_room trend-compare task
::
:: Operator runs ONCE interactively from an ELEVATED cmd.exe (Administrator):
::     cd C:\Users\karma
::     bin\install_daily_trend_compare.bat
::
:: Actions (all goto :label form per v26 fix; no ( ... ) blocks):
::     (no args)      -> install (requires elevated cmd)
::     --status       -> read-only Query task (idempotent; always rc=0)
::     --dry-run      -> print the WOULD-BE schtasks /Create invocation + exit 0
::     --uninstall    -> schtasks /Delete the task + exit 0
::     --help         -> flag inventory + exit 0 (cont.16+)
::
:: To uninstall without going through this bat:
::     schtasks /Delete /TN "WarRoomDailyTrendCompare" /F
::
:: To verify install + immediate fire:
::     bin\validate_daily_trend_compare.bat
::
:: Parameterization: this .bat reads bin/daily_trend_compare.xml and substitutes
:: the hardcoded `C:\Users\karma` with the actual %USERPROFILE% via PowerShell's
:: `.Replace()` (the .NET String literal-replace method) before passing to
:: `schtasks /Create /XML`.
::
:: Why `.Replace()` NOT `-replace`: PowerShell's `-replace` is a REGEX operator,
:: and the pattern `C:\Users\karma` would trigger `\U` (incomplete Unicode escape
:: in .NET regex -> `InvalidRegularExpression` runtime error). `.Replace()` is
:: the .NET String literal substring method -- no regex, no escape gymnastics.
:: Do NOT "simplify" this back to `-replace` or paths like `C:\Users` will
:: silently break again. (Lesson learned cont.18 MINOR #3.)
::
:: Why a separate task (not appended to nightly_snapshot.xml): Windows scheduled
:: tasks do support multiple <Exec> actions, but chaining them couples their
:: exit semantics. If snapshot-doctor fails, the trend-compare action would
:: still run (or vice versa) -- operator can't triage one without the other.
:: Two separate tasks = two independent failure surfaces = clearer post-mortem.
::
:: Why schtasks not Register-ScheduledTask (FU1 cont.13): PowerShell's
:: `Register-ScheduledTask -Xml` (CIM API) fails with "No mapping between
:: account names and security IDs" on this host. `schtasks /Create /XML` uses
:: the Win32 native API and resolves S-1-5-4 INTERACTIVE SID cleanly. The
:: PowerShell call in this .bat is ONLY for string substitution -- not for
:: the task-scheduler API.
::
:: Why all goto :label branches (NOT `if ... (` blocks): CMD `(...)` block parser
:: trips on multi-line echo statements that combine (a) a `^` line-continuation
:: AND (b) unquoted path-substitution that introduces a drive colon
:: (e.g. `%PYTHON%`, `%SCHTASKS_RC%`, `%PS_RC%`). Parser mistakes the unquoted
:: inline `(...)` for nested block start -> `: was unexpected at this time.`
:: Lesson applied: v26-style goto :label form throughout.
::
:: Schedule: 23:59 daily (4 minutes after WarRoomNightlySnapshot at 23:55, so
:: the trend-compare has a fresh 1d/7d snapshot set to compare against). The
:: 4-min buffer (was 2 min) covers slow-disk snapshots where the snapshot's
:: last-write > 30s after the task fires. Operators wanting tighter cadence can
:: move both tasks earlier; for normal CI cadence 23:55 + 23:59 is the right
:: rhythm (nightly run + daily-rate digest at the top of the hour).
::
:: Prereq: daily_trend_compare.xml sits next to this .bat (in C:\Users\karma\bin\).
:: To verify post-install: bin\validate_daily_trend_compare.bat (fires task,
:: waits WAIT_SECONDS, checks for new .md report under outbox/trend_reports).

setlocal

set "TEMPLATE=%~dp0daily_trend_compare.xml"
set "TMP_XML=%TEMP%\war_room_daily_trend_compare_%RANDOM%.xml"
set "TMP_PS_OUT=%TEMP%\war_room_ps_sub_%RANDOM%.txt"
set "TASK_NAME=WarRoomDailyTrendCompare"

if not exist "%TEMPLATE%" goto :no_template

:: --- Dispatch on first arg BEFORE any side-effects ---
:: All five branches (do_help / do_install / do_dry_run / do_uninstall / do_status) gate
:: on `if /i "%~1"==...` and goto :label; the install branch is the default
:: (no arg matching falls through).
if /i "%~1"=="--help"      goto :show_help
if /i "%~1"=="--status"    goto :do_status
if /i "%~1"=="--dry-run"   goto :do_dry_run
if /i "%~1"=="--uninstall" goto :do_uninstall

:: ============================================================
:: do_install (default; no --dry-run / --uninstall)
:: ============================================================
:do_install
echo.
echo Installing scheduled task "%TASK_NAME%":
echo   template:   %TEMPLATE%
echo   USERPROFILE: %USERPROFILE%
echo   (substituting hardcoded C:\Users\karma with %USERPROFILE% for portability)
echo.

REM PowerShell error capture (cont.18 MINOR #1 pattern): redirect stdout+stderr to a
REM file so we can surface PowerShell's actual error message; capture %errorlevel% to
REM a variable IMMEDIATELY (before any subsequent command resets it). Do NOT pipe
REM (`powershell ... |`) because cmd.exe pipe spawns a subshell that can mask the
REM left-hand process's exit code.
powershell -NoProfile -Command "(Get-Content -Path '%TEMPLATE%' -Raw -Encoding Unicode).Replace('C:\Users\karma', '%USERPROFILE%') | Set-Content -Path '%TMP_XML%' -Encoding Unicode -NoNewline" > "%TMP_PS_OUT%" 2>&1
set "PS_RC=%errorlevel%"
if not "%PS_RC%"=="0" goto :ps_fail
if exist "%TMP_PS_OUT%" del "%TMP_PS_OUT%"

REM Validate temp XML actually exists before schtasks call (cont.18 MINOR #2 pattern).
if not exist "%TMP_XML%" goto :no_tmp_xml

REM --- Pre-flight (enhance-all round 2026-07-09): XML schema validation via throwaway test task ---
REM Task Scheduler v1.2 schema enforces a strict node-order sequence (RegistrationInfo >
REM Triggers > Settings > Data > Principal > Actions). `schtasks /Create /XML` validates
REM internally and emits "ERROR: The task XML contains an unexpected node at (line,col):
REM <node>" when violated. Without this pre-flight, operators see the error AT the real
REM install call (a confusing "rc=1, re-run from elevated cmd.exe" hint that may mask the
REM actual template-level schema bug). With this pre-flight, schema errors surface BEFORE
REM any elevation check AND before the real `WarRoomDailyTrendCompare` task is created,
REM with the literal schtasks error message visible so the operator can fix the XML.
REM The test task uses `TASK_NAME.SchemaTest.%RANDOM%` and is deleted immediately on
REM success. If the test fails OR this bat is killed before cleanup, the test task may
REM linger; the failure banner shows the cleanup command.
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
echo   bin\validate_daily_trend_compare.bat
echo.
echo To test immediately (does NOT wait for 23:59 trigger):
echo   schtasks /Run /TN "%TASK_NAME%"
echo.
echo To see the captured report afterwards:
echo   dir /od /b "%USERPROFILE%\SLEEP_TRIPLE\outbox\trend_reports\report__*.md"
echo.

endlocal
exit /b 0

:: ============================================================
:: --dry-run branch (safe preview; no scheduler changes)
:: ============================================================
:do_dry_run
echo.
echo [DRY-RUN] WarRoomDailyTrendCompare (no install will happen)
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
echo   Schedule:   23:59 daily (4 min after WarRoomNightlySnapshot at 23:55)
echo   Action:   python war_room.py launch-trend-compare --emit-report
echo                 --alert-on-degraded --strict-alert-rc --a 1d --b 7d
echo.
echo [PASS] dry-run OK -- no scheduler changes made. Re-run WITHOUT
echo        --dry-run from an ELEVATED cmd.exe (Administrator) to install.
endlocal
exit /b 0

:: ============================================================
:: --uninstall branch (symmetric idempotent UX like --dry-run)
:: ============================================================
:: Migration note (cont.16-fup): this arm was the LAST multi-line (...) block in any of
:: the 3 installers. cmd parses the WHOLE bat upfront (v26 lesson), so even though --uninstall
:: isn't reached in T0/T2/T5 stub paths, this block tripped any future parse-stress. Mirrors
:: the nightly + BOTH_TASKS :do_uninstall migrations: `if "(X)"=="0" ( ... ) else ( ... )`
:: -> `if "(X)"=="0" goto :label` + fall-through INFO block + 2 success/after labels.
:do_uninstall
echo.
echo [UNINSTALL] WarRoomDailyTrendCompare
echo.
schtasks /Delete /TN "%TASK_NAME%" /F
set "DEL_RC=%errorlevel%"
if "%DEL_RC%"=="0" goto :uninstall_daily_passed
echo [INFO] task was not installed or not deletable; rc=%DEL_RC%
echo        (no install was removed; this is symmetric with --dry-run's idempotent UX)
goto :uninstall_daily_after

:uninstall_daily_passed
echo [PASS] task deleted.

:uninstall_daily_after
endlocal
exit /b 0

:: ============================================================
:: --status branch (cont.16; safe read-only idempotent UX)
:: ============================================================
:do_status
echo.
echo [STATUS] WarRoomDailyTrendCompare
echo.
schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
set "QUERY_RC=%errorlevel%"
if "%QUERY_RC%"=="0" goto :status_registered_daily

echo.
echo [INFO] task not currently registered (rc=%QUERY_RC% -- task absent is idempotent-success).
endlocal
exit /b 0

:status_registered_daily
echo.
echo [INFO] task registered (rc=0). Use schtasks /Run to test-fire.
endlocal
exit /b 0

:: ============================================================
:: Error labels (all goto :label form to avoid v26 `(...)` parse-trip)
:: ============================================================
:no_template
echo [FAIL] %TEMPLATE% not found
echo        Hint: daily_trend_compare.xml should sit next to this .bat
endlocal
exit /b 1

:ps_fail
echo [FAIL] PowerShell substitution failed, errorlevel %PS_RC%:
if exist "%TMP_PS_OUT%" type "%TMP_PS_OUT%"
if exist "%TMP_XML%" del "%TMP_XML%"
if exist "%TMP_PS_OUT%" del "%TMP_PS_OUT%"
endlocal
exit /b 1

:no_tmp_xml
echo [FAIL] temp XML %TMP_XML% was not written; PowerShell substitution may have failed silently.
endlocal
exit /b 1

:schema_fail
echo.
echo [FAIL] XML schema validation failed; schtasks rejected with rc=%TEST_RC%:
if exist "%TMP_PS_OUT%" type "%TMP_PS_OUT%"
echo        This is a TEMPLATE-level error in bin\daily_trend_compare.xml; fix the
echo        XML node-ordering (Task Scheduler v1.2 expects: RegistrationInfo ^
echo        Triggers ^> Settings ^> Data ^> Principal ^> Actions) before re-installing.
echo        If the error is about ACCESS DENIED rather than schema, the current
echo        shell is not elevated -- ignore this pre-flight and re-run from an
echo        elevated cmd.exe (the real install still requires elevation regardless).
echo        If the error says "value which is incorrectly formatted or out of range",
echo        schtasks is rejecting a value inside the XML (UserId / LogonType / RunLevel /
echo        Task version attribute -- see CHANGELOG ## 2026-07-09 (cont.13+) for the
echo        recent value-validation rounds). FALLBACK: open Task Scheduler GUI,
echo        click "Import Task...", select bin\daily_trend_compare.xml, then in
echo        "Security Options" set "Run as" to your actual DOMAIN\User with
echo        "Run whether user is logged on or not" unchecked. Save with name
echo        "%TASK_NAME%". This bypasses schtasks' static-XML value checking.
echo        Test task "%TEST_TASK_NAME%" may still exist; cleanup with:
echo          schtasks /Delete /TN "%TEST_TASK_NAME%" /F
if exist "%TMP_XML%" del "%TMP_XML%"
if exist "%TMP_PS_OUT%" del "%TMP_PS_OUT%"
endlocal
exit /b 1

:schtasks_fail
echo.
echo [FAIL] schtasks /Create returned errorlevel %SCHTASKS_RC%.
echo        Hint: re-run from an ELEVATED cmd.exe (Administrator).
endlocal
exit /b 1

:: ============================================================
:: --help branch (cont.16+; safe read-only idempotent UX)
:: ============================================================
:show_help
echo.
echo bin\install_daily_trend_compare.bat -- install daily war_room trend-compare task
echo.
echo Usage:
echo     bin\install_daily_trend_compare.bat             :: install (requires elevated cmd.exe)
echo     bin\install_daily_trend_compare.bat --status    :: read-only Query (always rc=0)
echo     bin\install_daily_trend_compare.bat --dry-run   :: preview; no scheduler changes
echo     bin\install_daily_trend_compare.bat --uninstall :: delete task
echo     bin\install_daily_trend_compare.bat --help      :: this message
echo.
echo See bin\install_BOTH_TASKS_DESIGN_NOTES.md section 7 for design context.
endlocal
exit /b 0
