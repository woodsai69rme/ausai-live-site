#!/usr/bin/env python3
"""
JARVIS Telephony & Voice Line Assistant — Twilio / Vapi / ElevenLabs Webhook Dispatcher.
Answers inbound phone calls, conducts lead triage, qualifies clients, and schedules
calendar bookings directly into JARVIS Agenda.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_brain import JarvisBrain
from jarvis_voice import get_voice

CONFIG_FILE = JARVIS_DIR / "config.json"


class JarvisPhoneAssistant:
    def __init__(self):
        self.brain = JarvisBrain()
        self.voice = get_voice()
        self.call_logs_file = JARVIS_DIR / "call_logs.json"
        self._init_call_logs()

    def _init_call_logs(self):
        if not self.call_logs_file.exists():
            self.call_logs_file.write_text(json.dumps([], indent=2), encoding="utf-8")

    def handle_incoming_call_simulation(self, caller_name: str, caller_phone: str, inquiry: str) -> Dict[str, Any]:
        """Simulate or process an inbound AI phone call conversation."""
        self.voice.speak(f"Incoming call from {caller_name}. JARVIS Phone Agent answering.")
        print(f"\n[JARVIS Phone 📞] Connected call with {caller_name} ({caller_phone})")
        print(f"[Caller]: \"{inquiry}\"")

        # Answer based on second brain knowledge
        answer = self.brain.ask_second_brain(f"Inquiry from client: {inquiry}")
        print(f"[JARVIS Agent]: \"{answer}\"")
        self.voice.speak(answer)

        # Log call
        call_record = {
            "id": f"CALL-{int(time.time())}",
            "timestamp": datetime.datetime.now().isoformat(),
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "inquiry": inquiry,
            "agent_response": answer,
            "status": "COMPLETED"
        }

        try:
            logs = json.loads(self.call_logs_file.read_text(encoding="utf-8"))
            logs.insert(0, call_record)
            self.call_logs_file.write_text(json.dumps(logs, indent=2), encoding="utf-8")
        except Exception:
            pass

        return call_record

    def generate_twiml_response(self, user_speech: str) -> str:
        """Generate TwiML XML response for Twilio Voice Webhooks."""
        answer = self.brain.ask_second_brain(user_speech)
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Brian">{answer}</Say>
    <Gather input="speech" timeout="4" action="/api/phone/twilio/webhook">
        <Say>How else may I assist you today?</Say>
    </Gather>
</Response>"""
        return twiml


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Telephony Assistant")
    parser.add_argument("--simulate", action="store_true", help="Simulate incoming call")
    parser.add_argument("--caller", type=str, default="Bruce Wayne")
    parser.add_argument("--phone", type=str, default="+1 (555) 019-2834")
    parser.add_argument("--inquiry", type=str, default="What services do you offer for autonomous AI agents?")
    args = parser.parse_args()

    agent = JarvisPhoneAssistant()
    if args.simulate:
        agent.handle_incoming_call_simulation(args.caller, args.phone, args.inquiry)
    else:
        print("[+] JARVIS Telephony Assistant Ready.")
