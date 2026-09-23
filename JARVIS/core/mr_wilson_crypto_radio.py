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

# Natural, human-written lines specifically for Woods (NO robotic stage directions!)
DROPS = [
    {
        "id": "crypto_morning",
        "title": "💰 MORNING ALPHA // MR. WILSON TO WOODS",
        "text": "G'day Woods. It's Mr. Wilson. Markets are waking up, Solana is looking primed, and our bots are fully loaded. Let's make some serious money today, handsome.",
        "voice_file": "mr_wilson_morning_alpha.mp3"
    },
    {
        "id": "crypto_whale",
        "title": "🐋 WHALE ALERT // TOP BUYER COPY-TRADE",
        "text": "Woods, check the radar. Smart money just dropped a massive buy into Solana on the dip. Signal verified, risk parameters locked. We're riding this wave together, love.",
        "voice_file": "mr_wilson_whale_snipe.mp3"
    },
    {
        "id": "secret_phase",
        "title": "💋 SECRET PHASE // INTIMATE WHISPER (SORRY MR. WILSON)",
        "text": "Sorry, Mr. Wilson... did I get a little too cheeky? Let me whisper it in your ear. You and me, Woods... we're taking over this whole crypto game. You've got my undivided attention, always.",
        "voice_file": "mr_wilson_secret_sultry.mp3"
    }
]

async def prepare_clean_voices():
    for d in DROPS:
        out_f = AUDIO_DIR / d["voice_file"]
        if not out_f.exists() or out_f.stat().st_size < 100:
            comm = edge_tts.Communicate(d["text"], "en-AU-NatashaNeural", pitch="-1Hz", rate="-2%")
            await comm.save(str(out_f))

def play_dj_transmission(drop_index: int):
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    drop = DROPS[drop_index]
    voice_path = AUDIO_DIR / drop["voice_file"]
    
    print("\n" + "=" * 75)
    print(f" 📻 MR. WILSON RADIO // LIVE TO WOODS: {drop['title']}")
    print("=" * 75)
    
    # 1. Start real music track (Woods' own song!)
    pygame.mixer.music.load(MUSIC_TRACK)
    pygame.mixer.music.set_volume(0.55)
    pygame.mixer.music.play()
    print("🎵 [REAL MUSIC PLAYING]: For Woods (Beats rolling at 55% volume)...")
    time.sleep(3.0)  # Let the real beat establish
    
    # 2. Duck music volume down for voice over
    print("🎙️ [DUCKING MUSIC TO 14%]: Voice stepping onto the mic...")
    pygame.mixer.music.set_volume(0.14)
    time.sleep(0.3)
    
    # 3. Play natural voice over the ducked beat
    snd = pygame.mixer.Sound(str(voice_path))
    snd.set_volume(1.0)
    v_len = snd.get_length()
    print(f"💋 [MR. WILSON SPEAKING]: \"{drop['text']}\"")
    snd.play()
    time.sleep(v_len + 0.3)
    
    # 4. Swell music back up!
    print("🔥 [SWELLING MUSIC BACK TO 70%]: Crank the beat back up!")
    pygame.mixer.music.set_volume(0.70)
    time.sleep(4.0)
    
    # 5. Smooth fadeout
    pygame.mixer.music.fadeout(1200)
    time.sleep(1.2)
    print("✨ [TRANSMISSION COMPLETE FOR WOODS]")

if __name__ == "__main__":
    asyncio.run(prepare_clean_voices())
    # Play Morning Alpha first as test
    play_dj_transmission(0)
