# Android Recovery Toolkit - Quick Reference Guide

## Quick Start

### Launch the Toolkit
```
Double-click: Android-Recovery-Toolkit-Launcher.bat
```

### Main Menu Options
- **A** - Connection & Diagnostics
- **B** - Screen Mirroring & Control  
- **C** - Quick ADB Commands
- **D** - Recovery & Emergency Tools
- **E** - Emergency Data Recovery
- **F** - Advanced Forensics Toolkit
- **G** - ADB Enhancement Toolkit
- **H** - Phone Info & Status Tool
- **I** - Enhanced GUI Application
- **J** - Enhanced Web Interface
- **0** - Exit

## Common Tasks

### Check Device Connection
```
Menu: A → 1. Enhanced Connection Tester
```

### Screen Mirroring (Normal)
```
Menu: B → Standard Mirroring
```

### Screen Mirroring (Broken Screen)
```
Menu: B → Broken Screen Mode
```

### Data Extraction
```
Menu: E → Data Extraction
```
Or: Menu: D → 1. Data Extraction

### System Backup
```
Menu: D → 2. Phone Backup
```

### Screen Unlock
```
Menu: D → 4. Screen Unlock Tools
```

### Quick ADB Commands
```
Menu: C → Various quick commands
```

## ADB Quick Commands

### Navigation
```
adb shell input keyevent KEYCODE_HOME     # Home button
adb shell input keyevent KEYCODE_BACK     # Back button  
adb shell input keyevent KEYCODE_APP_SWITCH  # Recent apps
adb shell input keyevent KEYCODE_POWER    # Power button
```

### Screen Control
```
adb shell input tap X Y                  # Tap at coordinates
adb shell input swipe X1 Y1 X2 Y2       # Swipe gesture
adb shell screencap -p /sdcard/screen.png # Take screenshot
adb shell input text "hello"             # Type text
```

### Device Management
```
adb devices                              # List connected devices
adb reboot                              # Reboot device
adb reboot recovery                     # Reboot to recovery
adb reboot bootloader                   # Reboot to bootloader
```

## Scrcpy Quick Commands

### Basic Usage
```
scrcpy                                  # Normal mirroring
scrcpy --turn-screen-off               # Turn device screen off
scrcpy --max-size 1024                 # Limit resolution
scrcpy --record file.mp4               # Record session
```

### Keyboard Shortcuts
- **Ctrl+H**: Home
- **Ctrl+B**: Back  
- **Ctrl+S**: Recent apps
- **Ctrl+M**: Menu
- **Ctrl+P**: Power
- **Ctrl+R**: Rotate screen
- **Ctrl+C**: Copy
- **Ctrl+V**: Paste

## Emergency Procedures

### Device with Broken Screen
1. Connect via USB
2. Menu: B → Broken Screen Mode
3. Control device with mouse/keyboard

### Data Recovery (Emergency)
1. Connect via USB
2. Menu: E → Emergency Data Recovery
3. Follow prompts to extract data

### Screen Unlock (Pattern/Lock)
1. Menu: D → 4. Screen Unlock Tools
2. Select appropriate method
3. Follow instructions carefully

### Factory Reset (Last Resort)
1. Menu: D → 4. Screen Unlock Tools
2. Select Factory Reset option
3. Type "YES" to confirm (WARNING: Erases all data)

## Wireless ADB Setup

### Initial Setup
1. Connect device via USB
2. Menu: A → 2. Wireless Connection Wizard
3. Select "A" for setup
4. Note device IP address
5. Disconnect USB
6. Connect wirelessly

### Connect to Known IP
1. Menu: A → 2. Wireless Connection Wizard  
2. Select "B" for known IP
3. Enter IP address when prompted

## Troubleshooting Quick Fixes

### Device Not Found
```
adb kill-server
adb start-server
```

### Unauthorized Device
- On device: Tap "Allow USB debugging"
- If screen broken: Use OTG mouse to click "Allow"

### Scrcpy Black Screen
- Ensure device screen is on
- Try: `scrcpy --render-expired-frames`
- Lower resolution settings

### Slow Performance
- Use: `scrcpy --max-size 1024 --max-fps 15`
- Close other applications
- Use faster USB connection

## Security Notes

### Input Validation
- IP addresses: XXX.XXX.XXX.XXX format
- Serial numbers: Alphanumeric only
- File paths: No system directory access
- Package names: com.example.format

### Safe Operations
- Always backup before destructive operations
- Verify device before factory reset
- Use authorized devices only
- Disable USB debugging when done

## GUI Application Quick Access

### Launch GUI
```
Menu: I → Enhanced GUI Application
```
Or run: `python gui_app.py`

### GUI Tabs
- **Connection & Diagnostics**: Device status
- **Control & Mirroring**: Screen control
- **Recovery & Data**: Data operations  
- **Additional Tools**: Utilities
- **Console Output**: Command logs

## Common Error Messages

### "Invalid IP address format"
- Check format: XXX.XXX.XXX.XXX
- Each number must be 0-255

### "Invalid serial number format" 
- Use only letters, numbers, hyphens, periods, colons

### "Invalid folder path"
- Cannot access system directories like /data/, /system/

### "Invalid package name format"
- Use format: com.example.application

## Recovery Key Combinations

### Samsung
- **Bootloader**: Vol Down + Home + Power
- **Recovery**: Vol Up + Home + Power

### Oppo  
- **Bootloader**: Vol Down + Power (hold 10+ sec)
- **Recovery**: Vol Up + Power (hold 10+ sec)

### Generic
- **Bootloader**: Vol Down + Power
- **Recovery**: Vol Up + Power

## File Locations

### Toolkit Files
- Main launcher: `Android-Recovery-Toolkit-Launcher.bat`
- Enhanced tester: `Enhanced-Phone-Connection-Tester.bat`
- Enhanced scrcpy: `Enhanced-Android-Scrcpy-Wrapper.bat`
- Enhanced recovery: `Enhanced-Advanced-Recovery-Suite.bat`
- GUI app: `gui_app.py`

### Output Locations
- Screenshots: Current directory
- Recordings: Current directory  
- Backups: Current directory
- Logs: Console output

## Safety Reminders

⚠️ **Always backup data before operations**
⚠️ **Only use on authorized devices** 
⚠️ **Factory reset erases all data**
⚠️ **Disable USB debugging when finished**
⚠️ **Verify IP addresses and serials**
⚠️ **Be cautious with system directories**