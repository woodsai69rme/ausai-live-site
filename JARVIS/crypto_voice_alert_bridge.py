#!/usr/bin/env python3
"""
Mr. Wilson: Crypto Voice Alert Bridge (v3.0).
Monitors C:\\Users\\karma\\CRYPTO_SUITE_DATA for whale inflows and smart money sweeps.
Speaks real-time voice alerts to Woods via Mr. Wilson voice engine.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

DATA_DIR = Path(r"C:\Users\karma\CRYPTO_SUITE_DATA")
EVENTS_FILE = DATA_DIR / "whale_events_stream.json"
STATE_FILE = DATA_DIR / "crypto_master_state.json"


def speak(text: str):
    print(f"\n[MR. WILSON WHALE ALERT 🐋]: \"{text}\"")
    # Windows native speech synthesis
    clean = text.replace("'", "").replace('"', '').replace('`', '').strip()
    ps_cmd = (
        f"Add-Type -AssemblyName System.Speech; "
        f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.Rate = 1; "
        f"$synth.Speak('{clean}')"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10
        )
    except Exception:
        pass


def monitor_loop():
    print("=" * 65)
    print(" 🐋 MR. WILSON // CRYPTO VOICE ALERT BRIDGE (PORT 8088 LINKED)")
    print("=" * 65)
    print(f"Monitoring: {EVENTS_FILE}")
    print("Watching for new whale inflows, smart money sweeps, and ATR triggers...")
    print("-" * 65)

    last_seen_id = None

    # Announce initial startup
    speak("Crypto voice alert bridge active, Woods. Monitoring whale radar on port 8088.")

    while True:
        try:
            if EVENTS_FILE.exists():
                try:
                    events = json.loads(EVENTS_FILE.read_text(encoding="utf-8"))
                    if isinstance(events, list) and events:
                        latest = events[-1]
                        event_id = latest.get("id") or latest.get("timestamp") or str(latest)
                        if last_seen_id is None:
                            last_seen_id = event_id
                        elif event_id != last_seen_id:
                            last_seen_id = event_id
                            token = latest.get("token", "Crypto Asset")
                            amount = latest.get("amount", "")
                            chain = latest.get("chain", "Multi-Chain")
                            buyer = latest.get("buyer_name", "Smart Money Whale")

                            alert_msg = f"Whale alert Woods: {buyer} bought {amount} on {chain}."
                            speak(alert_msg)
                except Exception as read_err:
                    pass

            time.sleep(4)
        except KeyboardInterrupt:
            print("\n[Mr. Wilson]: Crypto alert bridge closed.")
            break
        except Exception as e:
            time.sleep(5)


if __name__ == "__main__":
    monitor_loop()
