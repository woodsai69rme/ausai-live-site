@echo off
REM ============================================
REM PHONE CONNECTION TESTER & QUICK CONNECT
REM ============================================

title Android Phone Connection Tester v2.0
color 0A

:start
cls
echo ============================================
echo ANDROID PHONE CONNECTION TESTER v2.0
echo ============================================
echo.
echo Current directory: %CD%
echo.

REM Check if ADB is available
echo [1/4] Checking ADB installation...
set ADB_PATH=adb
where adb >nul 2>nul
if %errorlevel% NEQ 0 (
    if exist "adb.exe" (
        echo ADB found in current directory.
        set PATH=%PATH%;%CD%
    ) else if exist "%AppData%\Roaming\Python\Python313\site-packages\adbutils\binaries\adb.exe" (
        echo ADB found in Python adbutils directory.
        set ADB_PATH="%AppData%\Roaming\Python\Python313\site-packages\adbutils\binaries\adb.exe"
        set PATH=%PATH%;%AppData%\Roaming\Python\Python313\site-packages\adbutils\binaries
    ) else (
        echo.
        echo ERROR: ADB not found!
        echo.
        echo Try selecting "Fix Tools" in the next step.
    )
) else (
    echo ADB is installed and available in PATH.
)

echo.
echo [2/4] Checking Scrcpy installation...
set scrcpy_available=0
where scrcpy >nul 2>nul
if %errorlevel% EQU 0 (
    set scrcpy_available=1
    echo Scrcpy found in PATH.
) else (
    if exist "scrcpy.exe" (
        set scrcpy_available=1
        echo Scrcpy found in current directory.
        set PATH=%PATH%;%CD%
    ) else (
        echo WARNING: Scrcpy not found. Some features will be disabled.
    )
)

echo.
echo [3/4] Checking connected devices...
adb devices

echo.
echo [4/4] Analyzing connection status...
echo.

adb devices | findstr "device$" >nul
if %errorlevel% NEQ 0 (
    echo NO ACTIVE DEVICES DETECTED
    echo ==========================
    echo.
    echo 1. Check USB cable and port
    echo 2. Check if USB Debugging is ON
    echo 3. Install drivers (Samsung/Oppo)
    echo.
    echo If you are trying to connect WIRELESSLY, select option below.
    echo.
) else (
    echo DEVICE DETECTED!
    echo ================
    adb shell getprop ro.product.model
    adb shell getprop ro.product.brand
    echo.
)

REM Check for unauthorized
adb devices | findstr "unauthorized" >nul
if %errorlevel% EQU 0 (
    echo WARNING: Device is UNAUTHORIZED. Please accept prompt on phone.
    echo.
)

echo ============================================
echo MAIN MENU
echo ============================================
echo.
echo 1. Start Scrcpy (Normal)
echo 2. Start Scrcpy (Broken Screen / Low Res)
echo 3. Wireless Connection Wizard (Connect without Cable)
echo 4. Install APK (Drag & Drop)
echo 5. Quick ADB Actions (Touch ID, Reboot, etc.)
echo 6. Samsung Tools
echo 7. Oppo Tools
echo 8. Refresh / Check Connection
echo 9. Advanced Recovery Suite (Dr.Fone Alt)
echo 11. Fix Tools (Download ADB/Scrcpy)
echo 0. Exit
echo.
choice /c 12345678901 /m "Select option: "

if errorlevel 11 goto fix_tools
if errorlevel 10 goto exit
if errorlevel 9 goto recovery_suite
if errorlevel 8 goto start
if errorlevel 7 goto oppo
if errorlevel 6 goto samsung
if errorlevel 5 goto quick_actions
if errorlevel 4 goto install_apk
if errorlevel 3 goto wireless
if errorlevel 2 goto scrcpy_broken
if errorlevel 1 goto scrcpy_normal

:quick_actions
call Quick-ADB-Commands.bat
goto start

:scrcpy_normal
if %scrcpy_available% NEQ 1 goto no_scrcpy
call Android-Scrcpy-Wrapper.bat
goto start

:scrcpy_broken
if %scrcpy_available% NEQ 1 goto no_scrcpy
call Android-Scrcpy-Wrapper.bat
goto start

:wireless
cls
echo ============================================
echo WIRELESS CONNECTION WIZARD
echo ============================================
echo.
echo Prerequisite:
echo 1. Phone must be connected via USB FIRST to set up.
echo 2. PC and Phone must be on the SAME Wi-Fi network.
echo.
echo [A] I am connected via USB, set up wireless now
echo [B] I already set it up, just connect to IP
echo [C] Back
echo.
choice /c ABC /m "Select: "
if errorlevel 3 goto start
if errorlevel 2 goto connect_ip
if errorlevel 1 goto setup_wireless

:setup_wireless
echo.
echo Enabling TCP/IP mode on port 5555...
adb tcpip 5555
echo.
echo Now disconnect the USB cable.
echo.
echo Find your phone's IP address (Settings > About > Status)
echo OR I can try to find it for you if you are still connected...
adb shell ip route > ip_info.txt
findstr "wlan0" ip_info.txt
del ip_info.txt
echo.
set /p ip_addr="Enter Phone IP Address (e.g., 192.168.1.5): "
adb connect %ip_addr%:5555
pause
goto start

:connect_ip
echo.
set /p ip_addr="Enter Phone IP Address: "
adb connect %ip_addr%:5555
pause
goto start

:install_apk
cls
echo ============================================
echo APK INSTALLER
echo ============================================
echo.
echo Drag and drop your .APK file into this window and press Enter.
echo.
set /p apk_path="Path to APK: "
echo Installing...
adb install "%apk_path%"
if %errorlevel% EQU 0 (
    echo Installation Successful!
) else (
    echo Installation Failed.
)
pause
goto start

:samsung
REM (Kept simplified for brevity, logic exists in previous version)
call Quick-ADB-Commands.bat
goto start

:oppo
REM (Kept simplified for brevity)
call Quick-ADB-Commands.bat
goto start

:recovery_suite
call Advanced-Recovery-Suite.bat
goto start

:no_scrcpy
echo.
echo Scrcpy not found. Please download it and place it in this folder.
pause
goto start

:exit
exit /b 0
