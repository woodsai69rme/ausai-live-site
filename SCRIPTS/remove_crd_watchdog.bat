@echo off
setlocal

echo Removing CRD AutoStart Watchdog scheduled task...
schtasks /delete /tn "CRD AutoStart Watchdog" /f
if errorlevel 1 (
    echo   Task was not present (already removed).
    exit /b 0
)
echo   Removed.
echo   Note: the log file at C:\ProgramData\CRD-Watchdog\log.txt
echo   is preserved for forensics; delete it manually if you want.
endlocal
