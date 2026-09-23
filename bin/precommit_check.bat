@echo off
REM bin\precommit_check.bat
REM Canonical operator-side pre-commit verification v3 (v3.3.2, paired-ack).
REM Single source of truth for Stage A + Stage B verification logic.
REM
REM Stage A: node --check syntax on staged dashboards.mjs + 3 HTML files.
REM Stage B: node tools\test_dashboards.js smoke regression (16 cats,
REM          ~75 linkedom assertions).
REM
REM v3.3.2 BREAKING CHANGE (paired-ack for BOTH hatches):
REM   PRECOMMIT_BYPASS=1          -> now requires PRECOMMIT_BYPASS_ACK=1
REM   PRECOMMIT_SKIP_SMOKE=1      -> now requires PRECOMMIT_SKIP_SMOKE_ACK=1
REM   Single-var set returns rc=2 with "missing ACK" message. Defends against
REM   accidental CI bleed-through / parent-shell env var inheritance.
REM   See CHANGELOG ## 2026-07-13 (post-cont.5-fup-13) for paired-ack rationale.
REM
REM Running in cmd.exe (vs the stripped git-bash hook subprocess) means
REM `where node` queries the FULL Windows PATH -- this is the v3.3.1 fix
REM for the 3 prior pure-bash rewrite attempts that empirically failed with
#REM PATH-strip.
REM
REM Usage:
REM   bin\precommit_check.bat                  (from any cwd; cd's to repo root)
REM   bin\precommit_check.bat ^> nul           (silent -- rc only)
REM
REM Exit codes:
REM   0 = all-pass OR paired-ack hatch honored
REM   1 = Stage A syntax FAIL or Stage B smoke FAIL
REM   2 = paired-ack violated (single-var set without _ACK)
REM
REM Escape hatches (paired-ack required for BOTH):
REM   PRECOMMIT_BYPASS=1 + PRECOMMIT_BYPASS_ACK=1     -- bypass entire hook
REM   PRECOMMIT_SKIP_SMOKE=1 + PRECOMMIT_SKIP_SMOKE_ACK=1 -- skip Stage B smoke only
REM
REM See CHANGELOG ## 2026-07-13 (post-cont.5-fup-13) for SMOKE-skip + paired-ack rationale.

setlocal enabledelayedexpansion

REM --- Bypass hatch: PRECOMMIT_BYPASS=1 + PRECOMMIT_BYPASS_ACK=1 (paired) ---
REM Both env vars required -- single-var set is refused (CI bleed defense).
REM See CHANGELOG ## 2026-07-13 (post-cont.5-fup-13) for paired-ack rationale.
if defined PRECOMMIT_BYPASS (
    if not defined PRECOMMIT_BYPASS_ACK (
        echo [check] FAIL: PRECOMMIT_BYPASS=1 requires PRECOMMIT_BYPASS_ACK=1 paired ack.
        echo            To bypass the hook entirely, set BOTH env vars:
        echo              set PRECOMMIT_BYPASS=1 ^& set PRECOMMIT_BYPASS_ACK=1 ^& git commit ...
        echo            Single-var set is refused to prevent accidental CI bleed-through.
        exit /b 2
    )
    echo [check] WARN: PRECOMMIT_BYPASS=1 + PRECOMMIT_BYPASS_ACK=1 -- hook will be skipped.
    echo [check]       Stage A syntax + Stage B smoke both bypassed. Verify manually before pushing.
    exit /b 0
)

REM --- Skip-smoke hatch: PRECOMMIT_SKIP_SMOKE=1 + PRECOMMIT_SKIP_SMOKE_ACK=1 (paired) ---
REM Both env vars required -- single-var set is refused (CI bleed defense).
REM See CHANGELOG ## 2026-07-13 (post-cont.5-fup-13) for paired-ack rationale.
if defined PRECOMMIT_SKIP_SMOKE (
    if not defined PRECOMMIT_SKIP_SMOKE_ACK (
        echo [check] FAIL: PRECOMMIT_SKIP_SMOKE=1 requires PRECOMMIT_SKIP_SMOKE_ACK=1 paired ack.
        echo            To skip just Stage B smoke, set BOTH env vars:
        echo              set PRECOMMIT_SKIP_SMOKE=1 ^& set PRECOMMIT_SKIP_SMOKE_ACK=1 ^& git commit ...
        echo            Single-var set is refused to prevent accidental CI bleed-through.
        exit /b 2
    )
    REM Ack validated -- Stage B will skip (the actual skip is in the Stage B block below).
)

REM --- Resolve repo root -----------------------------------------------------
set "REPO_ROOT=%~dp0..\"
cd /d "%REPO_ROOT%"
if not exist ".git" (
    echo [check] FAIL: not in a git repo ^(.git/ missing at %CD%^).
    echo            Run from inside the repo's bin\ subdirectory.
    exit /b 1
)
if not exist "dashboards.mjs" (
    echo [check] FAIL: dashboards.mjs not found at %CD%.
    echo            This script is intended for the dashboard-system repo.
    exit /b 1
)
echo [check] Repo root: %CD%

REM --- Discover node via cmd.exe 'where' (full Windows PATH) ----------------
set "NODE_BIN="
for /f "tokens=*" %%P in ('where node 2^>nul') do (
    if not defined NODE_BIN set "NODE_BIN=%%P"
)
if "!NODE_BIN!"=="" (
    echo [check] FAIL: no node found in PATH.
    echo            Install Node.js LTS from https://nodejs.org/ then retry.
    exit /b 1
)
echo [check] -- node: !NODE_BIN!

REM --- Stage A: node --check syntax on staged dashboard files --------------
echo [check] Stage A: syntax-check staged dashboard files...
set "STAGE_A_FAILED="
for %%T in (dashboards.mjs UNIFIED_MASTER_DASHBOARD.html AI_TOOLS_DASHBOARD.html AUSAI_OPS_DASHBOARD.html) do (
    if not exist "%%T" (
        echo   -- A: skip ^(not found^): %%T
    ) else (
        git diff --cached --quiet -- "%%T" 2>nul && (
            echo   -- A: skip ^(no staged changes^): %%T
        ) || (
            echo   -- A: syntax-checking ^(staged^): %%T
            "!NODE_BIN!" --check "%%T" 1>nul 2>nul && (
                rem success -- continue
            ) || (
                echo [check] FAIL: %%T has syntax errors. Run:
                echo            "!NODE_BIN!" --check "%%T"  to see details.
                set "STAGE_A_FAILED=1"
            )
        )
    )
)
if defined STAGE_A_FAILED (
    echo [check] STAGE A FAILED. Fix syntax errors above before committing.
    exit /b 1
)

REM --- Stage B: smoke regression via node tools\test_dashboards.js --------
REM Always runs unless paired-ack PRECOMMIT_SKIP_SMOKE=1 + ACK=1 was validated
REM above. Single source of truth for the actual skip decision lives here;
REM the top block just enforces the paired-ack policy.
echo [check] Stage B: smoke regression ^("!NODE_BIN!" tools\test_dashboards.js^)...
if defined PRECOMMIT_SKIP_SMOKE (
    REM Paired-ack already validated at top -- safe to skip directly.
    echo [check] -- skipped ^(paired-ack: PRECOMMIT_SKIP_SMOKE=1 + PRECOMMIT_SKIP_SMOKE_ACK=1^)
) else (
    "!NODE_BIN!" tools\test_dashboards.js 1>nul 2>nul
    if not "!ERRORLEVEL!"=="0" (
        echo [check] FAIL: smoke regression failed.
        echo            Run "!NODE_BIN!" tools\test_dashboards.js for details.
        exit /b 1
    )
)

if defined PRECOMMIT_SKIP_SMOKE (
    echo [check] OK: pre-commit Stage A PASSED. ^(Stage B skipped via paired-ack: PRECOMMIT_SKIP_SMOKE=1 + PRECOMMIT_SKIP_SMOKE_ACK=1^)
) else (
    echo [check] OK: pre-commit Stage A + Stage B PASSED.
)
endlocal
exit /b 0
