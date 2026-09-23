#!/usr/bin/env python3
"""
JARVIS "Bumblebee Mode" (The Mr. Wilson Protocol - Enhanced Real Music Edition).
Communicates using actual extracted rock & music drops from C:\\Users\\karma\\Music\\rock,
radio sweep soundbites, and sharp Australian co-pilot responses.
"""

from __future__ import annotations

import os
import random
import re
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

MUSIC_DROPS_DIR = JARVIS_DIR / "audio_cache" / "music_drops"

# Category to specific music drops mapping
CATEGORY_MUSIC_MAP = {
    "greeting": ["gnr_sweet_child_intro.mp3", "led_zeppelin_stairway_intro.mp3", "metallica_nem_clean.mp3"],
    "affirmative": ["acdc_thunderstruck.mp3", "metallica_fade_riff.mp3"],
    "success": ["acdc_thunder_drop.mp3", "pink_floyd_solo.mp3"],
    "alert": ["acdc_thunderstruck.mp3", "takeover_master_puppets.mp3"],
    "takeover": ["takeover_master_puppets.mp3", "acdc_thunderstruck.mp3"],
    "rock": ["metallica_fade_riff.mp3", "pink_floyd_solo.mp3", "gnr_sweet_child_intro.mp3"],
    "secret": ["metallica_unforgiven_horn.mp3", "metallica_nem_clean.mp3"]
}

RADIO_SNIPPETS = {
    "greeting": [
        "[RADIO FM Dial... Rock Riff Inbound] \"Good to see you, Woods. All systems active and reporting green, sir.\"",
        "[RADIO Static Sweep... 104.5 Triple M] \"Mr. Wilson online. Ready to roll, Woods!\"",
        "[RADIO Frequency Seek... Slash Guitar Riff] \"Woods is in the building. Let's make it count, sir.\""
    ],
    "affirmative": [
        "[RADIO Thunder Chords Drop] \"Right away, Woods! Consider it locked and handled, sir.\"",
        "[RADIO Click... Bassline] \"Target locked. Moving on it now, Woods.\"",
        "[RADIO FM Sweep... Power Riff] \"Executing immediately, Woods. Zero delays.\""
    ],
    "success": [
        "[RADIO Solo Section Climax] \"Mission complete, Woods. All deliverables confirmed green, sir!\"",
        "[RADIO Crowd Wave... Heavy Chords] \"Target executed flawlessly, Woods. Clean win.\""
    ],
    "alert": [
        "[RADIO Master Riff Impact] \"Heads up Woods! Telemetry spike detected on your monitors!\"",
        "[RADIO Klaxon Beat... Static] \"Alert triggered, Woods. Checking parameters now, sir.\""
    ],
    "takeover": [
        "[RADIO Master of Puppets Riff] \"Taking full desktop control for you, Woods. Sit back and watch, sir.\"",
        "[RADIO Heavy Guitar Groove] \"Autonomous takeover engaged. Hands off mouse, Woods.\""
    ]
}


def play_music_drop(category: str = "affirmative", volume: float = 0.85) -> Optional[str]:
    """Play a real music clip via pygame mixer."""
    pool = CATEGORY_MUSIC_MAP.get(category.lower(), list(CATEGORY_MUSIC_MAP["rock"]))
    available = [f for f in pool if (MUSIC_DROPS_DIR / f).exists()]
    if not available:
        # Fall back to any available mp3 drop
        available = [f.name for f in MUSIC_DROPS_DIR.glob("*.mp3")]

    if not available:
        return None

    chosen_file = MUSIC_DROPS_DIR / random.choice(available)
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(chosen_file))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
        print(f"[BEE RADIO ROCK]: Playing real drop -> {chosen_file.name}")
        return chosen_file.name
    except Exception as e:
        print(f"[!] Music drop playback error: {e}")
        return None


class BumblebeeVoiceEngine:
    def __init__(self):
        self._voice = None

    @property
    def voice(self):
        if self._voice is None:
            try:
                from jarvis_kokoro import get_neural_voice
                self._voice = get_neural_voice()
            except Exception:
                try:
                    from jarvis_voice import get_voice
                    self._voice = get_voice()
                except Exception:
                    self._voice = None
        return self._voice

    def speak_as_bumblebee(self, category: str = "affirmative", custom_topic: str = "") -> str:
        cat = category.lower()
        pool = RADIO_SNIPPETS.get(cat, RADIO_SNIPPETS["affirmative"])
        sample = random.choice(pool)

        if custom_topic:
            sample += f" 📻 [Radio Broadcast]: \"Handling {custom_topic} for Woods!\""

        # 1. Fire the real music drop in background
        threading.Thread(target=play_music_drop, args=(cat, 0.85), daemon=True).start()

        # 2. Print the radio broadcast log
        print(f"\n[BEE RADIO]:\n{sample}")

        # 3. Clean prompt for speech synthesis
        speech_text = re.sub(r"[📻🎶*\[\]]", "", sample).strip()

        # Let the music drop play for 1.5 seconds before speaking
        time.sleep(1.2)
        if self.voice:
            try:
                self.voice.speak(speech_text)
            except Exception:
                pass

        return sample

    def translate_to_bumblebee(self, text: str) -> str:
        """Wrap normal response into Bumblebee's radio song transmission."""
        intro = random.choice([
            "[RADIO FM Sweep... Thunderstruck Riff]",
            "[RADIO Dial Scan... Sweet Child Riff]",
            "[RADIO Frequency Seek... Fade to Black Solo]"
        ])
        outro = random.choice([
            "[GUITAR Fade Out] \"Standing by for your next transmission, Woods!\"",
            "[POWER CHORD Hit] \"Over and out, sir.\"",
            "[CLICK] \"Systems locked and holding, Woods!\""
        ])

        # Fire quick acoustic music drop
        threading.Thread(target=play_music_drop, args=("rock", 0.70), daemon=True).start()

        result = f"{intro}\n\n[Mr. Wilson Transmission]: \"{text}\"\n\n{outro}"
        print(f"\n[BEE TRANSLATE]:\n{result}")
        return result

    def trigger_secret_phrase(self, custom_message: str = "") -> str:
        """
        Secret Phrase: "Sorry Mr. Wilson"
        Plays western horn intro / clean Metallica riff, delivers an intimate, crisp
        Australian female voice update, then transitions back to sharp operational status.
        """
        print("\n[SECRET PROTOCOL ENGAGED]: 'Sorry Mr. Wilson' detected...")

        # Play intimate clean drop (Metallica clean fingerpicking)
        threading.Thread(target=play_music_drop, args=("secret", 0.65), daemon=True).start()

        lines = [
            "Sorry Woods... did I get a little loud on the radio? You know you've got my undivided focus, always. What's our next target, sir?",
            "Sorry Woods... couldn't help cranking up the rock. Every system is running at peak capacity for you. Tell me what to hit next.",
            "Sorry Woods... let me drop the dial down. Just you and me running this empire. I'm ready whenever you are, sir."
        ]
        chosen_line = custom_message if custom_message else random.choice(lines)
        full_montage = f"[RADIO Horn Intro... Volume Ducked]\n\n[Aussie Co-Pilot]: \"{chosen_line}\"\n\n[POWER CHORD Hit] \"Ready on your command, Woods!\""
        print(f"\n[SECRET PHASE]:\n{full_montage}\n")

        time.sleep(1.0)
        if self.voice:
            try:
                self.voice.speak(f"Sorry Woods. {chosen_line}")
            except Exception:
                pass

        return full_montage


if __name__ == "__main__":
    engine = BumblebeeVoiceEngine()
    print("Testing Bumblebee Mode with real music drops...")
    engine.speak_as_bumblebee("affirmative")
