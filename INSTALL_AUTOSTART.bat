@echo off
title Install Empire Auto-Start Supervisor
color 0A
cls
echo ===============================================================================
echo   ⚙️ INSTALLING EMPIRE MASTER AUTO-START SUPERVISOR
echo ===============================================================================
echo.
powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut([System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\Startup', 'EmpireAutoStart.lnk')); $s.TargetPath = 'C:\Users\karma\START_EMPIRE_SILENT_STARTUP.vbs'; $s.WorkingDirectory = 'C:\Users\karma'; $s.Description = 'Start all Empire 2026 engines silently on login'; $s.Save()"
if %ERRORLEVEL% equ 0 (
    echo [OK] Auto-Start Shortcut successfully installed in Windows Startup folder!
    echo      The 7 core engines will now automatically boot silently whenever you log in.
) else (
    echo [!] Could not install startup shortcut. Check permissions.
)
echo.
pause
