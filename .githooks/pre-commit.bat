@echo off
REM .githooks\pre-commit.bat
REM Windows cmd.exe -- thin wrapper v2 (FIX 1 from v3.3.1 review).
REM Single source of truth for Stage A + B verification logic lives in
REM bin\precommit_check.bat; this file just ensures the wrapped exit code
REM propagates correctly back to git's hook subprocess.
REM
REM FIX 1: `setlocal enabledelayedexpansion` + capture !ERRORLEVEL! BEFORE
REM popd. Without delayed expansion, `set RC=%ERRORLEVEL%` parsed at parse
REM time (returning 0 -- cmd.exe's value before the call). Worse: even with
REM delayed expansion, capturing AFTER popd would be wrong because popd
REM resets ERRORLEVEL on success. Result: the wrapped .bat's exit code
REM was being silently discarded, always returning 0 to git. The hook ran
REM but its FAIL verdicts were invisible -- exactly the regression this
REM round was supposed to fix.

setlocal enabledelayedexpansion

pushd "%~dp0\..\"
call "bin\precommit_check.bat" %*
REM Capture BEFORE popd (cmd.exe's popd resets ERRORLEVEL on success).
set "RC=!ERRORLEVEL!"
popd

REM endlocal escape: %RC% pre-expands (inner-scope value) at parse time,
REM then endlocal discards inner scope, then `& set FINAL_RC=<literal>`
REM re-assigns in outer scope. Preserves captured rc across setlocal boundary.
endlocal & set "FINAL_RC=%RC%"
exit /b %FINAL_RC%
