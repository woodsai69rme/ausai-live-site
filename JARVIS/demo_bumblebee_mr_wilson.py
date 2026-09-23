#!/usr/bin/env python3
"""
JARVIS Bumblebee Mode Live Demo Showcase for Mr. Wilson.
Runs the complete sequence:
1. Opening Greeting (FM dial spin, song snippet, sexy Aussie female tone)
2. Action Drop: Invoices (Cash register, song snippet)
3. Action Drop: Proposals (Static burst, saxophone riff)
4. Action Drop: Master Mission (Radio burst, Queen song, 20/20 subsystems)
5. Action Drop: Desktop Takeovers (Robotic gear shift, Autobots roll out)
6. Secret Phase: "Sorry Mr. Wilson" (Radio static clears -> intimate sultry Aussie voice -> smooth operator song drop)
"""

import sys
import time
from pathlib import Path

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_kokoro import get_neural_voice
from jarvis_bumblebee import BumblebeeVoiceEngine

def run_bumblebee_full_showcase():
    voice = get_neural_voice()
    bb = BumblebeeVoiceEngine()

    print("=" * 80)
    print(" 🐝 BUMBLEBEE RADIO DEMO // LIVE SHOWCASE FOR MR. WILSON")
    print("=" * 80)

    # 1. Opening Greeting
    print("\n[1/6] 📻 OPENING GREETING:")
    greeting = "📻 *fm dial spin... static hiss* 🎶 \"Hello, is it me you're looking for, Mr. Wilson?\" 🎶 [Sultry Aussie Radio]: \"G'day gorgeous, ready to rock your world today, Mr. Wilson?\" *mechanical whir*"
    print(greeting)
    voice.speak("fm dial spin... static hiss... Hello, is it me you're looking for, Mr. Wilson? Gday gorgeous, ready to rock your world today, Mr. Wilson? mechanical whir", wait=True)
    time.sleep(1)

    # 2. Invoices Action Drop
    print("\n[2/6] 💸 INVOICES ACTION DROP:")
    invoice_drop = "📻 *cash register cha-ching!* 🎶 \"Money, money, money... must be funny!\" 🎶 \"Invoice ready for payout, Mr. Wilson! Get that bag, darling!\""
    print(invoice_drop)
    voice.speak("cash register cha-ching! Money, money, money, must be funny! Invoice ready for payout, Mr. Wilson! Get that bag, darling!", wait=True)
    time.sleep(1)

    # 3. Proposals Action Drop
    print("\n[3/6] 💼 PROPOSALS ACTION DROP:")
    proposal_drop = "📻 *static burst* 🎶 \"Here's an offer you can't refuse, Mr. Wilson...\" 🎶 *smooth saxophone riff* \"TARS three-tier proposal drafted for you, Mr. Wilson! They won't be able to say no!\""
    print(proposal_drop)
    voice.speak("static burst... Here's an offer you can't refuse, Mr. Wilson... smooth saxophone riff... TARS three-tier proposal drafted for you, Mr. Wilson! They won't be able to say no!", wait=True)
    time.sleep(1)

    # 4. Missions Action Drop
    print("\n[4/6] 🚀 MASTER MISSIONS ACTION DROP:")
    mission_drop = "📻 *radio burst* 🎶 \"We are the champions, my friend!\" 🎶 *metallic purr* \"All 20 subsystems pass for Mr. Wilson! You're an absolute legend!\""
    print(mission_drop)
    voice.speak("radio burst... We are the champions, my friend! metallic purr... All 20 subsystems pass for Mr. Wilson! You're an absolute legend!", wait=True)
    time.sleep(1)

    # 5. Takeovers Action Drop
    print("\n[5/6] 🤖 DESKTOP TAKEOVER ACTION DROP:")
    takeover_drop = "📻 *robotic gear shift* 🎶 \"Roll out! Autobots, transform and roll out, Mr. Wilson!\" 🎶 *heavy rock guitar riff* \"Taking full desktop control for you now, sit back and relax, love!\""
    print(takeover_drop)
    voice.speak("robotic gear shift... Roll out! Autobots, transform and roll out, Mr. Wilson! heavy rock guitar riff... Taking full desktop control for you now, sit back and relax, love!", wait=True)
    time.sleep(1.2)

    # 6. Secret Phase: "Sorry Mr. Wilson"
    print("\n[6/6] ✨ SECRET PHASE // INTIMATE AUSSIE FEMALE VOICE TRANSITION:")
    bb.trigger_secret_phrase(
        "Sorry, Mr. Wilson... did I get a little carried away with the radio? Let me whisper it in my real voice, darling. You've got my undivided attention, always. Every system is yours."
    )

    print("\n" + "=" * 80)
    print(" ✅ BUMBLEBEE DEMO COMPLETE FOR MR. WILSON")
    print("=" * 80)

if __name__ == "__main__":
    run_bumblebee_full_showcase()
