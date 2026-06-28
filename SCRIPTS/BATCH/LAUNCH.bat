@echo off
REM Ultimate Launcher for Enhanced Charm Crush CLI
REM This file provides the EASIEST way to start

cd /d "%~dp0"

echo ==================================================
echo      ENHANCED CHARM CRUSH CLI - LAUNCHER
echo ==================================================
echo.
echo [1] Start GUI (Recommended - Visual Interface)
echo [2] Start Main Menu (Batch File - Fast)
echo [3] Quick Actions Only (One-Click Tasks)
echo [4] Setup/Install (First Time Only)
echo [5] Open Documentation
echo [Q] Quit
echo.
set /p "choice=Choose (1-5, Q): "

if "%choice%"=="1" (
    echo Starting GUI...
    python charm_crush_gui.py
    goto EOF
)

if "%choice%"=="2" (
    echo Starting Main Menu...
    run_charm_crush.bat
    goto EOF
)

if "%choice%"=="3" (
    echo Starting Quick Actions...
    quick_actions.bat
    goto EOF
)

if "%choice%"=="4" (
    echo Running Setup...
    python setup_enhanced_cli.py
    echo.
    echo Setup complete! Run again and choose [1] to start GUI.
    pause
    goto EOF
)

if "%choice%"=="5" (
    echo Opening Documentation...
    if exist "COMPLETE_USER_GUIDE.md" (
        start notepad COMPLETE_USER_GUIDE.md
    ) else (
        echo Documentation not found. Run setup first.
    )
    pause
    goto EOF
)

if /i "%choice%"=="Q" goto EOF

echo Invalid choice!
pause

:EOF
echo.
echo Thank you for using Enhanced Charm Crush CLI!