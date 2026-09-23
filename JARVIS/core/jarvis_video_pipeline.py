#!/usr/bin/env python3
"""
JARVIS & SPARK Autonomous Script-to-Video Pipeline.
Takes SPARK exploded content scripts and automatically formats them into
a 60-second video production manifest with scenes, audio voiceovers, keyframe visual prompts,
and transient timing compatible with ComfyUI Wan 2.2 and Tellem Studio.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_kokoro import get_neural_voice

VIDEO_VAULT = JARVIS_DIR / "content_vault" / "video_manifests"
VIDEO_VAULT.mkdir(parents=True, exist_ok=True)


class JarvisVideoPipeline:
    def __init__(self):
        self.voice = get_neural_voice()

    def generate_video_manifest(self, topic: str) -> Path:
        """Create a 60-second video timeline manifest for Wan 2.2 / Tellem Studio."""
        safe_topic = re.sub(r"\W+", "_", topic)[:30]
        out_file = VIDEO_VAULT / f"Video_Manifest_{safe_topic}.json"

        self.voice.speak(f"SPARK Video Pipeline generating 60-second production manifest for {topic}.")
        print(f"\n[SPARK Video 🎬] Generating Video Manifest for: \"{topic}\"")

        # 4-Scene Breakdown for 60s Reel/Short
        scenes = [
            {
                "scene_id": 1,
                "timestamp": "00:00 - 00:08",
                "duration_sec": 8.0,
                "hook_voiceover": f"Stop doing manual tasks on your PC. Here is how autonomous AI copilots run in 2026.",
                "visual_prompt": f"Cyberpunk holographic HUD interface on dark workstation display, glowing neon cyan reticle, octane render 8k",
                "motion_direction": "slow push in, futuristic grid animation"
            },
            {
                "scene_id": 2,
                "timestamp": "00:08 - 00:24",
                "duration_sec": 16.0,
                "hook_voiceover": f"With Set-of-Marks visual perception, the AI sees every button, navigates software, and creates client invoices from voice notes in seconds.",
                "visual_prompt": f"Computer screen with neon numbered badges overlaying UI menus, smooth bezier mouse cursor navigating windows, tech studio lighting",
                "motion_direction": "dynamic pan across multi-window layout"
            },
            {
                "scene_id": 3,
                "timestamp": "00:24 - 00:45",
                "duration_sec": 21.0,
                "hook_voiceover": f"AI Employees like TARS compile three-tier proposals while SPARK explodes one topic into 15 multi-platform posts automatically.",
                "visual_prompt": f"Iron man style tactical war room radar with multi-service telemetry, emerald green and gold analytics graphs",
                "motion_direction": "slow orbit around floating data panels"
            },
            {
                "scene_id": 4,
                "timestamp": "00:45 - 00:60",
                "duration_sec": 15.0,
                "hook_voiceover": f"Deploy your own private copilot today or comment COPILOT below for our free setup blueprint.",
                "visual_prompt": f"Sleek AusAI Tech logo pulsing with electric energy, modern typography CTA, dark aesthetic",
                "motion_direction": "fade to black with glowing reactor icon"
            }
        ]

        manifest = {
            "title": f"Autonomous AI Copilot 2026: {topic}",
            "generated_at": datetime.datetime.now().isoformat(),
            "target_format": "9:16 Vertical Video (1080x1920) / YouTube Shorts & TikTok",
            "total_duration": "60 seconds",
            "model_targets": {
                "video_generator": "Wan 2.2 Mega TI2V-5B (4-Step Lightning)",
                "tts_engine": "Kokoro-82M / Edge-TTS",
                "audio_bpm": 128
            },
            "scenes": scenes
        }

        out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"[+] Video Manifest saved: {out_file}")
        self.voice.speak("Video storyboard and scene manifest generated successfully.")
        return out_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Video Pipeline")
    parser.add_argument("--topic", type=str, default="How AI Employees Run Autonomous Workstations in 2026")
    args = parser.parse_args()

    pipeline = JarvisVideoPipeline()
    pipeline.generate_video_manifest(args.topic)
