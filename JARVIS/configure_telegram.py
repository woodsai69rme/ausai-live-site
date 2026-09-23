#!/usr/bin/env python3
"""
JARVIS Telegram Bot Token & Webhook Configuration Utility.
Easily pair your Telegram Bot Token and verify connectivity to your mobile device.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
CONFIG_FILE = JARVIS_DIR / "config.json"


def configure_telegram():
    print("=" * 60)
    print(" 📱 JARVIS TELEGRAM MOBILE BRIDGE CONFIGURATION")
    print("=" * 60)
    print("Instructions to create a free bot:")
    print("1. Open Telegram on your phone/desktop and search for '@BotFather'")
    print("2. Send '/newbot' and follow prompts to get your Bot API Token.")
    print("3. Paste the token below.\n")

    current_token = ""
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            current_token = cfg.get("telegram", {}).get("bot_token", "")
        except Exception:
            pass

    if current_token:
        print(f"Current Token: {current_token[:8]}...{current_token[-6:]}")
        change = input("Do you want to change the token? (y/N): ").strip().lower()
        if change != "y":
            token = current_token
        else:
            token = input("Enter new Telegram Bot Token: ").strip()
    else:
        token = input("Enter Telegram Bot Token: ").strip()

    if not token:
        print("[!] No token provided. Skipping setup.")
        return

    # Test token
    print("[+] Verifying token with Telegram Bot API...")
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                bot_info = data["result"]
                print(f"[✅ SUCCESS] Bot Verified: @{bot_info.get('username')} ({bot_info.get('first_name')})")
                
                # Save to config.json
                cfg = {}
                if CONFIG_FILE.exists():
                    try:
                        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                if "telegram" not in cfg:
                    cfg["telegram"] = {}
                cfg["telegram"]["bot_token"] = token
                CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
                print(f"[+] Saved token to {CONFIG_FILE}")
                print("\nTo start your mobile listener, run:")
                print("python C:\\Users\\karma\\JARVIS\\jarvis_cli.py telegram")
            else:
                print(f"[❌ ERROR] Telegram rejected token: {data.get('description')}")
    except Exception as e:
        print(f"[❌ ERROR] Connection failed: {e}")


if __name__ == "__main__":
    configure_telegram()
