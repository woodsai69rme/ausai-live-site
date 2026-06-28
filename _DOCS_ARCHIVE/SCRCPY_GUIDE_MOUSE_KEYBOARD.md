# Scrcpy Advanced Features Guide

## 🖱️ Mouse & Keyboard Control
By default, Scrcpy allows you to use your PC's peripherals to control the Android device.

### Standard Controls
*   **Left Click:** Tap
*   **Right Click:** Back (or Power on some devices)
*   **Middle Click:** Home
*   **Scroll Wheel:** Scroll
*   **Keyboard:** Typing on PC types on Phone (Standard text injection)

### Shortcuts (Hold Left Alt or Ctrl)
| Shortcut | Action |
| :--- | :--- |
| **Alt + f** | Switch Fullscreen |
| **Alt + h** | Home |
| **Alt + b** | Back |
| **Alt + s** | Switch App (Recent) |
| **Alt + m** | Menu |
| **Alt + p** | Power On/Off |
| **Alt + o** | Turn Screen OFF (Keep Mirroring) |
| **Alt + r** | Rotate Screen |
| **Alt + n** | Expand Notification Panel |

---

## 🖥️ Screen Mirroring Options (v3.0 Script)

### 1. Standard Mode
The default experience. High quality, audio forwarded.

### 2. Broken Screen Mode
*   **Screen Off:** The physical phone screen goes black to save battery and prevent "ghost touches" from a cracked digitizer.
*   **Low Res:** 1024px width. ensures smooth frame rates even on older phones.
*   **Stay Awake:** Prevents the phone from locking while you are working on it.

### 3. Visual Help / Dead Touch
*   **Show Touches:** Highlights exactly where you click with a white dot. Essential if the screen is working but you are unsure if clicks are registering.
*   **Always On Top:** Forces the window to stay above your browser/file explorer.

### 4. OTG Mode (Emergency)
**Crucial for "USB Debugging Disabled" scenarios.**
If you cannot enable USB Debugging because the screen is broken:
1.  Run `Android-Scrcpy-Wrapper.bat` -> Option **4**.
2.  Select **Mouse Only**.
3.  Your PC mouse now acts as a *physical USB mouse* plugged into the phone.
4.  You can use this to blindly (or with HDMI out) click "Allow" on the USB debugging prompt!
*Requires Android 10+.*

---

## 🔊 Audio & Recording
*   **Audio:** Forwarded automatically on Android 11+.
*   **Recording:** Option 5 in the menu saves an `.mp4` file of your session.

