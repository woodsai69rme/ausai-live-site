#!/usr/bin/env python3
"""
JARVIS Kokoro-82M & High-Speed Neural Speech Engine.
Provides sub-100ms lightweight neural text-to-speech with local audio caching and
seamless fallback across Kokoro ONNX, Edge-TTS, and Native Windows Speech Synthesis.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Optional

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
AUDIO_CACHE_DIR = JARVIS_DIR / "audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class JarvisKokoroEngine:
    def __init__(self, voice: str = "af_sarah", fallback_voice: str = "en-AU-NatashaNeural"):
        self.voice = voice
        self.fallback_voice = fallback_voice
        self.kokoro_available = False
        self._check_kokoro_service()

    def _check_kokoro_service(self):
        """Check if local Kokoro FastAPI / Docker service is running on port 8880."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8880/v1/models", headers={"User-Agent": "JARVIS"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    self.kokoro_available = True
        except Exception:
            self.kokoro_available = False

    def _get_cache_path(self, text: str) -> Path:
        hash_id = hashlib.md5(f"{self.voice}_{text}".encode("utf-8")).hexdigest()
        return AUDIO_CACHE_DIR / f"speech_{hash_id}.mp3"

    def synthesize(self, text: str) -> Optional[Path]:
        """Synthesize high-fidelity voice audio to file."""
        clean_text = text.strip()
        if not clean_text:
            return None

        cache_path = self._get_cache_path(clean_text)
        if cache_path.exists() and cache_path.stat().st_size > 100:
            return cache_path

        # 1. Try local Kokoro API if running
        if self.kokoro_available:
            try:
                url = "http://127.0.0.1:8880/v1/audio/speech"
                payload = json.dumps({
                    "model": "kokoro",
                    "input": clean_text,
                    "voice": self.voice,
                    "response_format": "mp3",
                    "speed": 1.05
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    cache_path.write_bytes(resp.read())
                    return cache_path
            except Exception:
                pass

        # 2. Try Edge-TTS (Sexy Australian Female: en-AU-NatashaNeural)
        try:
            import edge_tts
            communicate = edge_tts.Communicate(clean_text, self.fallback_voice, pitch="-2Hz", rate="-2%")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(communicate.save(str(cache_path)))
            loop.close()

            if cache_path.exists() and cache_path.stat().st_size > 100:
                return cache_path
        except Exception:
            pass

        return None

    def play_audio(self, audio_path: Path):
        """Play audio file with pygame mixer.Sound (exact duration) or Windows media fallback."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            snd = pygame.mixer.Sound(str(audio_path))
            snd.play()
            time.sleep(snd.get_length() + 0.3)
            return
        except Exception as e:
            pass

        ps_cmd = f"""
        try {{
            $player = New-Object -ComObject wmplayer.ocx
            $player.URL = '{audio_path}'
            $player.controls.play()
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            while ($sw.ElapsedMilliseconds -lt 8000 -and $player.playState -ne 1 -and $player.playState -ne 8) {{
                Start-Sleep -Milliseconds 100
            }}
            $player.close()
        }} catch {{}}
        """
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
        except Exception:
            pass

    def speak(self, text: str, wait: bool = False):
        """Speak text with neural audio or native SAPI fallback."""
        print(f"[JARVIS Neural 🎙️]: \"{text}\"")
        audio_file = self.synthesize(text)
        if audio_file:
            if wait:
                self.play_audio(audio_file)
            else:
                threading.Thread(target=self.play_audio, args=(audio_file,), daemon=True).start()
        else:
            # Native SAPI fallback
            clean_sapi = text.replace("'", "").replace('"', '').strip()
            ps_fallback = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 1; $s.Speak('{clean_sapi}')"
            try:
                if wait:
                    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_fallback], timeout=6)
                else:
                    subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_fallback])
            except Exception:
                pass


_kokoro_instance: Optional[JarvisKokoroEngine] = None

def get_neural_voice() -> JarvisKokoroEngine:
    global _kokoro_instance
    if _kokoro_instance is None:
        _kokoro_instance = JarvisKokoroEngine()
    return _kokoro_instance


if __name__ == "__main__":
    v = get_neural_voice()
    v.speak("Kokoro Neural Speech Engine initialized for JARVIS.", wait=True)
