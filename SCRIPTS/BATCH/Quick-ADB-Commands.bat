@echo off
REM ============================================
REM Quick-ADB-Commands.bat
REM Sibling of Enhanced-Phone-Connection-Tester.bat and
REM Enhanced-Advanced-Recovery-Suite.bat (Dr.Fone-Alt family).
REM Fill-in for the missing sibling referenced from those menus.
REM ============================================
title Quick ADB Commands
color 0A

:set_paths
REM Locate ADB -- prefer system, then python adbutils, then current dir
set "ADB=adb"
where adb >nul 2>nul
if %errorlevel% NEQ 0 (
    if exist "adb.exe" (
        set PATH=%PATH%;%CD%
    ) else if exist "%AppData%\Roaming\Python\Python313\site-packages\adbutils\binaries\adb.exe" (
        set PATH=%PATH%;%AppData%\Roaming\Python\Python313\site-packages\adbutils\binaries
    )
)

:start
cls
echo ============================================
echo QUICK ADB COMMANDS
echo ============================================
echo.
adb devices
echo.
echo -------- common actions --------
echo   1. Send TAP (x y)
echo   2. Send SWIPE (x1 y1 x2 y2 ms)
echo   3. Send KEYEVENT (code or name e.g. KEYCODE_HOME)
echo   4. Send TEXT (will escape spaces as %%s)
echo   5. Take SCREENSHOT (saved to /sdcard, pulled to here)
echo   6. Pull /sdcard/DCIM  (photos) -> Recovered_Photos
echo   7. Pull /sdcard/WhatsApp -> Recovered_WhatsApp
echo   8. ADB shell raw (drop into device shell)
echo   9. Reboot into recovery / bootloader / fastbootd
echo  10. Refresh (kill-server + start-server + devices)
echo   0. Back
echo.

choice /c 1234567890 /m "Select: "
if errorlevel 10 goto back
if errorlevel 9  goto reboot
if errorlevel 8  goto shell
if errorlevel 7  goto pull_wa
if errorlevel 6  goto pull_dcim
if errorlevel 5  goto screen
if errorlevel 4  goto text
if errorlevel 3  goto key
if errorlevel 2  goto swipe
if errorlevel 1  goto tap
goto start

:tap
set /p xy="x y (e.g. 540 1200): "
adb shell input tap %xy%
pause
goto start

:swipe
set /p coords="x1 y1 x2 y2 duration_ms: "
adb shell input swipe %coords%
pause
goto start

:key
set /p code="keyevent code (e.g. KEYCODE_HOME or 26): "
adb shell input keyevent %code%
pause
goto start

:text
REM NOTE: input text does not accept spaces natively. Replace with %%s.
set /p msg="text to send: "
adb shell input text "%msg: =%%s%"
echo (note: spaces were converted to %%s; tweak via shell escape if needed)
pause
goto start

:screen
set stamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set stamp=%stamp: =0%
adb shell screencap -p /sdcard/screen_%stamp%.png
adb pull /sdcard/screen_%stamp%.png .\
echo Saved: screen_%stamp%.png
pause
goto start

:pull_dcim
mkdir "Recovered_Photos" 2>nul
echo Pulling photos...
adb pull /sdcard/DCIM ./Recovered_Photos
echo Done.
pause
goto start

:pull_wa
mkdir "Recovered_WhatsApp" 2>nul
echo Pulling WhatsApp media (best-effort, both layouts)...
adb pull /sdcard/WhatsApp/Media ./Recovered_WhatsApp
adb pull /sdcard/Android/media/com.whatsapp/WhatsApp/Media ./Recovered_WhatsApp
echo Done.
pause
goto start

:shell
adb shell
pause
goto start

:reboot
echo.
echo Reboot target:
echo   R = recovery
echo   B = bootloader (fastboot)
echo   F = fastbootd
echo   S = system (normal)
choice /c RBFS /m "Pick: "
if errorlevel 4 goto rb_system
if errorlevel 3 goto rb_fbdt
if errorlevel 2 goto rb_boot
if errorlevel 1 goto rb_recovery
goto reboot
:rb_recovery
adb reboot recovery
goto reboot_done
:rb_boot
adb reboot bootloader
goto reboot_done
:rb_fbdt
adb reboot fastboot
goto reboot_done
:rb_system
adb reboot
:reboot_done
echo Done. Phone may take 30-60s to come back up.
pause
goto start

:set_paths
goto start

:back
exit /b 0
