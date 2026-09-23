#!/usr/bin/env python3
"""
JARVIS Empire Master Gateway & Multi-Port Watchdog.
Audits, monitors and launches the entire unified system across all 4 key ports:
• Port 3142: God-Mode AI Command Center (Next.js)
• Port 6970: JARVIS Holographic HUD & REST API
• Port 8000: ResearchOS Suite Web UI
• Port 8088: Smart Money & Crypto Top Buyer API
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Tuple

SERVICES = {
    "GOD_MODE": {
        "name": "God-Mode AI Command Center",
        "port": 3142,
        "url": "http://127.0.0.1:3142",
        "launch_cmd": "npm run dev",
        "cwd": r"C:\Users\karma\ACTIVE_PROJECTS\ai-tools-suite"
    },
    "JARVIS_HUD": {
        "name": "JARVIS Holographic HUD Server",
        "port": 6970,
        "url": "http://127.0.0.1:6970/api/status",
        "launch_cmd": "python C:\\Users\\karma\\JARVIS\\web_hud\\server.py",
        "cwd": r"C:\Users\karma\JARVIS"
    },
    "RESEARCHOS": {
        "name": "ResearchOS Universal Suite",
        "port": 8000,
        "url": "http://127.0.0.1:8000",
        "launch_cmd": "C:\\Users\\karma\\START_RESEARCHOS.bat",
        "cwd": r"C:\Users\karma"
    },
    "CRYPTO_API": {
        "name": "Crypto Top Buyer & Whale Radar API",
        "port": 8088,
        "url": "http://127.0.0.1:8088/api/crypto",
        "launch_cmd": "python C:\\Users\\karma\\TOOLS\\unified_crypto_top_buyer_engine.py --daemon",
        "cwd": r"C:\Users\karma"
    }
}


class EmpireGateway:
    def check_port_status(self, port: int) -> Tuple[bool, str]:
        """Fast non-blocking raw socket check (prevents single-worker HTTP deadlocks)."""
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return True, "ONLINE"
        except Exception:
            return False, "OFFLINE"

    def audit_all_services(self, verbose: bool = False) -> Dict[str, Dict[str, Any]]:
        results = {}
        if verbose:
            print("\n" + "=" * 75)
            print(" 🌐 EMPIRE MASTER GATEWAY: SERVICE HEALTH & STATUS RADAR")
            print("=" * 75)
        
        for key, s in SERVICES.items():
            online, msg = self.check_port_status(s["port"])
            if verbose:
                status_icon = "🟢" if online else "🔴"
                print(f" {status_icon} [{s['port']}] {s['name']:<38} : {msg}")
            results[key] = {
                "name": s["name"],
                "port": s["port"],
                "online": online,
                "status_msg": msg
            }

        if verbose:
            print("=" * 75)
        return results

    def launch_service(self, key: str):
        s = SERVICES.get(key)
        if not s:
            print(f"[!] Unknown service: {key}")
            return

        print(f"[+] Launching {s['name']} on port {s['port']}...")
        if os.path.exists(s["cwd"]):
            subprocess.Popen(s["launch_cmd"], cwd=s["cwd"], shell=True)
        else:
            subprocess.Popen(s["launch_cmd"], shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Empire Gateway")
    parser.add_argument("--audit", action="store_true", help="Audit all service ports")
    parser.add_argument("--launch", type=str, choices=list(SERVICES.keys()) + ["ALL"], help="Launch service")
    args = parser.parse_args()

    gw = EmpireGateway()
    if args.launch:
        if args.launch == "ALL":
            for k in SERVICES:
                gw.launch_service(k)
        else:
            gw.launch_service(args.launch)
    else:
        gw.audit_all_services(verbose=True)
