@echo off
REM ============================================
REM EMERGENCY RESCUE DUMP - ONE CLICK
REM ============================================
title EMERGENCY RESCUE DUMP
color 4F

echo ============================================
echo !!! EMERGENCY RESCUE DUMP STARTED !!!
echo ============================================
echo.
echo This script will attempt to pull ALL data from
echo the connected device immediately.
echo.

REM Create timestamped folder
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set folder=RESCUE_DUMP_%datetime:~0,14%
mkdir "%folder%"
cd "%folder%"

echo [1/6] Extracting System Info...
adb shell getprop > system_properties.txt
adb shell pm list packages > installed_packages.txt

echo [2/6] Pulling DCIM (Photos/Videos)...
mkdir DCIM
adb pull /sdcard/DCIM ./DCIM/

echo [3/6] Pulling Pictures...
mkdir Pictures
adb pull /sdcard/Pictures ./Pictures/

echo [4/6] Pulling Downloads...
mkdir Downloads
adb pull /sdcard/Download ./Downloads/

echo [5/6] Pulling WhatsApp Data...
mkdir WhatsApp
adb pull /sdcard/WhatsApp ./WhatsApp/
adb pull /sdcard/Android/media/com.whatsapp/WhatsApp ./WhatsApp/

echo [6/6] Pulling Documents & Music...
mkdir Documents
adb pull /sdcard/Documents ./Documents/
mkdir Music
adb pull /sdcard/Music ./Music/

echo.
echo ============================================
echo RESCUE COMPLETE!
echo Data saved in: %folder%
echo ============================================
pause
