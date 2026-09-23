#!/usr/bin/env python3
"""
JARVIS 24/7 Auto-Restart Supervisor & Process Guardian.
Monitors the JARVIS Web HUD Server (Port 6970) and automatically recovers/restarts it
if it ever terminates or experiences an unhandled exception.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
SERVER_SCRIPT = JARVIS_DIR / "web_hud" / "server.py"
PORT = 6970


def is_port_open(port: int = PORT) -> bool:
    """Check if port is actively listening."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except Exception:
        return False


def run_supervisor():
    print(f"[+] JARVIS 24/7 Supervisor Guardian Active (Monitoring Port {PORT})...")
    server_process = None

    while True:
        try:
            if not is_port_open(PORT):
                print(f"[!] JARVIS server on Port {PORT} is OFFLINE. Spawning process...")
                server_process = subprocess.Popen(
                    [sys.executable, str(SERVER_SCRIPT)],
                    cwd=str(JARVIS_DIR),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                )
                print(f"[+] Spawned JARVIS Server with PID {server_process.pid}. Waiting for socket...")
                time.sleep(3)
            
            time.sleep(5)
        except KeyboardInterrupt:
            print("[*] Supervisor shutting down.")
            if server_process:
                server_process.terminate()
            break
        except Exception as e:
            print(f"[!] Supervisor loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run_supervisor()
