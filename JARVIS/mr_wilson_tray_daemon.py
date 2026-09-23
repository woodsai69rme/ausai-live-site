#!/usr/bin/env python3
"""
Mr. Wilson: Sovereign System Tray Daemon (v3.0).
Provides a silent, persistent Windows System Tray icon for Woods.
Allows 1-click access to the Companion, Voice Listener, Bumblebee Drops, ATO War Room,
Crypto Radar, YouTube Reviewer, and X: Drive backups without terminal clutter.
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw
import pystray

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
AVATAR_IMG = JARVIS_DIR / "mr_wilson_avatar.jpg"
STUDIO_IMG = JARVIS_DIR / "mr_wilson_studio.jpg"
DASHBOARD_HTML = Path(r"C:\Users\karma\Desktop\MR_WILSON_MASTER_DASHBOARD.html")
WOODATO_EXCEL = Path(r"C:\WOODATO\ATO_REASON_FOR_DECISION_APPENDIX_1_AS_IS.xlsx")


def create_tray_icon_image():
    if AVATAR_IMG.exists():
        try:
            img = Image.open(AVATAR_IMG)
            return img.resize((64, 64), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # Fallback generated icon (neon circle on dark background)
    img = Image.new("RGBA", (64, 64), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=(0, 255, 178), outline=(255, 42, 133), width=3)
    draw.text((22, 20), "W", fill=(0, 0, 0))
    return img


def launch_companion(icon, item):
    script = JARVIS_DIR / "desktop_companion_mr_wilson.py"
    subprocess.Popen([sys.executable, str(script)], creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def trigger_bumblebee_drop(icon, item):
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:6971/api/bumblebee", timeout=3)
    except Exception:
        # Fallback to direct script
        subprocess.Popen([sys.executable, str(JARVIS_DIR / "core" / "jarvis_bumblebee.py")])


def open_dashboard(icon, item):
    if DASHBOARD_HTML.exists():
        os.startfile(str(DASHBOARD_HTML))
    else:
        import webbrowser
        webbrowser.open("http://localhost:6970")


def open_ato(icon, item):
    if WOODATO_EXCEL.exists():
        os.startfile(str(WOODATO_EXCEL))
    else:
        subprocess.Popen([sys.executable, str(JARVIS_DIR / "ato_war_room_mr_wilson.py")], creationflags=subprocess.CREATE_NEW_CONSOLE)


def open_crypto(icon, item):
    import webbrowser
    webbrowser.open("http://localhost:8088")


def open_youtube_reviewer(icon, item):
    subprocess.Popen([sys.executable, str(JARVIS_DIR / "youtube_intel_reviewer.py")], creationflags=subprocess.CREATE_NEW_CONSOLE)


def open_holo_gestures(icon, item):
    subprocess.Popen([sys.executable, str(JARVIS_DIR / "holo_gestures.py")], creationflags=subprocess.CREATE_NEW_CONSOLE)


def sync_backups(icon, item):
    sync_script = JARVIS_DIR / "sync_mr_wilson_vault.py"
    if sync_script.exists():
        subprocess.Popen([sys.executable, str(sync_script)], creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def exit_action(icon, item):
    icon.stop()


def run_tray():
    icon_image = create_tray_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("💋 Mr. Wilson: Sovereign Co-Pilot", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🎬 Show Desktop Companion", launch_companion),
        pystray.MenuItem("🐝 Fire Bumblebee Rock Drop", trigger_bumblebee_drop),
        pystray.MenuItem("📊 Open Master Dashboard", open_dashboard),
        pystray.MenuItem("🇦🇺 Open ATO War Room", open_ato),
        pystray.MenuItem("🐋 Open Crypto Radar (:8088)", open_crypto),
        pystray.MenuItem("📺 Review YouTube Video/Playlist", open_youtube_reviewer),
        pystray.MenuItem("🖐️ Start Holo-Gestures (Hand Control)", open_holo_gestures),
        pystray.MenuItem("💾 Sync Backups to X: Drive", sync_backups),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🚪 Exit Mr. Wilson Tray", exit_action)
    )

    icon = pystray.Icon("MrWilson", icon_image, "Mr. Wilson // Sovereign Co-Pilot", menu)
    print("[*] Mr. Wilson System Tray Daemon active.")
    icon.run()


if __name__ == "__main__":
    run_tray()
