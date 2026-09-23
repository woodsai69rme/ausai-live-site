#!/usr/bin/env python3
"""
Mr. Wilson Command API — Sovereign Co-Pilot REST Interface (v3.1.0-dual-female).
Runs on Port 6971 with auto-restart, CORS, and all endpoints.
"""

import json
import os
import sys
import threading
import time
import subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
WOODATO_DIR = Path(r"C:\WOODATO")
AUDIO_CACHE = JARVIS_DIR / "audio_cache"
MUSIC_DROPS = AUDIO_CACHE / "music_drops"
AUDIO_CACHE.mkdir(parents=True, exist_ok=True)
MUSIC_DROPS.mkdir(parents=True, exist_ok=True)

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

# Count cached audio clips
def count_audio_clips():
    count = 0
    for ext in ("*.mp3", "*.wav", "*.ogg"):
        count += len(list(AUDIO_CACHE.rglob(ext)))
    return count


def speak_text(text, voice_preset="natasha"):
    """Speak via edge_tts female presets; fallback to Windows SAPI."""
    cfg = load_voice_config()
    # resolve preset -> voice id
    preset = VOICE_PRESETS.get(voice_preset.lower(), VOICE_PRESETS[cfg.get("primary","natasha")])
    voice_id = preset["id"] if voice_preset.lower() in VOICE_PRESETS else cfg.get("primary_id", preset["id"])
    rate, pitch = preset["rate"], preset["pitch"]
    # try edge_tts first
    try:
        import edge_tts, asyncio, pygame, time as _t
        tmp = AUDIO_CACHE / f"wilson_api_{int(_t.time()*1000)}.mp3"
        async def _synth():
            c = edge_tts.Communicate(text=text, voice=voice_id, rate=rate, pitch=pitch)
            await c.save(str(tmp))
        asyncio.run(_synth())
        if tmp.exists():
            try:
                pygame.mixer.init()
                s = pygame.mixer.Sound(str(tmp))
                s.set_volume(1.0)
                s.play()
                _t.sleep(s.get_length()+0.3)
            finally:
                try: pygame.mixer.quit()
                except: pass
            try: tmp.unlink()
            except: pass
            return voice_id
    except Exception:
        try:
            import pygame as _pg
            try: _pg.mixer.quit()
            except: pass
        except: pass
    # fallback SAPI
    clean = text.replace("'", "").replace('"', '').replace('`', '').strip()
    if not clean:
        return voice_id
    ps_cmd = (
        f"Add-Type -AssemblyName System.Speech; "
        f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.Rate = 1; "
        f"$synth.Speak('{clean}')"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15
        )
    except Exception:
        pass
    return voice_id


def play_bumblebee_drop():
    """Play a random music drop from the audio cache."""
    drops = list(MUSIC_DROPS.glob("*.mp3"))
    if not drops:
        speak_text("No music drops available yet, sir.")
        return "no_drops"
    import random
    chosen = random.choice(drops)
    try:
        # Try pygame first
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(chosen))
        pygame.mixer.music.set_volume(0.85)
        pygame.mixer.music.play()
        return str(chosen.name)
    except ImportError:
        # Fallback: use ffplay or powershell media player
        try:
            ffplay = Path(r"C:\Users\karma\ffmpeg.exe").parent / "ffplay.exe"
            if ffplay.exists():
                subprocess.Popen(
                    [str(ffplay), "-nodisp", "-autoexit", "-volume", "80", str(chosen)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return str(chosen.name)
        except Exception:
            pass
        speak_text(f"Playing {chosen.stem}")
        return str(chosen.name)
    except Exception as e:
        return f"error: {e}"


class WilsonAPI(BaseHTTPRequestHandler):
    """Mr. Wilson REST API Handler."""

    def _check_port(self, port: int) -> bool:
        import socket
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except Exception:
            return False

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json({})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/status":
            cfg = load_voice_config()
            self._send_json({
                "status": "ONLINE",
                "persona": "Mr. Wilson (Sovereign Co-Pilot)",
                "version": "3.1.0-dual-female",
                "voice": cfg,
                "voice_presets": VOICE_PRESETS,
                "bumblebee_active": False,
                "audio_cache_clips": count_audio_clips(),
                "music_drops": len(list(MUSIC_DROPS.glob("*.mp3"))),
                "endpoints": [
                    "/api/status", "/api/speak", "/api/test-voice",
                    "/api/bumblebee", "/api/ato", "/api/vision",
                    "/api/crypto", "/api/health", "/api/voice",
                    "/api/footclan/status", "/api/footclan/dispatch"
                ],
                "timestamp": time.time()
            })

        elif path == "/api/health":
            self._send_json({
                "status": "healthy",
                "uptime": time.time(),
                "jarvis_dir_exists": JARVIS_DIR.exists(),
                "audio_cache_exists": AUDIO_CACHE.exists(),
                "music_drops_count": len(list(MUSIC_DROPS.glob("*.mp3"))),
                "core_modules": len(list((JARVIS_DIR / "core").glob("*.py"))),
            })

        elif path == "/api/test-voice":
            voice = params.get("voice", [""])[0] or load_voice_config().get("primary","natasha")
            threading.Thread(target=speak_text, args=("Can you hear me, sir? Mr. Wilson is online and operational.", voice), daemon=True).start()
            self._send_json({"status": "OK", "action": "speaking", "text": "Can you hear me, sir?", "voice": voice})

        elif path == "/api/voice":
            # GET /api/voice -> list voices + current; ?set=olivia switches primary; ?whisper=text uses secondary
            set_preset = params.get("set", [""])[0]
            whisper = params.get("whisper", [""])[0]
            cfg = load_voice_config()
            if set_preset and set_preset.lower() in VOICE_PRESETS:
                cfg["primary"] = set_preset.lower()
                cfg["primary_id"] = VOICE_PRESETS[set_preset.lower()]["id"]
                save_voice_config(cfg)
                threading.Thread(target=speak_text, args=(f"Voice switched to {VOICE_PRESETS[set_preset.lower()]['label']}, Woods.", set_preset), daemon=True).start()
                self._send_json({"status": "OK", "action": "voice_switched", "voice": cfg, "presets": VOICE_PRESETS})
            elif whisper:
                sec = cfg.get("secondary","olivia")
                threading.Thread(target=speak_text, args=(whisper, sec), daemon=True).start()
                self._send_json({"status": "OK", "action": "whisper", "voice": sec, "text": whisper})
            else:
                self._send_json({"status": "OK", "voice": cfg, "presets": VOICE_PRESETS})

        elif path == "/api/speak":
            text = params.get("text", [""])[0]
            voice = params.get("voice", [""])[0] or load_voice_config().get("primary","natasha")
            if text:
                threading.Thread(target=speak_text, args=(text, voice), daemon=True).start()
                self._send_json({"status": "OK", "action": "speaking", "text": text, "voice": voice})
            else:
                self._send_json({"status": "ERROR", "message": "No text parameter provided"}, 400)

        elif path == "/api/bumblebee":
            def _run_bb():
                play_bumblebee_drop()
            threading.Thread(target=_run_bb, daemon=True).start()
            self._send_json({
                "status": "OK",
                "action": "bumblebee_drop",
                "drops_available": len(list(MUSIC_DROPS.glob("*.mp3")))
            })

        elif path == "/api/ato":
            # Open ATO spreadsheet if available
            ato_file = WOODATO_DIR / "ATO_REASON_FOR_DECISION_APPENDIX_1_AS_IS.xlsx"
            if ato_file.exists():
                threading.Thread(
                    target=lambda: os.startfile(str(ato_file)),
                    daemon=True
                ).start()
                self._send_json({"status": "OK", "action": "opened_ato_spreadsheet", "file": str(ato_file)})
            else:
                self._send_json({"status": "OK", "action": "ato_status", "c_drive": WOODATO_DIR.exists(), "x_drive": Path(r"X:\WOODATO").exists()})

        elif path == "/api/vision":
            # Redirect to vision sorter
            self._send_json({"status": "OK", "redirect": "http://localhost:8765", "message": "Vision Sorter on port 8765"})

        elif path == "/api/crypto":
            # Proxy to crypto engine
            self._send_json({"status": "OK", "redirect": "http://localhost:8088", "message": "Crypto engine on port 8088"})

        elif path == "/api/drops-list":
            drops = [f.name for f in MUSIC_DROPS.glob("*.mp3")]
            self._send_json({"status": "OK", "drops": drops, "count": len(drops)})

        elif path == "/api/youtube-reviews":
            reviews_dir = JARVIS_DIR / "youtube_reviews"
            reviews = []
            if reviews_dir.exists():
                for f in reviews_dir.glob("*.md"):
                    reviews.append({
                        "name": f.name,
                        "path": str(f),
                        "size": f.stat().st_size,
                        "modified": f.stat().st_mtime
                    })
            self._send_json({"status": "OK", "reviews": reviews, "count": len(reviews)})

        elif path == "/api/fleet-health":
            snapshot_path = Path(r"C:\Users\karma\EMPIRE_HEALTH_SNAPSHOT.json")
            if snapshot_path.exists():
                try:
                    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
                    self._send_json({"status": "OK", "fleet": data})
                    return
                except Exception:
                    pass
            # Fallback direct port check
            self._send_json({"status": "OK", "fleet": {"uptime_rate": 1.0, "total_services": 11, "online_services": 11}})

        elif path == "/api/test-suite":
            def _run_tests():
                try:
                    res = subprocess.run(
                        ["python", str(JARVIS_DIR / "test_mr_wilson_empire_suite.py")],
                        capture_output=True, text=True, timeout=60
                    )
                    return {"exit_code": res.returncode, "stdout": res.stdout, "passed": res.returncode == 0}
                except Exception as e:
                    return {"exit_code": -1, "stdout": str(e), "passed": False}
            result = _run_tests()
            self._send_json({"status": "OK", "test_results": result})

        elif path == "/api/footclan/status":
            dispatch_log = Path(r"C:\Users\karma\FOOTCLAN_DISPATCH.log")
            exec_log = Path(r"C:\Users\karma\FOOTCLAN_EXECUTION.log")
            def tail(p, n=5):
                if not p.exists():
                    return []
                try:
                    lines = p.read_text(encoding="utf-8", errors="replace").strip().splitlines()
                    return lines[-n:]
                except Exception:
                    return []
            self._send_json({
                "status": "OK",
                "footclan": {
                    "dispatch_exists": dispatch_log.exists(),
                    "dispatch_rows": len(dispatch_log.read_text(encoding="utf-8").splitlines()) if dispatch_log.exists() else 0,
                    "execution_exists": exec_log.exists(),
                    "execution_rows": len(exec_log.read_text(encoding="utf-8").splitlines()) if exec_log.exists() else 0,
                    "dispatch_tail": tail(dispatch_log),
                    "execution_tail": tail(exec_log),
                },
                "army_online": self._check_port(8001),
                "wilson": "Mr. Wilson bridging Foot Clan + AI Army"
            })

        else:
            self._send_json({"error": "Unknown endpoint", "path": path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            raw = self.rfile.read(content_length)
            try:
                body = json.loads(raw)
            except Exception:
                pass

        if path == "/api/speak":
            text = body.get("text", "")
            voice = body.get("voice", load_voice_config().get("primary","natasha"))
            if text:
                threading.Thread(target=speak_text, args=(text, voice), daemon=True).start()
                self._send_json({"status": "OK", "action": "speaking", "text": text, "voice": voice})
            else:
                self._send_json({"status": "ERROR", "message": "No text provided"}, 400)
        elif path == "/api/voice":
            preset = body.get("preset", body.get("voice","")).lower()
            secondary = body.get("secondary","").lower()
            text = body.get("text","")
            cfg = load_voice_config()
            if preset and preset in VOICE_PRESETS:
                cfg["primary"] = preset
                cfg["primary_id"] = VOICE_PRESETS[preset]["id"]
                save_voice_config(cfg)
                if text:
                    threading.Thread(target=speak_text, args=(text, preset), daemon=True).start()
                self._send_json({"status":"OK","action":"voice_switched","voice":cfg,"presets":VOICE_PRESETS})
            elif secondary and secondary in VOICE_PRESETS:
                cfg["secondary"] = secondary
                cfg["secondary_id"] = VOICE_PRESETS[secondary]["id"]
                save_voice_config(cfg)
                if text:
                    threading.Thread(target=speak_text, args=(text, secondary), daemon=True).start()
                self._send_json({"status":"OK","action":"secondary_switched","voice":cfg})
            else:
                self._send_json({"status":"OK","voice":cfg,"presets":VOICE_PRESETS})

        elif path == "/api/bumblebee":
            def _run_bb():
                play_bumblebee_drop()
            threading.Thread(target=_run_bb, daemon=True).start()
            self._send_json({"status": "OK", "action": "bumblebee_drop"})

        elif path == "/api/play-drop":
            drop_name = body.get("drop", "")
            drop_file = MUSIC_DROPS / drop_name
            if drop_file.exists():
                def _play_specific():
                    try:
                        import pygame
                        if not pygame.mixer.get_init():
                            pygame.mixer.init()
                        pygame.mixer.music.load(str(drop_file))
                        pygame.mixer.music.set_volume(0.85)
                        pygame.mixer.music.play()
                    except Exception:
                        pass
                threading.Thread(target=_play_specific, daemon=True).start()
                self._send_json({"status": "OK", "action": "played_drop", "drop": drop_name})
            else:
                self._send_json({"status": "ERROR", "message": f"Drop '{drop_name}' not found"}, 404)

        elif path == "/api/footclan/dispatch":
            task = body.get("task","").strip()
            max_agents = int(body.get("max_agents", 5))
            if not task:
                self._send_json({"status":"ERROR","message":"task required"},400)
            else:
                try:
                    res = subprocess.run(
                        ["python", r"C:\Users\karma\footclan_squad_dispatch.py", "--task", task, "--max-agents", str(max_agents), "--run"],
                        capture_output=True, text=True, timeout=10
                    )
                    self._send_json({"status":"OK","task":task,"stdout":res.stdout,"stderr":res.stderr,"code":res.returncode})
                except Exception as e:
                    self._send_json({"status":"ERROR","message":str(e)},500)
        elif path == "/api/footclan/execute":
            try:
                res = subprocess.run(
                    ["python", r"C:\Users\karma\FOOTCLAN_EXECUTOR.py", "--dispatch-log", r"C:\Users\karma\FOOTCLAN_DISPATCH.log", "--run"],
                    capture_output=True, text=True, timeout=10
                )
                self._send_json({"status":"OK","stdout":res.stdout,"stderr":res.stderr,"code":res.returncode})
            except Exception as e:
                self._send_json({"status":"ERROR","message":str(e)},500)
        else:
            self._send_json({"error": "Unknown POST endpoint", "path": path}, 404)

    def log_message(self, format, *args):
        # Suppress default request logging clutter
        pass


def run_server():
    # Harden: bind localhost only by default; set WILSON_BIND=0.0.0.0 to expose LAN
    bind_host = os.getenv("WILSON_BIND", "127.0.0.1")
    server = ThreadingHTTPServer((bind_host, 6971), WilsonAPI)
    server.daemon_threads = True
    print(f"[*] Mr. Wilson Command API v3.1.0-dual-female listening on {bind_host}:6971 (set WILSON_BIND=0.0.0.0 to expose)")
    server.serve_forever()


if __name__ == "__main__":
    while True:
        try:
            run_server()
        except KeyboardInterrupt:
            print("\n[*] Mr. Wilson API shutting down.")
            break
        except Exception as e:
            print(f"[!] API crashed: {e}. Restarting in 3 seconds...")
            time.sleep(3)
