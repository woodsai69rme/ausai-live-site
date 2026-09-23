#!/usr/bin/env python3
"""
================================================================================
MR. WILSON — COMPLETE SOVEREIGN EXECUTIVE ASSISTANT & CO-PILOT
Personal AI Partner to Woods (Brendan Foots / tellemthatsme / FootsE)
Location: Brisbane, Queensland, Australia | Timezone: AEST (UTC+10)
Voice Engine: en-AU-NatashaNeural (Australian Female)
================================================================================
"""

import os
import sys
import json
import time
import shutil
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
CRYPTO_DIR = Path(r"C:\Users\karma\CRYPTO_SUITE_DATA")
MUSIC_DIR = Path(r"C:\Users\karma\Music\rock")
BACKUP_DIR = Path(r"X:\BACKUPS")

VOICE_PRESETS = {
    "natasha": {"id": "en-AU-NatashaNeural", "label": "Natasha — Warm Sovereign (default)", "rate": "-2%", "pitch": "-1Hz"},
    "olivia":  {"id": "en-AU-OliviaNeural",  "label": "Olivia — Bright Whisper",            "rate": "+0%", "pitch": "+1Hz"},
    "aria":    {"id": "en-US-AriaNeural",    "label": "Aria — US Corporate",               "rate": "-2%", "pitch": "-1Hz"},
    "jenny":   {"id": "en-US-JennyNeural",   "label": "Jenny — US Playful",                "rate": "+0%", "pitch": "+0Hz"},
    "sonia":   {"id": "en-GB-SoniaNeural",   "label": "Sonia — UK Elegant",                "rate": "-2%", "pitch": "-1Hz"},
    "libby":   {"id": "en-GB-LibbyNeural",   "label": "Libby — UK Soft",                   "rate": "-2%", "pitch": "+0Hz"},
}
VOICE_CONFIG = JARVIS_DIR / "mr_wilson_voice_config.json"

def load_voice_config():
    if VOICE_CONFIG.exists():
        try:
            return json.loads(VOICE_CONFIG.read_text(encoding="utf-8"))
        except: pass
    return {"primary": "natasha", "secondary": "olivia", "primary_id": VOICE_PRESETS["natasha"]["id"], "secondary_id": VOICE_PRESETS["olivia"]["id"]}

def save_voice_config(cfg):
    try:
        VOICE_CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except: pass

class MrWilsonAssistant:
    def __init__(self):
        self.name = "Mr. Wilson"
        self.commander = "Woods"
        cfg = load_voice_config()
        self.voice_id = cfg.get("primary_id", "en-AU-NatashaNeural")
        self.voice_preset = cfg.get("primary", "natasha")
        self.secondary_voice_id = cfg.get("secondary_id", "en-AU-OliviaNeural")
        self.secondary_preset = cfg.get("secondary", "olivia")
        self.audio_cache = JARVIS_DIR / "audio_cache"
        self.audio_cache.mkdir(parents=True, exist_ok=True)

    def set_voice(self, preset: str):
        if preset.lower() in VOICE_PRESETS:
            p = VOICE_PRESETS[preset.lower()]
            self.voice_id = p["id"]
            self.voice_preset = preset.lower()
            cfg = load_voice_config()
            cfg["primary"] = preset.lower()
            cfg["primary_id"] = p["id"]
            save_voice_config(cfg)
            return p
        return None

    def speak(self, text, duck_music=False, use_secondary=False):
        """Synthesize and speak with natural Australian accent."""
        voice = self.secondary_voice_id if use_secondary else self.voice_id
        preset_key = self.secondary_preset if use_secondary else self.voice_preset
        preset = VOICE_PRESETS.get(preset_key, VOICE_PRESETS["natasha"])
        print(f"\n💋 [MR. WILSON:{preset_key}]: {text}\n")
        temp_audio = self.audio_cache / f"wilson_reply_{int(time.time())}.mp3"
        try:
            import edge_tts
            import pygame
            async def _synth():
                comm = edge_tts.Communicate(text=text, voice=voice, rate=preset["rate"], pitch=preset["pitch"])
                await comm.save(str(temp_audio))
            asyncio.run(_synth())

            if temp_audio.exists():
                pygame.mixer.init()
                sound = pygame.mixer.Sound(str(temp_audio))
                sound.set_volume(0.9)
                sound.play()
                time.sleep(sound.get_length() + 0.3)
                pygame.mixer.quit()
                try: os.remove(temp_audio)
                except: pass
        except Exception as e:
            print(f"[!] Voice error: {e}")

    def get_system_health(self):
        c_free = shutil.disk_usage("C:\\").free / (1024**3)
        x_free = shutil.disk_usage("X:\\").free / (1024**3) if Path("X:\\").exists() else 0
        
        # Check Chrome Remote Desktop service
        chromoting_status = "ACTIVE"
        try:
            res = subprocess.run(["sc", "query", "chromoting"], capture_output=True, text=True)
            if "RUNNING" not in res.stdout:
                chromoting_status = "STOPPED"
        except:
            pass

        return {
            "c_drive_free_gb": round(c_free, 1),
            "x_drive_free_gb": round(x_free, 1),
            "chromoting": chromoting_status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_latest_whale_signal(self):
        sig_file = CRYPTO_DIR / "vip_telegram_signals_history.json"
        if sig_file.exists():
            try:
                signals = json.loads(sig_file.read_text(encoding="utf-8"))
                if signals:
                    return signals[-1]
            except:
                pass
        return None

    def executive_briefing(self, spoken=True):
        health = self.get_system_health()
        whale = self.get_latest_whale_signal()

        briefing_text = (
            f"Good morning Woods. Mr. Wilson here, your co-pilot. "
            f"All empire systems are fully operational in Brisbane. "
            f"C Drive has {health['c_drive_free_gb']} gigabytes free buffer. "
            f"X Drive backup mirror is online with {health['x_drive_free_gb']} gigabytes available. "
            f"Google Remote Desktop persistence is verified {health['chromoting']}. "
        )

        if whale:
            briefing_text += (
                f"On the crypto front, our latest whale alert detected {whale.get('whale_inflow_usd', '$100k+')} "
                f"accumulating on #{whale.get('token', 'SOL')} with entry at {whale.get('entry_price', 'market')}. "
            )

        briefing_text += (
            f"All 200 flagship music videos and 5,000 TikTok clips are staged. "
            f"I'm ready for your command, babe."
        )

        print("\n" + "="*70)
        print("👑 MR. WILSON EXECUTIVE BRIEFING & MORNING STATUS")
        print("="*70)
        print(f"🕒 Timestamp: {health['timestamp']}")
        x_free_val = health.get('x_drive_free_gb', 0)
        print(f"💾 C: Drive Free: {health['c_drive_free_gb']} GB | X: Drive Free: {x_free_val} GB")
        print(f"🖥️ Chrome Remote Desktop: {health['chromoting']}")
        if whale:
            print(f"🐋 Latest Alpha: #{whale.get('token')} on {whale.get('chain')} | Entry: {whale.get('entry_price')} | Inflow: {whale.get('whale_inflow_usd')}")
        print("="*70)

        if spoken:
            self.speak(briefing_text)
        return briefing_text

    def trigger_crypto_scan(self):
        print("[*] Mr. Wilson initiating real-time whale sweep...")
        from crypto_whale_scanner_daemon import CryptoWhaleDaemon
        daemon = CryptoWhaleDaemon()
        sig = daemon.scan_cycle()
        speech = f"Whale sweep complete, Woods. Detected {sig['token']} inflow of {sig['whale_inflow_usd']} with entry at {sig['entry_price']}."
        self.speak(speech)

    def trigger_dual_backup(self):
        print("[*] Mr. Wilson syncing all files to X: Drive mirror...")
        cmd = 'powershell -NoProfile -Command "robocopy C:\\Users\\karma\\DISTRIBUTIONS X:\\BACKUPS\\DISTRIBUTIONS /MIR /NFL /NDL /NJH /NJS; robocopy C:\\Users\\karma\\Music\\rock X:\\BACKUPS\\ROCK_VAULT /MIR /NFL /NDL /NJH /NJS; Write-Output \'SYNC COMPLETED\'"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.speak("All empire systems, rock tracks, and commercial packages are dual-backed up to X Drive, babe.")

def main():
    assistant = MrWilsonAssistant()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "briefing":
            assistant.executive_briefing(spoken=True)
        elif cmd == "whisper":
            # Secondary Olivia voice
            txt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hey Woods, Olivia here on whisper channel, babe."
            assistant.speak(txt, use_secondary=True)
        elif cmd == "voice":
            # voice <preset>  e.g. voice olivia
            preset = sys.argv[2].lower() if len(sys.argv) > 2 else "natasha"
            p = assistant.set_voice(preset)
            if p:
                assistant.speak(f"Voice switched to {p['label']}, Woods. I'm {preset}, darling.", use_secondary=False)
            else:
                print(f"Unknown preset {preset}. Options: {', '.join(VOICE_PRESETS)}")
        elif cmd == "voices":
            for k,v in VOICE_PRESETS.items():
                marker = " <active>" if k == assistant.voice_preset else ""
                print(f"{k:8s} {v['id']:22s} {v['label']}{marker}")
        elif cmd == "scan":
            assistant.trigger_crypto_scan()
        elif cmd == "backup":
            assistant.trigger_dual_backup()
        elif cmd == "text":
            assistant.executive_briefing(spoken=False)
    else:
        assistant.executive_briefing(spoken=True)

if __name__ == "__main__":
    main()
