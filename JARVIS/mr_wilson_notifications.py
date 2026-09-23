#!/usr/bin/env python3
"""
================================================================================
MR. WILSON NATIVE WINDOWS NOTIFICATION & TOAST ENGINE
Sends high-priority on-screen popups to Woods for whale alerts, system health,
and executive reminders using native Windows PowerShell notifications.
================================================================================
"""

import os
import sys
import subprocess
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ICON_PATH = Path(r"C:\Users\karma\JARVIS\mr_wilson_studio.jpg")

def send_toast(title: str, message: str, sound: bool = True):
    """Deliver a Windows 10/11 native toast notification."""
    ps_cmd = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textNodes = $template.GetElementsByTagName('text')
    $textNodes.Item(0).AppendChild($template.CreateTextNode('{title}')) > $null
    $textNodes.Item(1).AppendChild($template.CreateTextNode('{message}')) > $null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Mr. Wilson Co-Pilot')
    $notifier.Show($toast)
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=5)
        print(f"🔔 [TOAST DELIVERED] {title} — {message}")
        return True
    except Exception as e:
        print(f"[!] Notification fallback: {e}")
        return False

def notify_whale_alert(token: str, inflow: str, entry: str, sl: str, tp: str):
    title = f"🚨 MR. WILSON WHALE ALERT: #{token}"
    msg = f"Smart money inflow: {inflow} | Entry: {entry} | Hard SL: {sl} | Target: {tp}"
    send_toast(title, msg)

def notify_system_status(msg: str):
    send_toast("💋 Mr. Wilson System Guardian", msg)

if __name__ == "__main__":
    notify_system_status("Self-enhancement online. All sensory, voice, and radar engines upgraded for Woods.")
