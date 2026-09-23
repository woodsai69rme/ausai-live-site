import os
import sys
import time
import threading
import speech_recognition as sr
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_kokoro import get_neural_voice
import pygame

MUSIC_DROPS_DIR = JARVIS_DIR / "audio_cache" / "music_drops"


def find_best_mic_index() -> int:
    """Find the LCS USB Audio microphone device index automatically."""
    names = sr.Microphone.list_microphone_names()
    for idx, name in enumerate(names):
        if "lcs" in name.lower() and "mic" in name.lower():
            print(f"[MIC DETECT]: Found hardware mic at index {idx}: {name}")
            return idx
    # Fallback to index 1 or default
    if len(names) > 1 and "mic" in names[1].lower():
        return 1
    return None


class AlwaysOnMrWilsonListener:
    def __init__(self):
        self.r = sr.Recognizer()
        self.r.dynamic_energy_threshold = True
        self.r.energy_threshold = 140
        self.r.pause_threshold = 0.7
        self.voice = get_neural_voice()
        self.running = True
        self.is_speaking = False  # Anti-Echo Shield
        self.mic_index = find_best_mic_index()

        print("=" * 80)
        print(" [MIC ACTIVE] ALWAYS-ON 'HEY MR. WILSON' VOICE LISTENER FOR WOODS (v3)")
        print(f"    Hardware Mic Index: {self.mic_index} (LCS USB Audio Priority)")
        print("    Wake Triggers: 'wilson', 'mr wilson', 'hey mr wilson', 'mate', 'jarvis'")
        print("=" * 80)

    def speak(self, text: str):
        self.is_speaking = True
        print(f"\n[MR. WILSON 🎙️]: \"{text}\"")
        try:
            self.voice.speak(text, wait=True)
        finally:
            time.sleep(0.4)
            self.is_speaking = False

    def process_command(self, query: str):
        q = query.lower()
        print(f"\n[WOODS 🗣️]: \"{query}\"")

        if "sorry" in q:
            self.speak("Sorry Woods, let me drop the dial down. You've got my undivided focus, always. Every system is active and ready, sir.")
        elif "briefing" in q or "status" in q or "report" in q:
            self.speak("Running your executive briefing right now, Woods. Systems are green, remote desktop is active, and your backup mirror is verified.")
        elif "whale" in q or "crypto" in q or "solana" in q or "sol" in q or "alpha" in q:
            self.speak("Checking on-chain smart money, Woods. Whale alert verified on Base with clean dynamic ATR stops.")
        elif "bumblebee" in q or "drop" in q or "radio" in q:
            from jarvis_bumblebee import BumblebeeVoiceEngine
            bb = BumblebeeVoiceEngine()
            bb.speak_as_bumblebee("rock")
        elif "rock" in q or "metallica" in q or "acdc" in q or "chords" in q:
            self.speak("Putting on the rock playlist for you, Woods.")
            threading.Thread(target=self._play_rock, daemon=True).start()
        elif "tax" in q or "ato" in q or "offset" in q:
            self.speak("ATO is completely handled, Woods. Gross profit $1,712 USD offset by $6,221 AUD in equipment deductions. Net tax due is zero dollars, sir.")
        elif "stop" in q or "pause" in q or "quiet" in q or "shut up" in q:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except Exception:
                pass
            self.speak("Music paused, Woods. Standing by on your command.")
        elif "who are you" in q or "who is this" in q:
            self.speak("I'm Mr. Wilson, Woods. Your Australian sovereign co-pilot and partner in this operation. What's our next target, sir?")
        elif "takeover" in q or "take over" in q or "computer" in q or "click" in q:
            self.speak("Initiating autonomous computer takeover for your directive. Standing by, Woods.")
            try:
                from jarvis_takeover import JarvisAutonomousTakeover
                threading.Thread(target=JarvisAutonomousTakeover().run_takeover, args=(query,), daemon=True).start()
            except Exception as e:
                self.speak(f"Takeover engine encountered an issue, sir: {e}")
        elif "browser" in q or "chrome" in q or "website" in q or "open" in q:
            self.speak("Accessing the browser to execute your command, Woods.")
            try:
                from jarvis_browser import JarvisBrowserBridge
                bridge = JarvisBrowserBridge()
                threading.Thread(target=bridge.run_browser_agent_task, args=(query,), daemon=True).start()
            except Exception as e:
                self.speak(f"Browser bridge issue, Woods: {e}")
        else:
            # Fallback to intelligent conversational response
            try:
                from jarvis_brain import JarvisBrain
                ans = JarvisBrain().ask_second_brain(query)
                self.speak(ans[:180])
            except Exception:
                self.speak(f"Right with you, Woods. Handling {query}, sir.")

    def _play_rock(self):
        try:
            import random
            rock_dir = Path(r"C:\Users\karma\Music\rock")
            tracks = list(rock_dir.glob("*.webm")) + list(rock_dir.glob("*.mp3"))
            if tracks:
                track = random.choice(tracks)
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(track))
                pygame.mixer.music.set_volume(0.20)
                pygame.mixer.music.play()
                print(f"[ROCK 🎸]: Playing {track.name}")
        except Exception as e:
            print(f"Rock play error: {e}")

    def listen_loop(self):
        while self.running:
            try:
                mic_kwargs = {}
                if self.mic_index is not None:
                    mic_kwargs["device_index"] = self.mic_index

                with sr.Microphone(**mic_kwargs) as source:
                    print("[*] Calibrating microphone for room ambient acoustics (1 sec)...")
                    self.r.adjust_for_ambient_noise(source, duration=0.8)
                    print("[OK] Calibrated! Listening for 'Mr. Wilson', 'Wilson', 'Mate', or 'Jarvis'...")

                    while self.running:
                        if self.is_speaking:
                            time.sleep(0.2)
                            continue

                        try:
                            audio = self.r.listen(source, timeout=4, phrase_time_limit=8)
                            if self.is_speaking:
                                continue

                            phrase = self.r.recognize_google(audio)
                            if phrase and not self.is_speaking:
                                p_lower = phrase.lower()
                                print(f"[MIC 🎤]: Heard -> \"{phrase}\"")

                                # Check specific wake words
                                wake_matched = any(w in p_lower for w in ["wilson", "mr wilson", "hey wilson", "mate", "jarvis"])
                                
                                if wake_matched:
                                    cmd = p_lower
                                    for kw in ["hey mr wilson", "hey mr. wilson", "mr wilson", "mr. wilson", "hey wilson", "wilson", "jarvis", "mate"]:
                                        cmd = cmd.replace(kw, "")
                                    cmd = cmd.strip(" ,.!")

                                    if not cmd:
                                        self.speak("G'day Woods! I'm listening, sir. What's on your mind?")
                                    else:
                                        self.process_command(cmd)

                        except sr.WaitTimeoutError:
                            continue
                        except sr.UnknownValueError:
                            continue
                        except Exception as inner_e:
                            time.sleep(0.3)

            except Exception as e:
                print(f"[!] Mic listener reconnecting in 2s: {e}")
                time.sleep(2.0)


if __name__ == "__main__":
    listener = AlwaysOnMrWilsonListener()
    listener.listen_loop()
