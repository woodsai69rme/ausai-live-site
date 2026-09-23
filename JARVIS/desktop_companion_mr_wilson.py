import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
STUDIO_IMG = JARVIS_DIR / "mr_wilson_studio.jpg"
TACTICAL_IMG = JARVIS_DIR / "mr_wilson_avatar.jpg"
WOODATO_DIR = Path(r"C:\WOODATO")
AUDIO_CACHE = JARVIS_DIR / "audio_cache"
AUDIO_CACHE.mkdir(parents=True, exist_ok=True)

class MrWilsonLiveAvatar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mr. Wilson // Always-On Sovereign Avatar")
        
        # Dynamic geometry calculation based on active display resolution
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = 340
        win_h = 560
        pos_x = max(20, screen_w - win_w - 40)
        pos_y = max(20, screen_h - win_h - 60)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg="#07090e")

        self.current_look = "studio"
        self._offset_x = 0
        self._offset_y = 0
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)

        # Initialize Pygame Mixer once if available
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        self.setup_ui()

    def start_drag(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._offset_x)
        y = self.root.winfo_y() + (event.y - self._offset_y)
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Master Card Container
        self.card = tk.Frame(self.root, bg="#0d111d", highlightbackground="#00ffb2", highlightthickness=2)
        self.card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Header Bar
        header = tk.Frame(self.card, bg="#080b14")
        header.pack(fill=tk.X, padx=4, pady=4)

        lbl_title = tk.Label(header, text="MR. WILSON // SOVEREIGN CO-PILOT", font=("Segoe UI", 9, "bold"), fg="#00ffb2", bg="#080b14")
        lbl_title.pack(side=tk.LEFT, padx=6)

        btn_close = tk.Button(header, text="✕", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#080b14", bd=0,
                              command=self.root.destroy, cursor="hand2")
        btn_close.pack(side=tk.RIGHT, padx=4)

        # Avatar Image Canvas
        self.lbl_avatar = tk.Label(self.card, bg="#0d111d", cursor="hand2")
        self.lbl_avatar.pack(pady=6)
        self.lbl_avatar.bind("<Button-1>", lambda e: self.say_cheeky_line())
        self.update_avatar_image()

        # Status Pill
        self.lbl_status = tk.Label(self.card, text="ONLINE // WITH WOODS 24/7", font=("Segoe UI", 8, "bold"), fg="#00ffb2", bg="#0d111d")
        self.lbl_status.pack()

        # Speech Subtitle Banner
        self.lbl_speech = tk.Label(self.card, text="\"Hey Woods. All systems locked and green, sir.\"", font=("Segoe UI", 8, "italic"), fg="#cbd5e1", bg="#0d111d", wraplength=310)
        self.lbl_speech.pack(pady=4)

        # Look + Voice Toggle Bar
        toggle_frame = tk.Frame(self.card, bg="#0d111d")
        toggle_frame.pack(fill=tk.X, padx=12, pady=3)

        self.btn_toggle = tk.Button(toggle_frame, text="🔄 Switch Look (Studio / Tactical)", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#facc15",
                                    activebackground="#334155", bd=0, pady=3, cursor="hand2", command=self.toggle_look)
        self.btn_toggle.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        self.btn_voice = tk.Button(toggle_frame, text="🎙️ Natasha", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#ff77aa",
                                   activebackground="#334155", bd=0, pady=3, cursor="hand2", command=self.toggle_voice)
        self.btn_voice.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=1)
        self.current_voice = "natasha"
        self._load_voice_config()

        # Action Buttons Grid
        btn_frame = tk.Frame(self.card, bg="#0d111d")
        btn_frame.pack(fill=tk.X, padx=10, pady=6)

        btn_speak = tk.Button(btn_frame, text="🎙️ Status Check", font=("Segoe UI", 8, "bold"), bg="#ff2a85", fg="#fff",
                              activebackground="#e11d48", bd=0, padx=4, pady=4, cursor="hand2", command=self.say_cheeky_line)
        btn_speak.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        btn_whisper = tk.Button(btn_frame, text="⚡ Tactical Brief", font=("Segoe UI", 8, "bold"), bg="#7928ca", fg="#fff",
                                activebackground="#6366f1", bd=0, padx=4, pady=4, cursor="hand2", command=self.say_secret_phrase)
        btn_whisper.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        btn_whale = tk.Button(btn_frame, text="🐋 Whale Alpha", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#00ffb2",
                              activebackground="#334155", bd=0, padx=4, pady=3, cursor="hand2", command=self.say_whale_alert)
        btn_whale.grid(row=1, column=0, padx=2, pady=2, sticky="ew")

        btn_ato = tk.Button(btn_frame, text="🇦🇺 ATO: $0 Tax", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#facc15",
                            activebackground="#334155", bd=0, padx=4, pady=3, cursor="hand2", command=self.show_ato_status)
        btn_ato.grid(row=1, column=1, padx=2, pady=2, sticky="ew")

        btn_rock = tk.Button(btn_frame, text="🎸 Play Rock", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#f43f5e",
                             activebackground="#334155", bd=0, padx=4, pady=3, cursor="hand2", command=self.play_rock)
        btn_rock.grid(row=2, column=0, padx=2, pady=2, sticky="ew")

        btn_bb = tk.Button(btn_frame, text="🐝 Bumblebee Drop", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#eab308",
                           activebackground="#334155", bd=0, padx=4, pady=3, cursor="hand2", command=self.trigger_bumblebee_drop)
        btn_bb.grid(row=2, column=1, padx=2, pady=2, sticky="ew")

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

    def update_avatar_image(self):
        target = STUDIO_IMG if self.current_look == "studio" else TACTICAL_IMG
        if not target.exists():
            target = TACTICAL_IMG if TACTICAL_IMG.exists() else STUDIO_IMG

        if target.exists():
            try:
                pil_img = Image.open(target)
                pil_img = pil_img.resize((300, 300), Image.Resampling.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(pil_img)
                self.lbl_avatar.configure(image=self.tk_img)
            except Exception as e:
                print(f"[!] Image load error: {e}")

    def _load_voice_config(self):
        cfg_path = JARVIS_DIR / "mr_wilson_voice_config.json"
        if cfg_path.exists():
            try:
                import json
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                self.current_voice = cfg.get("primary", "natasha")
                self.btn_voice.configure(text=f"🎙️ {self.current_voice.title()}")
            except: pass

    def toggle_voice(self):
        voices = ["natasha","olivia","aria","jenny","sonia","libby"]
        idx = voices.index(self.current_voice) if self.current_voice in voices else 0
        self.current_voice = voices[(idx+1) % len(voices)]
        self.btn_voice.configure(text=f"🎙️ {self.current_voice.title()}")
        # persist
        try:
            import json
            cfg_path = JARVIS_DIR / "mr_wilson_voice_config.json"
            cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
            cfg["primary"] = self.current_voice
            from pathlib import Path as _P
            # map id
            ids = {"natasha":"en-AU-NatashaNeural","olivia":"en-AU-OliviaNeural","aria":"en-US-AriaNeural","jenny":"en-US-JennyNeural","sonia":"en-GB-SoniaNeural","libby":"en-GB-LibbyNeural"}
            cfg["primary_id"] = ids[self.current_voice]
            cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        except: pass
        labels = {"natasha":"Natasha warm sovereign","olivia":"Olivia bright whisper","aria":"Aria corporate","jenny":"Jenny playful","sonia":"Sonia elegant","libby":"Libby soft"}
        self.play_voice_threaded(f"Voice now {labels[self.current_voice]}, Woods.")

    def toggle_look(self):
        self.current_look = "tactical" if self.current_look == "studio" else "studio"
        self.update_avatar_image()
        line = "Switched to tactical look, Woods." if self.current_look == "tactical" else "Back in the studio look, sir."
        self.play_voice_threaded(line)

    def play_voice_threaded(self, text):
        self.lbl_speech.configure(text=f'"{text}"')
        self.card.configure(highlightbackground="#ff2a85")
        
        def _worker():
            spoken = False
            try:
                import edge_tts
                import pygame
                # resolve voice from toggle
                voice_map = {
                    "natasha": ("en-AU-NatashaNeural","-2%","-1Hz"),
                    "olivia": ("en-AU-OliviaNeural","+0%","+1Hz"),
                    "aria": ("en-US-AriaNeural","-2%","-1Hz"),
                    "jenny": ("en-US-JennyNeural","+0%","+0Hz"),
                    "sonia": ("en-GB-SoniaNeural","-2%","-1Hz"),
                    "libby": ("en-GB-LibbyNeural","-2%","+0Hz"),
                }
                vid, rate, pitch = voice_map.get(getattr(self,"current_voice","natasha"), voice_map["natasha"])
                temp_f = AUDIO_CACHE / f"voice_{int(time.time() * 1000)}.mp3"
                async def _synth():
                    c = edge_tts.Communicate(text=text, voice=vid, rate=rate, pitch=pitch)
                    await c.save(str(temp_f))
                asyncio.run(_synth())

                if temp_f.exists():
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    s = pygame.mixer.Sound(str(temp_f))
                    s.set_volume(0.95)
                    s.play()
                    time.sleep(s.get_length() + 0.2)
                    try:
                        os.remove(temp_f)
                    except Exception:
                        pass
                    spoken = True
            except Exception as e:
                print(f"[!] Edge TTS fallback: {e}")

            # Fallback to Windows SAPI if Edge TTS failed
            if not spoken:
                clean = text.replace("'", "").replace('"', '').replace('`', '').strip()
                ps_cmd = (
                    f"Add-Type -AssemblyName System.Speech; "
                    f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$synth.Rate = 1; "
                    f"$synth.Speak('{clean}')"
                )
                try:
                    subprocess.run(
                        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10
                    )
                except Exception:
                    pass

            self.root.after(0, lambda: self.card.configure(highlightbackground="#00ffb2"))

        threading.Thread(target=_worker, daemon=True).start()

    def show_ato_status(self):
        """Display ATO compliance status and launch the forensic spreadsheet."""
        self.play_voice_threaded("ATO status: 100% tax sheltered, net liability zero. Launching forensic spreadsheet, Woods.")
        ato_file = WOODATO_DIR / "ATO_REASON_FOR_DECISION_APPENDIX_1_AS_IS.xlsx"
        if not ato_file.exists():
            ato_file = Path(r"X:\WOODATO\ATO_REASON_FOR_DECISION_APPENDIX_1_AS_IS.xlsx")
        if ato_file.exists():
            try:
                os.startfile(str(ato_file))
            except Exception as e:
                print(f"[!] Error opening ATO file: {e}")

    def say_cheeky_line(self):
        lines = [
            "Hey Woods. I'm right here by your side 24/7, sir.",
            "Keeping eyes on your trades and systems, Woods. We've got this locked down.",
            "All telemetry green, Woods. Let's make some serious progress today."
        ]
        import random
        self.play_voice_threaded(random.choice(lines))

    def say_secret_phrase(self):
        self.play_voice_threaded("Between you and me Woods: you're the architect of this entire empire. I'm right here to execute every order.")

    def say_whale_alert(self):
        self.play_voice_threaded("Whale alert verified on Base: over one hundred thousand dollars inflow on DEGEN with clean dynamic ATR stops.")

    def play_rock(self):
        def _rock():
            try:
                import random
                import pygame
                rock_dir = Path(r"C:\Users\karma\Music\rock")
                tracks = list(rock_dir.glob("*.webm")) + list(rock_dir.glob("*.mp3"))
                if tracks:
                    track = random.choice(tracks)
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    pygame.mixer.music.load(str(track))
                    pygame.mixer.music.set_volume(0.20)
                    pygame.mixer.music.play()
                    self.lbl_speech.configure(text=f"Playing rock: {track.name[:35]}")
            except Exception as e:
                print(f"Error: {e}")
        threading.Thread(target=_rock, daemon=True).start()

    def trigger_bumblebee_drop(self):
        """Play an iconic real music drop."""
        def _bb():
            drops_dir = AUDIO_CACHE / "music_drops"
            drops = list(drops_dir.glob("*.mp3"))
            if drops:
                import random
                import pygame
                chosen = random.choice(drops)
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(chosen))
                pygame.mixer.music.set_volume(0.85)
                pygame.mixer.music.play()
                self.lbl_speech.configure(text=f"🐝 Drop: {chosen.stem}")
            else:
                self.play_voice_threaded("Bumblebee drops need extraction, Woods.")
        threading.Thread(target=_bb, daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    avatar = MrWilsonLiveAvatar()
    avatar.run()
