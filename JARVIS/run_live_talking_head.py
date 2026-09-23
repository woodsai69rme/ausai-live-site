#!/usr/bin/env python3
"""
Mr. Wilson Live Talking Head / Avatar Launcher.
Runs desktop_companion_mr_wilson.py.
"""

import sys
import subprocess
from pathlib import Path

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
COMPANION_SCRIPT = JARVIS_DIR / "desktop_companion_mr_wilson.py"

if __name__ == "__main__":
    print("[*] Launching Mr. Wilson Live Companion Avatar...")
    if COMPANION_SCRIPT.exists():
        subprocess.run([sys.executable, str(COMPANION_SCRIPT)])
    else:
        print(f"[!] Companion script not found at {COMPANION_SCRIPT}")
