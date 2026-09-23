@echo off
:: bin/verify_nightly_task.bat -- check if the nightly war_room doctor snapshot task is installed
::
:: Read-only check: runs `schtasks /Query /TN "WarRoomNightlySnapshot"` and reports status.
:: Does NOT install; does NOT modify state. Exit 0 if installed, 1 if not.
::
:: Companion to bin\install_nightly_snapshot.bat.

setlocal

set "TASK_NAME=WarRoomNightlySnapshot"

schtasks /Query /TN "%TASK_NAME%" /V /FO LIST 2>nul
if errorlevel 1 (
  echo.
  echo [INFO] Task "%TASK_NAME%" is NOT installed.
  echo        To install: bin\install_nightly_snapshot.bat
  exit /b 1
)

echo.
echo [PASS] Task "%TASK_NAME%" is installed and enabled.
echo.
echo Next run: see schtasks /Query above.
echo To run now: schtasks /Run /TN "%TASK_NAME%"
echo To see captured snapshots afterwards: python war_room.py snapshot-doctor --list

endlocal
