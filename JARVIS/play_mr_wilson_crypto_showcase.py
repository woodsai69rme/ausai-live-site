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

MUSIC_TRACK = r"C:\Users\karma\Music\For Woods, I need a loyal stride No talk (1).mp3"

DROPS = [
    {
        "id": 1,
        "title": "💰 1. MORNING ALPHA // MR. WILSON TO WOODS",
        "text": "G'day Woods. It's Mr. Wilson. Markets are waking up, Solana is looking primed, and our bots are fully loaded. Let's make some serious money today, handsome.",
        "voice_file": "drop_1_morning_alpha.mp3"
    },
    {
        "id": 2,
        "title": "🐋 2. WHALE COPY-TRADE ALERT",
        "text": "Woods, check the radar. Smart money just dropped a massive buy into Solana on the dip. Signal verified, risk parameters locked. We're riding this wave together, love.",
        "voice_file": "drop_2_whale_snipe.mp3"
    },
    {
        "id": 3,
        "title": "💸 3. MILESTONE PROFIT SWEEPER",
        "text": "Take-profit hit on the fifteen-minute candle, Woods. Another twelve hundred bucks locked straight into USDC. That bag is secure, darling.",
        "voice_file": "drop_3_profit_sweeper.mp3"
    },
    {
        "id": 4,
        "title": "🤖 4. CHEEKY DESKTOP TAKEOVER (NO HEAVY METAL)",
        "text": "Hands off the keys, Woods. Let Mr. Wilson take the wheel for five minutes while you kick back and sip your coffee. Autobots roll out... smooth and lethal.",
        "voice_file": "drop_4_cheeky_takeover.mp3"
    },
    {
        "id": 5,
        "title": "💋 5. SECRET PHASE (SORRY MR. WILSON)",
        "text": "Sorry, Mr. Wilson... did I get a little too cheeky? Let me whisper it in your ear. You and me, Woods... we're taking over this whole crypto game. You've got my undivided attention, always.",
        "voice_file": "drop_5_secret_sultry.mp3"
    }
]

def play_all_drops_chill():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    print("\n" + "=" * 80)
    print(" 🔊 MR. WILSON LIVE RADIO // CHILL & MELLOW VOLUME (MUSIC NOT TOO LOUD) FOR WOODS")
    print("=" * 80)

    for d in DROPS:
        voice_path = AUDIO_DIR / d["voice_file"]
        print(f"\n▶️ [{d['id']}/5] BROADCASTING: {d['title']}")
        
        if d["id"] == 5:
            # Secret phase: Beat cuts to silence, whisper, then soft chill groove
            print("🛑 [BEAT CUTS TO SILENCE]: Intimate whisper protocol...")
            pygame.mixer.music.stop()
            time.sleep(0.6)
            
            snd = pygame.mixer.Sound(str(voice_path))
            snd.set_volume(1.0)
            print(f"💋 [HOT AUSSIE CHICK // MR. WILSON]: \"{d['text']}\"")
            snd.play()
            time.sleep(snd.get_length() + 0.4)
            
            # Chill gentle beat returns
            print("🎵 [GENTLE CHILL GROOVE RETURNS (20% VOLUME)]...")
            pygame.mixer.music.load(MUSIC_TRACK)
            pygame.mixer.music.set_volume(0.20)
            pygame.mixer.music.play()
            time.sleep(3.5)
            pygame.mixer.music.fadeout(1000)
            time.sleep(1.0)
        else:
            # Chill mellow background: 18% base, 5% ducked, 22% swell
            pygame.mixer.music.load(MUSIC_TRACK)
            pygame.mixer.music.set_volume(0.18)
            pygame.mixer.music.play()
            print("🎵 [MELLOW BEAT AT 18% (CHILL, NOT LOUD)]...")
            time.sleep(2.5)

            print("🎙️ [DUCKING MUSIC TO 5%]: Voice crystal clear...")
            pygame.mixer.music.set_volume(0.05)
            time.sleep(0.2)

            snd = pygame.mixer.Sound(str(voice_path))
            snd.set_volume(1.0)
            print(f"💋 [HOT AUSSIE CHICK // MR. WILSON]: \"{d['text']}\"")
            snd.play()
            time.sleep(snd.get_length() + 0.3)

            print("🎵 [GENTLE SWELL TO 22% (NEVER LOUD)]...")
            pygame.mixer.music.set_volume(0.22)
            time.sleep(3.0)

            pygame.mixer.music.fadeout(800)
            time.sleep(0.8)

        time.sleep(0.8)

    pygame.mixer.quit()
    print("\n" + "=" * 80)
    print(" ✅ ALL 5 CHILL DROPS COMPLETED CLEANLY FOR WOODS")
    print("=" * 80)

if __name__ == "__main__":
    play_all_drops_chill()
