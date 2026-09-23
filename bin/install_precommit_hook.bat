@echo off
REM bin\install_precommit_hook.bat
REM One-shot installer for the .githooks/ pre-commit hook v2 (v3.3.1).
REM
REM Sets `git config core.hooksPath .githooks` so git invokes
REM .githooks\pre-commit (which delegates to pre-commit.bat on Windows)
REM instead of the default .git/hooks/ lookup.
REM
REM Idempotent: re-running reports current state without re-installing.
REM Reversible: `git config --unset core.hooksPath` reverts cleanly.
REM
REM Husky-coexistence (FIX 3 v2): if core.hooksPath = .husky is already
REM set, this script prints a multi-line WARNING and asks for explicit
REM [Y/N] confirmation BEFORE overriding. Operators in CI scripts that
REM want to install without being prompted can set FORCE_OVERRIDE=1.
REM
REM Usage:
REM   bin\install_precommit_hook.bat                          (prompt on husky conflict)
REM   FORCE_OVERRIDE=1 bin\install_precommit_hook.bat         (CI / scripted install)

setlocal enabledelayedexpansion

cd /d "%~dp0\..\"

echo [install] === Pre-commit hook installer (v3.3.1) ===
echo [install] Repo root: %CD%
echo.

REM --- 1. Verify .githooks/ files present -- pre-flight gate --------------
if not exist ".githooks\pre-commit.bat" (
    echo [install] FAIL: .githooks\pre-commit.bat not found.
    echo             The .githooks/ directory must be populated first.
    exit /b 1
)
if not exist ".githooks\pre-commit" (
    echo [install] FAIL: .githooks\pre-commit not found.
    exit /b 1
)
if not exist "bin\precommit_check.bat" (
    echo [install] FAIL: bin\precommit_check.bat not found.
    echo             The canonical Windows runner is missing.
    exit /b 1
)

echo [install] .githooks/ hooks present:
echo   pre-commit           ^(bash dispatcher -- Unix path + Windows delegation^)
echo   pre-commit.bat       ^(Windows cmd.exe thin wrapper^)
echo   README.md            ^(operator docs^)
echo [install] bin/ runner present:
echo   precommit_check.bat  ^(canonical Windows runner^)
echo.

REM --- 2. Show current core.hooksPath ------------------------------------
set "CUR_HOOKS_PATH="
for /f "tokens=*" %%P in ('git config --get core.hooksPath 2^>nul') do (
    set "CUR_HOOKS_PATH=%%P"
)
echo [install] Current git core.hooksPath:
if "!CUR_HOOKS_PATH!"=="" (
    echo   ^(unset -- defaults to .git/hooks^)
) else (
    echo   !CUR_HOOKS_PATH!
    if /i "!CUR_HOOKS_PATH!"==".husky" (
        echo.
        echo [install] +----------------------------------------------------------------+
        echo [install] ^|  WARNING: core.hooksPath is currently .husky.  Overriding   ^|
        echo [install] ^|  will break husky workflows.                              ^|
        echo [install] +----------------------------------------------------------------+
        if defined FORCE_OVERRIDE (
            echo [install] FORCE_OVERRIDE=1 -- skipping prompt, overriding.
        ) else (
            set /p "CONFIRM=Override .husky with .githooks? [Y/N]: "
            if /i not "!CONFIRM!"=="Y" (
                echo.
                echo [install] Aborted. core.hooksPath remains .husky.
                exit /b 0
            )
            echo [install] Confirmed -- proceeding with override.
        )
    )
)

REM --- 3. Set core.hooksPath --------------------------------------------
echo.
echo [install] Setting git config core.hooksPath to .githooks ...
git config core.hooksPath .githooks
if errorlevel 1 (
    echo [install] FAIL: git config returned errorlevel !errorlevel!.
    exit /b 2
)

REM --- 4. Verify ------------------------------------------------------
echo.
echo [install] Post-install core.hooksPath:
for /f "tokens=*" %%P in ('git config --get core.hooksPath') do (
    echo   %%P
)

REM --- 5. Operator next-steps -----------------------------------------
echo.
echo [install] DONE. Pre-commit hook installed.
echo.
echo           To verify the hook fires on commit:
echo             git commit --allow-empty -m "test hook fire"
echo.
echo           To uninstall:
echo             git config --unset core.hooksPath
echo.
echo           Operator-side alternative (no git wiring):
echo             bin\precommit_check.bat
echo.
echo           To bypass the hook entirely (e.g. for emergency):
echo             set PRECOMMIT_BYPASS=1 ^& set PRECOMMIT_BYPASS_ACK=1 ^& git commit ...
echo             ^(paired-ack: BOTH env vars required since v3.3.2^)
echo.
echo           To skip just Stage B smoke (docs-only / trivial commit):
echo             set PRECOMMIT_SKIP_SMOKE=1 ^& set PRECOMMIT_SKIP_SMOKE_ACK=1 ^& git commit ...
echo             ^(paired-ack: BOTH env vars required; Stage A syntax still runs^)

endlocal
exit /b 0
