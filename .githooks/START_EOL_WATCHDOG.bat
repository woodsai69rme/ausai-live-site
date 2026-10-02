@echo off
REM START_EOL_WATCHDOG.bat -- one-shot advisory EOL drift check (added 2026-10-01).
REM Part of the EOL hygiene program; see .githooks/README.md v3.7.
REM Exit codes: 0 = OK, 1 = error, 2 = REGRESSION vs baseline (advisory only).
REM Examples:  START_EOL_WATCHDOG.bat            (run + print verdict)
REM            START_EOL_WATCHDOG.bat --quiet    (log only, silent)
REM            START_EOL_WATCHDOG.bat --init     (re-baseline after a settlement)
cd /d "%~dp0.."
python .githooks\eol_watchdog.py %*
exit /b %ERRORLEVEL%
