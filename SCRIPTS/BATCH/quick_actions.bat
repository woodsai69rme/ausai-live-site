@echo off
REM Quick Actions for Enhanced Charm Crush CLI
REM Fast access to common operations

cd /d "%~dp0"

echo ================= QUICK ACTIONS =================
echo.
echo [A] Download ALL My GitHub Repos
echo [B] Sync X:\githubrepo
echo [C] Cleanup C: Drive (Dry Run)
echo [D] Cleanup X: Drive (Live - Warning!)
echo [E] Show Status & Costs
echo [F] Chat with AI
echo [G] Find Large Files (>100MB)
echo [H] Remove Duplicates (DRY RUN)
echo [I] Run Setup/Install
echo [Q] Quit
echo.

set /p "action=Choose action (A-I, Q): "

if /i "%action%"=="A" (
    echo Downloading all repositories...
    python github_bulk_downloader.py --all --output X:\githubrepo
    goto END
)

if /i "%action%"=="B" (
    set /p "token=GitHub token (optional, press Enter to skip): "
    if "!token!"=="" (
        python repo_sync_organizer.py --base-path X:\githubrepo --check-updates
    ) else (
        python repo_sync_organizer.py --base-path X:\githubrepo --sync --token "!token!"
    )
    goto END
)

if /i "%action%"=="C" (
    echo Dry run on C: drive...
    python disk_cleanup_tool.py --dry-run
    goto END
)

if /i "%action%"=="D" (
    echo WARNING: This will DELETE files from X: drive!
    set /p "confirm=Type YES to continue: "
    if "!confirm!"=="YES" (
        python disk_cleanup_tool.py --live --drives X:
    ) else (
        echo Cancelled.
    )
    goto END
)

if /i "%action%"=="E" (
    python charm_crush_enhanced.py status
    goto END
)

if /i "%action%"=="F" (
    set /p "message=What would you like to discuss? "
    python charm_crush_enhanced.py chat --message "!message!"
    goto END
)

if /i "%action%"=="G" (
    echo Large files on C: drive...
    python disk_cleanup_tool.py --large-files --drives C: --threshold 100
    goto END
)

if /i "%action%"=="H" (
    echo Checking for duplicates...
    python repo_sync_organizer.py --base-path X:\githubrepo --find-duplicates
    goto END
)

if /i "%action%"=="I" (
    python setup_enhanced_cli.py
    goto END
)

if /i "%action%"=="Q" goto EOF

echo Invalid choice!
goto EOF

:END
echo.
echo Action complete!
pause

:EOF