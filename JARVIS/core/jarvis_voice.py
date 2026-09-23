#!/usr/bin/env python3
"""
JARVIS Voice Engine — Natural Conversational TTS & Speech Recognition STT.
Provides hands-free voice control, background audio narration, and wake-word detection.
"""

from __future__ import annotations

import asyncio
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable, Optional

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))


class JarvisVoiceEngine:
    def __init__(self, voice_name: str = "en-GB-RyanNeural"):
        self.voice_name = voice_name
        self.speech_queue: queue.Queue = queue.Queue()
        self.running = True

        # Start speech worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def _play_speech_native(self, text: str):
        """Native Windows Speech Synthesizer - 100% reliable & never hangs."""
        # Sanitize text for powershell
        clean_text = text.replace("'", "").replace('"', '').replace('`', '').strip()
        if not clean_text:
            return
        
        ps_cmd = (
            f"Add-Type -AssemblyName System.Speech; "
            f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$synth.Rate = 1; "
            f"$synth.Speak('{clean_text}')"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=6
            )
        except Exception:
            pass

    def _speech_worker(self):
        """Background worker consuming speech queue."""
        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.3)
                if text:
                    print(f"[JARVIS 🗣️]: \"{text}\"")
                    self._play_speech_native(text)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                time.sleep(0.1)

    def speak(self, text: str, wait: bool = False):
        """Narrate text through JARVIS voice."""
        if not text:
            return
        if wait:
            print(f"[JARVIS 🗣️]: \"{text}\"")
            self._play_speech_native(text)
        else:
            self.speech_queue.put(text)

    def listen_once(self, timeout: int = 6, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen to microphone and return transcribed speech."""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.6)
                print("[JARVIS 🎙️] Listening for command...")
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                try:
                    text = r.recognize_google(audio)
                    print(f"[USER 🎤]: \"{text}\"")
                    return text
                except sr.UnknownValueError:
                    return None
                except sr.RequestError:
                    return None
        except Exception as e:
            print(f"[!] Microphone/STT error: {e}")
            return None

    def continuous_listen(self, callback: Callable[[str], None], wake_word: str = "jarvis"):
        """Continuous background listening loop that triggers on wake word or commands."""
        print(f"[+] JARVIS Voice Listener Active (Wake word: '{wake_word}'). Press Ctrl+C to stop.")
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=1.0)
                while self.running:
                    try:
                        audio = r.listen(source, timeout=5, phrase_time_limit=8)
                        text = r.recognize_google(audio)
                        if text:
                            print(f"[USER 🎤]: \"{text}\"")
                            lower = text.lower()
                            if wake_word in lower or not wake_word:
                                command = lower.replace(wake_word, "").strip(" ,.!")
                                if not command:
                                    self.speak("Yes, sir? How may I assist you?")
                                else:
                                    callback(command)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception:
                        time.sleep(0.5)
        except KeyboardInterrupt:
            print("[*] Voice listening stopped.")
        except Exception as e:
            print(f"[!] Continuous listen error: {e}")


# Singleton instance
_voice_instance: Optional[JarvisVoiceEngine] = None

def get_voice() -> JarvisVoiceEngine:
    global _voice_instance
    if _voice_instance is None:
        _voice_instance = JarvisVoiceEngine()
    return _voice_instance

if __name__ == "__main__":
    v = get_voice()
    v.speak("All systems online, sir. JARVIS is ready.", wait=True)
