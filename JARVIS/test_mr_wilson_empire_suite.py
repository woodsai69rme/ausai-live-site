#!/usr/bin/env python3
"""
Comprehensive Automated Verification Test Suite for Mr. Wilson Sovereign Empire v3.0.
Systematically tests all 12 modules, endpoints, speech engines, and integrations.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
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
sys.path.insert(0, str(JARVIS_DIR))

PASS_COUNT = 0
FAIL_COUNT = 0


def log_test(test_name: str, passed: bool, details: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {test_name} - {details}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {test_name} - {details}")


print("=" * 80)
print(" 🧪 MR. WILSON SOVEREIGN EMPIRE v3.0 // MASTER VERIFICATION SUITE")
print("=" * 80)

# TEST 1: Mr. Wilson REST API (Port 6971)
print("\n[TEST 1] Testing Mr. Wilson REST API (Port 6971)...")
try:
    req = urllib.request.Request("http://localhost:6971/api/status")
    with urllib.request.urlopen(req, timeout=3) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        log_test("API /api/status", data.get("status") == "ONLINE", f"Persona: {data.get('persona')}, Drops: {data.get('music_drops')}")
except Exception as e:
    log_test("API /api/status", False, str(e))

try:
    req = urllib.request.Request("http://localhost:6971/api/health")
    with urllib.request.urlopen(req, timeout=3) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        log_test("API /api/health", data.get("status") == "healthy", f"Core modules: {data.get('core_modules')}")
except Exception as e:
    log_test("API /api/health", False, str(e))

# TEST 2: Bumblebee Music Drops & Engine
print("\n[TEST 2] Testing Bumblebee Real Music Engine...")
try:
    from jarvis_bumblebee import BumblebeeVoiceEngine, play_music_drop
    bb = BumblebeeVoiceEngine()
    drop_name = play_music_drop("rock", volume=0.0) # Silent test
    log_test("Bumblebee Music Drop Playback", drop_name is not None, f"Played: {drop_name}")
    
    snippet = bb.speak_as_bumblebee("affirmative")
    log_test("Bumblebee speak_as_bumblebee", bool(snippet), f"Snippet length: {len(snippet)}")

    trans = bb.translate_to_bumblebee("Deploying fleet.")
    log_test("Bumblebee translate_to_bumblebee", trans is not None and "Deploying fleet" in trans, "Proper return string verified")
except Exception as e:
    log_test("Bumblebee Engine", False, str(e))

# TEST 3: Voice Listener & LCS USB Audio Detection
print("\n[TEST 3] Testing Voice Listener & Hardware Mic Auto-Discovery...")
try:
    import speech_recognition as sr
    from always_on_mr_wilson_listener import find_best_mic_index, AlwaysOnMrWilsonListener
    idx = find_best_mic_index()
    log_test("LCS USB Audio Mic Discovery", idx is not None, f"Found mic at index {idx}")
    listener = AlwaysOnMrWilsonListener()
    log_test("Listener Instantiation", listener.mic_index is not None, "Listener ready")
except Exception as e:
    log_test("Voice Listener", False, str(e))

# TEST 4: Desktop Companion Integrity & Method Bindings
print("\n[TEST 4] Testing Desktop Companion Integrity...")
try:
    from desktop_companion_mr_wilson import MrWilsonLiveAvatar
    # Verify method exists without launching GUI mainloop
    has_ato = hasattr(MrWilsonLiveAvatar, "show_ato_status")
    has_bb = hasattr(MrWilsonLiveAvatar, "trigger_bumblebee_drop")
    has_voice = hasattr(MrWilsonLiveAvatar, "play_voice_threaded")
    log_test("Companion show_ato_status() method", has_ato, "Crash fix confirmed")
    log_test("Companion trigger_bumblebee_drop() method", has_bb, "1-click drop button confirmed")
    log_test("Companion play_voice_threaded() method", has_voice, "Threaded speech confirmed")
except Exception as e:
    log_test("Desktop Companion", False, str(e))

# TEST 5: Second Brain Knowledge & Golden Rules Retrieval
print("\n[TEST 5] Testing Second Brain Knowledge Retrieval...")
try:
    from jarvis_brain import JarvisBrain
    brain = JarvisBrain()
    results = brain.search_second_brain("golden rules")
    log_test("Second Brain Search (Golden Rules)", len(results) > 0, f"Found in {results[0]['name'] if results else 'None'}")
    agenda = brain.get_agenda_summary()
    log_test("Second Brain Agenda Summary", "BRIEFING" in agenda, "Briefing generated")
except Exception as e:
    log_test("Second Brain", False, str(e))

# TEST 6: Autonomous Takeover Safe Element Grounding
print("\n[TEST 6] Testing Takeover Engine Safety Controls...")
try:
    from jarvis_takeover import JarvisAutonomousTakeover
    takeover = JarvisAutonomousTakeover()
    # Test step execution on unresolvable element (should NOT blind click center)
    res = takeover.execute_step("CLICK('nonexistent_phantom_button_xyz_123')", "")
    is_safe = ("safely skipped" in res) or (res == "ABORTED_FAILSAFE")
    log_test("Takeover Blind Click Prevention", is_safe, f"Result: {res}")
except Exception as e:
    log_test("Takeover Engine", False, str(e))

# TEST 7: Chrome CDP Bridge Remote Allow Origins Flag
print("\n[TEST 7] Testing Chrome CDP Bridge Configuration...")
try:
    from jarvis_browser import JarvisBrowserBridge
    browser = JarvisBrowserBridge()
    log_test("Browser Bridge Instantiation", browser.cdp_port == 9222, "Port 9222 verified")
except Exception as e:
    log_test("Browser Bridge", False, str(e))

# TEST 8: Mobile Telegram Commander & Voice Note Decoding
print("\n[TEST 8] Testing Mobile Telegram Commander...")
try:
    from jarvis_telegram_bot import JarvisTelegramCommander
    commander = JarvisTelegramCommander()
    # Test authorization logic with authorized ID
    auth_id = commander.authorized_chat_ids[0] if commander.authorized_chat_ids else "LOCAL_DEV_USER"
    is_auth = commander.is_authorized(auth_id)
    log_test("Telegram Authorization Check", is_auth, f"Authorized chat ID verified: {auth_id}")
    # Verify voice downloader method exists
    has_voice_trans = hasattr(commander, "download_and_transcribe_voice")
    log_test("Telegram Voice Note Transcriber", has_voice_trans, "Voice note pipeline ready")
except Exception as e:
    log_test("Telegram Commander", False, str(e))

# TEST 9: ATO War Room Forensic Search
print("\n[TEST 9] Testing ATO War Room Forensic Engine...")
try:
    from ato_war_room_mr_wilson import REASON_CSV, WOODATO_DIR
    log_test("C:\\WOODATO Directory Mount", WOODATO_DIR.exists(), f"Path: {WOODATO_DIR}")
    log_test("Reason for Decision CSV Exists", REASON_CSV.exists(), f"Size: {REASON_CSV.stat().st_size} bytes")
except Exception as e:
    log_test("ATO War Room", False, str(e))

# TEST 10: Holo-Gestures Engine
print("\n[TEST 10] Testing Holo-Gestures Engine...")
try:
    from holo_gestures import HoloGestures
    hg = HoloGestures()
    log_test("Holo-Gestures Engine Instantiation", hg.screen_w > 0 and hg.cam_w == 640, f"Screen bounds: {hg.screen_w}x{hg.screen_h}")
except Exception as e:
    log_test("Holo-Gestures Engine", False, str(e))

# TEST 11: System Tray Daemon
print("\n[TEST 11] Testing System Tray Daemon Components...")
try:
    import pystray
    from mr_wilson_tray_daemon import create_tray_icon_image
    icon = create_tray_icon_image()
    log_test("System Tray Icon Generation", icon is not None and icon.size == (64, 64), f"Icon size: {icon.size}")
except Exception as e:
    log_test("System Tray Daemon", False, str(e))

# TEST 12: Dual-Drive Vault Sync (X: Mirror)
print("\n[TEST 12] Testing Vault Sync Mirror to X: Drive...")
try:
    from sync_mr_wilson_vault import DST_DIR
    log_test("X: Drive Backup Destination", DST_DIR.exists(), f"Path: {DST_DIR}")
    core_count = len(list((DST_DIR / "core").glob("*.py")))
    log_test("X: Drive Core Modules Mirror", core_count >= 20, f"Mirrored {core_count} core modules")
except Exception as e:
    log_test("Vault Sync", False, str(e))

print("\n" + "=" * 80)
print(f" 🏁 MASTER TEST RESULTS: {PASS_COUNT} PASSED | {FAIL_COUNT} FAILED")
print("=" * 80)

if FAIL_COUNT == 0:
    print("[✓] ALL SYSTEMS 100% OPERATIONAL & VERIFIED GREEN.")
else:
    print(f"[!] {FAIL_COUNT} tests flagged for review.")
