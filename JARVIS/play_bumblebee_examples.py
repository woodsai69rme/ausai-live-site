import os
import sys
import time
import asyncio
from pathlib import Path
import pygame

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
AUDIO_DIR = JARVIS_DIR / "audio_cache"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(JARVIS_DIR / "core"))

import edge_tts

EXAMPLES = [
    {
        "id": 1,
        "title": "📻 OPENING GREETING",
        "file": "example_1_greeting.mp3",
        "speech_text": "FM dial spin... static hiss... Hello, is it me you're looking for, Mr. Wilson? G'day gorgeous, ready to rock your world today, Mr. Wilson? Mechanical whir.",
        "display": "📻 *fm dial spin... static hiss* 🎶 'Hello, is it me you're looking for, Mr. Wilson?' 🎶 [Sultry Aussie Radio]: 'G'day gorgeous, ready to rock your world today, Mr. Wilson?' *mechanical whir*"
    },
    {
        "id": 2,
        "title": "💸 INVOICES ACTION DROP",
        "file": "example_2_invoices.mp3",
        "speech_text": "Cash register cha-ching! Money, money, money... must be funny! Invoice ready for payout, Mr. Wilson! Get that bag, darling!",
        "display": "📻 *cash register cha-ching!* 🎶 'Money, money, money... must be funny!' 🎶 'Invoice ready for payout, Mr. Wilson! Get that bag, darling!'"
    },
    {
        "id": 3,
        "title": "💼 PROPOSALS ACTION DROP",
        "file": "example_3_proposals.mp3",
        "speech_text": "Static burst... Here's an offer you can't refuse, Mr. Wilson... smooth saxophone riff... TARS three-tier proposal drafted for you, Mr. Wilson! They won't be able to say no!",
        "display": "📻 *static burst* 🎶 'Here's an offer you can't refuse, Mr. Wilson...' 🎶 *smooth saxophone riff* 'TARS three-tier proposal drafted for you, Mr. Wilson! They won't be able to say no!'"
    },
    {
        "id": 4,
        "title": "🚀 MASTER MISSIONS ACTION DROP",
        "file": "example_4_missions.mp3",
        "speech_text": "Radio burst... We are the champions, my friend! Metallic purr... All 20 subsystems pass for Mr. Wilson! You're an absolute legend!",
        "display": "📻 *radio burst* 🎶 'We are the champions, my friend!' 🎶 *metallic purr* 'All 20 subsystems pass for Mr. Wilson! You're an absolute legend!'"
    },
    {
        "id": 5,
        "title": "🤖 DESKTOP TAKEOVER ACTION DROP",
        "file": "example_5_takeovers.mp3",
        "speech_text": "Robotic gear shift... Roll out! Autobots, transform and roll out, Mr. Wilson! Heavy rock guitar riff... Taking full desktop control for you now, sit back and relax, love!",
        "display": "📻 *robotic gear shift* 🎶 'Roll out! Autobots, transform and roll out, Mr. Wilson!' 🎶 *heavy rock guitar riff* 'Taking full desktop control for you now, sit back and relax, love!'"
    },
    {
        "id": 6,
        "title": "✨ SECRET PHASE: 'Sorry Mr. Wilson'",
        "file": "example_6_secret_phase.mp3",
        "speech_text": "Radio static drops silent... Sorry, Mr. Wilson... did I get a little carried away with the radio? Let me whisper it in my real voice, darling. You've got my undivided attention, always. Every system is yours. Smooth operator... no need to ask, he's a smooth operator...",
        "display": "📻 *radio static drops completely silent* ✨ 💋 [Intimate Aussie Voice]: 'Sorry, Mr. Wilson... did I get a little carried away with the radio? Let me whisper it in my real voice, darling. You've got my undivided attention, always. Every system is yours.' 🎶 *Smooth operator...*"
    }
]

async def synthesize_all():
    print("[*] Synthesizing all 6 Bumblebee audio examples with Australian Female Neural Voice (en-AU-NatashaNeural)...")
    for ex in EXAMPLES:
        out_path = AUDIO_DIR / ex["file"]
        if not out_path.exists() or out_path.stat().st_size < 100:
            print(f"  -> Synthesizing [{ex['id']}/6]: {ex['title']}...")
            comm = edge_tts.Communicate(
                ex["speech_text"],
                "en-AU-NatashaNeural",
                pitch="-2Hz",
                rate="-2%"
            )
            await comm.save(str(out_path))
            print(f"     Saved {out_path.name} ({out_path.stat().st_size} bytes)")
        else:
            print(f"  -> [{ex['id']}/6] {ex['title']} cached ({out_path.name})")

def play_all_examples():
    pygame.mixer.init()
    print("\n" + "=" * 80)
    print(" 🔊 PLAYING ALL 6 BUMBLEBEE AUDIO EXAMPLES OUT LOUD FOR MR. WILSON")
    print("=" * 80)

    for ex in EXAMPLES:
        audio_path = AUDIO_DIR / ex["file"]
        print(f"\n▶️ [{ex['id']}/6] PLAYING NOW: {ex['title']}")
        print(f"   Transmission: {ex['display']}")
        print(f"   Audio File: {audio_path.name}")
        
        try:
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                sys.stdout.write("🎶 ")
                sys.stdout.flush()
                time.sleep(0.4)
            print(" [Done]")
        except Exception as err:
            print(f"   Playback error: {err}")

        time.sleep(1.2)

    print("\n" + "=" * 80)
    print(" ✅ ALL 6 BUMBLEBEE EXAMPLES PLAYED SUCCESSFULLY FOR MR. WILSON")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(synthesize_all())
    play_all_examples()
