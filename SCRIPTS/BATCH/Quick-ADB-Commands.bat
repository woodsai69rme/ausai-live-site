@echo off
REM ============================================
REM QUICK ADB COMMANDS v2.0
REM ============================================
title Quick ADB Commands v2.0
color 0E

:menu
cls
echo ============================================
echo QUICK ADB COMMANDS v2.0
echo ============================================
echo.
echo 1. Type Text (Send text to phone)
echo 2. Take Screenshot
echo 3. Navigation (Home, Back, Recents)
echo 4. Power / Reboot Menu
echo 5. Enable Touch Indicators
echo 6. Disable Touch Indicators
echo 7. List 3rd Party Apps
echo 8. PIN / Password Unlocker (Blind Unlock)
echo 9. Pattern Lock Helper (Swipe Nodes)
echo 10. Back to Main Menu
echo.
choice /c 1234567890 /m "Select: "

if errorlevel 10 exit /b 0
if errorlevel 9 goto pattern_unlock
if errorlevel 8 goto pin_unlock
if errorlevel 7 goto list_apps
if errorlevel 6 goto no_touch
if errorlevel 5 goto touch
if errorlevel 4 goto key_menu
if errorlevel 3 goto shell
if errorlevel 2 goto info
if errorlevel 1 goto reboot

:pattern_unlock
echo.
echo ============================================
echo PATTERN LOCK HELPER
echo ============================================
echo Pattern Node Map:
echo [1] [2] [3]
echo [4] [5] [6]
echo [7] [8] [9]
echo.
echo Enter nodes in order (e.g., 1236):
set /p nodes="Nodes: "
echo Drawing pattern...
adb shell input keyevent KEYCODE_WAKEUP
adb shell input swipe 500 1500 500 500 200
timeout /t 1 /nobreak >nul

set prev_x=
set prev_y=

REM This is a simplified approach using individual swipes for each segment.
REM For real patterns, a single continuous swipe command is better but complex for batch.
REM We will use a sequence of swipes with very short duration.

for /l %%i in (0,1,20) do (
    set "node=!nodes:~%%i,1!"
    if "!node!"=="" goto pattern_done
    
    set x=
    set y=
    if "!node!"=="1" (set x=250 & set y=800)
    if "!node!"=="2" (set x=540 & set y=800)
    if "!node!"=="3" (set x=830 & set y=800)
    if "!node!"=="4" (set x=250 & set y=1090)
    if "!node!"=="5" (set x=540 & set y=1090)
    if "!node!"=="6" (set x=830 & set y=1090)
    if "!node!"=="7" (set x=250 & set y=1380)
    if "!node!"=="8" (set x=540 & set y=1380)
    if "!node!"=="9" (set x=830 & set y=1380)

    if defined prev_x (
        adb shell input swipe !prev_x! !prev_y! !x! !y! 100
    )
    set prev_x=!x!
    set prev_y=!y!
)

:pattern_done
echo Pattern sent.
pause
goto menu


:type_text
echo.
echo Enter text to send to phone (no special chars):
set /p user_text="Text: "
adb shell input text "%user_text%"
echo Sent!
pause
goto menu

:screenshot
echo.
REM Robust timestamp generation using WMIC
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set filename=screenshot_%datetime:~0,14%.png
echo Taking screenshot...
adb shell screencap -p /sdcard/%filename%
adb pull /sdcard/%filename% .
adb shell rm /sdcard/%filename%
echo Saved as %filename% in current folder.
pause
goto menu

:nav_menu
cls
echo NAVIGATION
echo ----------
echo 1. Home
echo 2. Back
echo 3. Recent Apps
echo 4. Menu
choice /c 1234 /m "Select: "
if errorlevel 4 adb shell input keyevent KEYCODE_MENU
if errorlevel 3 adb shell input keyevent KEYCODE_APP_SWITCH
if errorlevel 2 adb shell input keyevent KEYCODE_BACK
if errorlevel 1 adb shell input keyevent KEYCODE_HOME
goto menu

:power_menu
cls
echo POWER MENU
echo ----------
echo 1. Toggle Screen On/Off
echo 2. Reboot
echo 3. Reboot Recovery
echo 4. Reboot Bootloader
choice /c 1234 /m "Select: "
if errorlevel 4 adb reboot bootloader
if errorlevel 3 adb reboot recovery
if errorlevel 2 adb reboot
if errorlevel 1 adb shell input keyevent KEYCODE_POWER
goto menu

:touch
adb shell settings put system show_touches 1
adb shell settings put system pointer_location 1
echo Indicators Enabled.
pause
goto menu

:no_touch
adb shell settings put system show_touches 0
adb shell settings put system pointer_location 0
echo Indicators Disabled.
pause
goto menu

:pin_unlock
echo.
echo ============================================
echo BLIND PIN UNLOCKER
echo ============================================
echo 1. Waking up screen...
adb shell input keyevent KEYCODE_WAKEUP
echo 2. Swiping up to show entry field...
adb shell input swipe 500 1500 500 500 200
timeout /t 1 /nobreak >nul
echo.
echo Enter your PIN/Password and press Enter:
set /p user_pin="PIN: "
echo Sending input...
adb shell input text "%user_pin%"
adb shell input keyevent KEYCODE_ENTER
echo.
echo Input sent. If the phone was on the lock screen, 
echo it should now be unlocked.
pause
goto menu

:list_apps
echo.
echo Listing 3rd Party Apps...
adb shell pm list packages -3
echo.
pause
goto menu
