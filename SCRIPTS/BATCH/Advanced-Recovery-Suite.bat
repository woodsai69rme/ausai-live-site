@echo off
REM ============================================
REM ADVANCED ANDROID RECOVERY SUITE (Dr.Fone Alternative)
REM ============================================
title Advanced Android Recovery Suite
color 0C

:main
cls
echo ============================================
echo ADVANCED RECOVERY SUITE
echo ============================================
echo.
echo Open Source alternative to commercial recovery tools.
echo.
echo [1] DATA EXTRACTION (Recover Photos, Files, Music)
echo [2] PHONE BACKUP (Full System Backup)
echo [3] SYSTEM REPAIR (Fix Boot Loops, Cache)
echo [4] SCREEN UNLOCK TOOLS (Remove PIN/Pattern)
echo [5] APP MANAGER (Debloat, Uninstall)
echo [6] SYSTEM DIAGNOSTICS (Live Logs / Health)
echo [7] EXIT
echo.
choice /c 1234567 /m "Select option: "

if errorlevel 7 exit /b 0
if errorlevel 6 goto diagnostics
if errorlevel 5 goto app_manager
if errorlevel 4 goto unlock_tools
if errorlevel 3 goto system_repair
if errorlevel 2 goto backup_tools
if errorlevel 1 goto data_extraction

REM ============================================
REM DATA EXTRACTION
REM ============================================
:data_extraction
cls
echo ============================================
echo DATA EXTRACTION MODULE
echo ============================================
echo.
echo Extracts data from device internal storage.
echo.
echo 1. Pull All Photos (DCIM)
echo 2. Pull All Downloads
echo 3. Pull WhatsApp Images/Media
echo 4. Pull Music
echo 5. Custom Folder Pull
echo 6. Back to Main Menu
echo.
choice /c 123456 /m "Select: "

if errorlevel 6 goto main
if errorlevel 5 goto custom_pull
if errorlevel 4 goto pull_music
if errorlevel 3 goto pull_whatsapp
if errorlevel 2 goto pull_downloads
if errorlevel 1 goto pull_photos

:pull_photos
echo.
echo Extracting Photos...
mkdir "Recovered_Photos" 2>nul
adb pull /sdcard/DCIM ./Recovered_Photos/
adb pull /sdcard/Pictures ./Recovered_Photos/
echo Done! Check 'Recovered_Photos' folder.
pause
goto data_extraction

:pull_downloads
echo.
echo Extracting Downloads...
mkdir "Recovered_Downloads" 2>nul
adb pull /sdcard/Download ./Recovered_Downloads/
echo Done!
pause
goto data_extraction

:pull_whatsapp
echo.
echo Extracting WhatsApp Media...
mkdir "Recovered_WhatsApp" 2>nul
adb pull /sdcard/WhatsApp/Media ./Recovered_WhatsApp/
adb pull /sdcard/Android/media/com.whatsapp/WhatsApp/Media ./Recovered_WhatsApp/
echo Done!
pause
goto data_extraction

:pull_music
echo.
echo Extracting Music...
mkdir "Recovered_Music" 2>nul
adb pull /sdcard/Music ./Recovered_Music/
echo Done!
pause
goto data_extraction

:custom_pull
echo.
set /p folder="Enter folder path on phone (e.g., /sdcard/Documents): "
mkdir "Recovered_Custom" 2>nul
adb pull %folder% ./Recovered_Custom/
echo Done!
pause
goto data_extraction

REM ============================================
REM PHONE BACKUP
REM ============================================
:backup_tools
cls
echo ============================================
echo FULL PHONE BACKUP
echo ============================================
echo.
echo Uses Android's native backup mechanism.
echo Note: You may need to confirm on the phone screen.
echo.
echo 1. Backup EVERYTHING (Apps + Data + SD Card)
echo 2. Backup Apps Only (APK + Data)
echo 3. Restore from Backup
echo 4. Back
echo.
choice /c 1234 /m "Select: "

if errorlevel 4 goto main
if errorlevel 3 goto restore
if errorlevel 2 goto backup_apps
if errorlevel 1 goto backup_all

:backup_all
echo.
set filename=full_backup_%date:~10,4%%date:~4,2%%date:~7,2%.ab
echo Starting Full Backup to %filename%...
echo UNLOCK YOUR PHONE AND CONFIRM THE BACKUP PASSWORD!
adb backup -apk -shared -all -f %filename%
echo.
echo Backup process finished (or cancelled).
pause
goto backup_tools

:backup_apps
echo.
set filename=apps_backup_%date:~10,4%%date:~4,2%%date:~7,2%.ab
echo Starting Apps Backup to %filename%...
echo UNLOCK YOUR PHONE AND CONFIRM!
adb backup -apk -noshared -all -f %filename%
pause
goto backup_tools

:restore
echo.
echo Drag and drop your .ab backup file here:
set /p backup_file="File: "
echo Restoring...
adb restore %backup_file%
pause
goto backup_tools

REM ============================================
REM SYSTEM REPAIR
REM ============================================
:system_repair
cls
echo ============================================
echo SYSTEM REPAIR TOOLS
echo ============================================
echo.
echo 1. Soft Reboot (Refresh System)
echo 2. Reboot to Safe Mode (Disables 3rd party apps)
echo 3. Wipe Cache Partition (via Recovery - Manual Step)
echo 4. Fix "Boot Loop" (Reboot Bootloader)
echo 5. Back
echo.
choice /c 12345 /m "Select: "

if errorlevel 5 goto main
if errorlevel 4 goto fix_bootloop
if errorlevel 3 goto wipe_cache
if errorlevel 2 goto safe_mode
if errorlevel 1 goto soft_reboot

:soft_reboot
adb shell am restart
echo System UI restarted.
pause
goto system_repair

:safe_mode
echo Rebooting to Safe Mode...
echo (Note: Not all phones support this via ADB, standard reboot sent)
adb reboot
echo Hold Volume Down during boot animation!
pause
goto system_repair

:wipe_cache
echo Rebooting to Recovery...
adb reboot recovery
echo.
echo ON PHONE:
echo 1. Use Vol Keys to select "Wipe Cache Partition"
echo 2. Press Power to confirm.
echo 3. Select "Reboot System Now".
pause
goto system_repair

:fix_bootloop
echo Rebooting to Bootloader (Fastboot)...
adb reboot bootloader
echo.
echo If phone is stuck, try holding Power + Vol Down for 15s.
pause
goto system_repair

REM ============================================
REM UNLOCK TOOLS
REM ============================================
:unlock_tools
cls
echo ============================================
echo SCREEN UNLOCK TOOLS
echo ============================================
echo.
echo WARNING: Removing lock screens on modern Android (6.0+)
echo usually requires ROOT access or a Factory Reset (Data Loss).
echo.
echo 1. Method 1: Remove Gesture Key (ROOT REQUIRED)
echo 2. Method 2: Clear Lock Settings (ROOT REQUIRED)
echo 3. Method 3: ADB Bypass (Very Old Android < 5.0)
echo 4. Method 4: Factory Reset (WIPES DATA - Last Resort)
echo 5. Back
echo.
choice /c 12345 /m "Select: "

if errorlevel 5 goto main
if errorlevel 4 goto factory_reset
if errorlevel 3 goto method_old
if errorlevel 2 goto method_locksettings
if errorlevel 1 goto method_gesture

:method_gesture
echo Attempting to remove gesture.key...
adb shell rm /data/system/gesture.key
echo Rebooting...
adb reboot
pause
goto unlock_tools

:method_locksettings
echo Attempting to clear lock settings...
adb shell locksettings clear --old 1234
echo (This command often fails without root).
pause
goto unlock_tools

:method_old
echo Attempting SQL Injection bypass (CVE-2013-6271)...
adb shell sqlite3 /data/data/com.android.providers.settings/databases/settings.db "update system set value=0 where name='lock_pattern_autolock';"
echo Rebooting...
adb reboot
pause
goto unlock_tools

:factory_reset
echo.
echo WARNING: THIS WILL ERASE ALL DATA ON THE PHONE.
echo Are you absolutely sure? (Y/N)
set /p confirm="Type YES to confirm: "
if "%confirm%"=="YES" (
    echo Factory Resetting...
    adb shell recovery --wipe_data
    echo Done.
) else (
    echo Cancelled.
)
pause
goto unlock_tools

REM ============================================
REM APP MANAGER
REM ============================================
:app_manager
cls
echo ============================================
echo APP MANAGER (DEBLOATER)
echo ============================================
echo.
echo 1. List All Apps
echo 2. List 3rd Party Apps
echo 3. List System Apps
echo 4. Uninstall App
echo 5. Disable App (Safe Debloat)
echo 6. Back
echo.
choice /c 123456 /m "Select: "

if errorlevel 6 goto main
if errorlevel 5 goto disable_app
if errorlevel 4 goto uninstall_app
if errorlevel 3 goto list_sys
if errorlevel 2 goto list_3rd
if errorlevel 1 goto list_all

:list_all
adb shell pm list packages | sort > apps_all.txt
notepad apps_all.txt
goto app_manager

:list_3rd
adb shell pm list packages -3 | sort > apps_3rd.txt
notepad apps_3rd.txt
goto app_manager

:list_sys
adb shell pm list packages -s | sort > apps_system.txt
notepad apps_system.txt
goto app_manager

:uninstall_app
set /p pkg="Enter package name (e.g., com.facebook.katana): "
adb uninstall %pkg%
pause
goto app_manager

:disable_app
set /p pkg="Enter package name to DISABLE: "
adb shell pm disable-user --user 0 %pkg%
echo App disabled.
pause
goto app_manager

:diagnostics
cls
echo ============================================
echo SYSTEM DIAGNOSTICS & HEALTH
echo ============================================
echo.
echo 1. Generate Full Health Report (Saves to file)
echo 2. Live Logcat (System Errors - Press Ctrl+C to stop)
echo 3. View Dumpsys (Battery/CPU/RAM stats)
echo 4. Check Disk Usage Detail
echo 5. Back
echo.
choice /c 12345 /m "Select: "

if errorlevel 5 goto main
if errorlevel 4 goto disk_detail
if errorlevel 3 goto dumpsys_view
if errorlevel 2 goto live_logcat
if errorlevel 1 goto health_report

:health_report
echo.
echo Generating report...
set filename=HEALTH_REPORT_%date:~10,4%%date:~4,2%%date:~7,2%.txt
echo [PRODUCT INFO] > %filename%
adb shell getprop ro.product.model >> %filename%
echo [BATTERY] >> %filename%
adb shell dumpsys battery >> %filename%
echo [STORAGE] >> %filename%
adb shell df -h >> %filename%
echo [UPTIME] >> %filename%
adb shell uptime >> %filename%
echo Report saved as %filename%
pause
goto diagnostics

:live_logcat
echo Starting Live Logs... (Press Ctrl+C to stop)
adb logcat *:E
pause
goto diagnostics

:dumpsys_view
cls
echo --- BATTERY ---
adb shell dumpsys battery | findstr "level"
echo --- RAM ---
adb shell dumpsys meminfo | findstr "Total"
echo --- CPU ---
adb shell dumpsys cpuinfo | head -n 10
echo.
pause
goto diagnostics

:disk_detail
adb shell du -d 1 -h /sdcard/
pause
goto diagnostics
