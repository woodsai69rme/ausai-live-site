#!/usr/bin/env python3
"""
Tellem Vision Sorter Bridge for Mr. Wilson (Port 8765).
Launches the Visual Sorter Web App and opens the studio in the default browser.
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOOLS_APP = Path(r"C:\Users\karma\TOOLS\visual_sorter_web_app.py")
STUDIO_URL = "http://localhost:8765"


def main():
    print("=" * 65)
    print(" 🎥 MR. WILSON // TELLEM VISION SORTER STUDIO (PORT 8765)")
    print("=" * 65)

    # Check if already listening on 8765
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_open = s.connect_ex(("127.0.0.1", 8765)) == 0
    s.close()

    if not is_open:
        print(f"[+] Launching Visual Sorter backend from {TOOLS_APP}...")
        if TOOLS_APP.exists():
            subprocess.Popen([sys.executable, "-u", str(TOOLS_APP)])
            time.sleep(2)
        else:
            print(f"[!] Visual sorter script not found at {TOOLS_APP}")
    else:
        print("[+] Visual Sorter Studio is actively online on Port 8765.")

    print(f"[+] Opening {STUDIO_URL} in browser...")
    webbrowser.open(STUDIO_URL)
    print("[✓] Studio connected. Keeping terminal bridge active.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[Mr. Wilson]: Vision sorter bridge disengaged.")


if __name__ == "__main__":
    main()
