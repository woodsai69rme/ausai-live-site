#!/usr/bin/env python3
"""
JARVIS Telegram Mobile Voice & Remote Operations Bridge.
Allows you to control your PC, send voice notes from your smartphone, generate invoices,
execute desktop takeover tasks, and receive PDF files & screenshots directly in Telegram.
"""

from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_arrow import show_ai_arrow_by_query
from jarvis_brain import JarvisBrain
from jarvis_invoice import JarvisInvoiceEngine
from jarvis_takeover import JarvisAutonomousTakeover
from jarvis_vision import get_vision
from jarvis_voice import get_voice

CONFIG_FILE = JARVIS_DIR / "config.json"


class JarvisTelegramBridge:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or self._load_bot_token()
        self.running = False
        self.last_update_id = 0
        self.vision = get_vision()
        self.voice = get_voice()
        self.brain = JarvisBrain()
        self.invoice_engine = JarvisInvoiceEngine()

    def _load_bot_token(self) -> str:
        if CONFIG_FILE.exists():
            try:
                cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                return cfg.get("telegram", {}).get("bot_token", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
            except Exception:
                pass
        return os.environ.get("TELEGRAM_BOT_TOKEN", "")

    def _api_call(self, method: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform HTTP request to Telegram Bot API."""
        if not self.bot_token:
            return {"ok": False, "description": "No bot token configured."}

        url = f"https://api.telegram.org/bot{self.bot_token}/{method}"
        try:
            if data:
                encoded = json.dumps(data).encode("utf-8")
                req = urllib.request.Request(url, data=encoded, headers={"Content-Type": "application/json"})
            else:
                req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "description": str(e)}

    def send_message(self, chat_id: int | str, text: str) -> Dict[str, Any]:
        """Send formatted markdown text message to Telegram chat."""
        return self._api_call("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

    def send_document(self, chat_id: int | str, file_path: str | Path, caption: str = "") -> Dict[str, Any]:
        """Upload and send document (PDF/HTML) to Telegram chat using multipart form data."""
        if not self.bot_token:
            return {"ok": False, "description": "No bot token configured."}

        path = Path(file_path)
        if not path.exists():
            return {"ok": False, "description": f"File not found: {path}"}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        boundary = "----JarvisBoundary" + str(int(time.time()))
        
        body = io.BytesIO()
        # Chat ID field
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
        
        # Caption field
        if caption:
            body.write(f"--{boundary}\r\n".encode())
            body.write(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode())

        # Document field
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="document"; filename="{path.name}"\r\n'.encode())
        body.write(f"Content-Type: {mime}\r\n\r\n".encode())
        body.write(path.read_bytes())
        body.write(f"\r\n--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            url,
            data=body.getvalue(),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "description": str(e)}

    def send_photo(self, chat_id: int | str, photo_path: str | Path, caption: str = "") -> Dict[str, Any]:
        """Upload and send screenshot image to Telegram."""
        if not self.bot_token:
            return {"ok": False, "description": "No bot token configured."}

        path = Path(photo_path)
        if not path.exists():
            return {"ok": False, "description": f"Photo not found: {path}"}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        boundary = "----JarvisPhotoBoundary" + str(int(time.time()))
        
        body = io.BytesIO()
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
        if caption:
            body.write(f"--{boundary}\r\n".encode())
            body.write(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode())

        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="photo"; filename="{path.name}"\r\n'.encode())
        body.write(b"Content-Type: image/png\r\n\r\n")
        body.write(path.read_bytes())
        body.write(f"\r\n--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            url,
            data=body.getvalue(),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "description": str(e)}

    def process_command(self, chat_id: int | str, text: str):
        """Process incoming text or voice transcript and route to JARVIS modules."""
        t_clean = text.strip()
        lower = t_clean.lower()
        print(f"[JARVIS Telegram 📱] Received from chat {chat_id}: '{t_clean}'")

        if lower.startswith("/start") or lower == "help":
            help_msg = (
                "⚡ *JARVIS Autonomous Copilot Bridge*\n\n"
                "Available commands:\n"
                "• `invoice <details>` — Generate PDF invoice\n"
                "• `takeover <task>` — Execute desktop task\n"
                "• `screen` — Capture live desktop screenshot\n"
                "• `arrow <element>` — Point AI arrow at UI button\n"
                "• `agenda` — View today's schedule & briefing\n"
                "• `ask <question>` — Search second brain & memory"
            )
            self.send_message(chat_id, help_msg)

        elif lower.startswith("invoice") or lower.startswith("/invoice") or "bill " in lower:
            prompt = re.sub(r"^/?invoice\s*", "", t_clean, flags=re.IGNORECASE)
            self.send_message(chat_id, f"⏳ Processing invoice for: _{prompt}_ ...")
            
            res = self.invoice_engine.process_voice_note_to_invoice(prompt)
            pdf_file = res.get("pdf_path")
            inv_data = res.get("invoice_data", {})
            
            caption = f"✅ *Invoice #{inv_data.get('invoice_number')}*\nClient: {inv_data.get('client_name')}\nTotal: ${inv_data.get('total_amount'):,.2f}"
            if pdf_file and Path(pdf_file).exists():
                self.send_document(chat_id, pdf_file, caption=caption)
            else:
                self.send_message(chat_id, caption)

        elif lower == "screen" or lower.startswith("/screen") or lower.startswith("/shot"):
            self.send_message(chat_id, "📸 Capturing live desktop frame...")
            path, _ = self.vision.capture_screen("telegram_live.png")
            desc = self.vision.describe_screen()
            self.send_photo(chat_id, path, caption=f"🖥️ *Desktop View*\n{desc[:300]}")

        elif lower.startswith("takeover") or lower.startswith("/takeover"):
            task = re.sub(r"^/?takeover\s*", "", t_clean, flags=re.IGNORECASE)
            self.send_message(chat_id, f"🤖 *Autonomous Takeover Started:*\n_{task}_")
            
            def _async_takeover():
                agent = JarvisAutonomousTakeover()
                res = agent.run_takeover(task)
                path, _ = self.vision.capture_screen("takeover_completed.png")
                self.send_photo(chat_id, path, caption=f"✅ *Takeover Finished!*\nSteps executed: {res.get('steps_executed')}")

            threading.Thread(target=_async_takeover, daemon=True).start()

        elif lower.startswith("arrow") or lower.startswith("/arrow"):
            target = re.sub(r"^/?arrow\s*", "", t_clean, flags=re.IGNORECASE)
            self.send_message(chat_id, f"🎯 Pointing AI arrow at: _{target}_")
            coords = show_ai_arrow_by_query(target, mode="guide")
            if coords:
                self.send_message(chat_id, f"✅ Target located at `({coords[0]}, {coords[1]})`.")
            else:
                self.send_message(chat_id, f"❌ Could not visually ground `{target}`.")

        elif lower == "agenda" or lower.startswith("/agenda"):
            summary = self.brain.get_agenda_summary()
            self.send_message(chat_id, summary)

        else:
            ans = self.brain.ask_second_brain(t_clean)
            self.send_message(chat_id, f"🧠 *JARVIS:* {ans}")

    def poll_updates(self):
        """Continuous polling loop for Telegram updates."""
        print(f"[+] JARVIS Telegram Bridge Polling Active. (Bot token: {'CONFIGURED' if self.bot_token else 'NOT SET'})")
        if not self.bot_token:
            print("[!] Please set your Telegram bot token in C:\\Users\\karma\\JARVIS\\config.json under 'telegram.bot_token'.")
            return

        self.running = True
        while self.running:
            try:
                res = self._api_call("getUpdates", {"offset": self.last_update_id + 1, "timeout": 15})
                if res.get("ok"):
                    for update in res.get("result", []):
                        self.last_update_id = update["update_id"]
                        msg = update.get("message", {})
                        chat_id = msg.get("chat", {}).get("id")
                        text = msg.get("text")
                        
                        if chat_id and text:
                            self.process_command(chat_id, text)
                time.sleep(0.5)
            except KeyboardInterrupt:
                break
            except Exception as e:
                time.sleep(2.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Telegram Bridge")
    parser.add_argument("--token", type=str, default=None, help="Telegram Bot Token")
    parser.add_argument("--test-msg", type=str, default=None, help="Simulate local message command")
    args = parser.parse_args()

    bridge = JarvisTelegramBridge(bot_token=args.token)
    if args.test_msg:
        bridge.process_command("LOCAL_TEST", args.test_msg)
    else:
        bridge.poll_updates()
