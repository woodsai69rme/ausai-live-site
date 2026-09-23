#!/usr/bin/env python3
"""
JARVIS Video Storyboard Visualizer.
Renders high-fidelity 4-scene contact sheet graphics for video manifests,
overlaying timestamps, hook voiceovers, and motion prompts with a tactical HUD style.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
MANIFEST_DIR = JARVIS_DIR / "content_vault" / "video_manifests"


def render_storyboard_preview(manifest_path: Path) -> Path:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    title = data.get("title", "Video Storyboard")

    # Canvas dimensions: 1920x1080 (16:9 contact sheet of four 9:16 or 16:9 panels)
    width, height = 1600, 900
    img = Image.new("RGB", (width, height), color=(6, 9, 19))
    draw = ImageDraw.Draw(img)

    # Grid background lines
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(12, 20, 36), width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(12, 20, 36), width=1)

    # Header
    draw.rectangle([(0, 0), (width, 80)], fill=(9, 14, 28))
    draw.line([(0, 80), (width, 80)], fill=(0, 240, 255), width=2)
    draw.text((30, 22), f"⚡ JARVIS VIDEO PRODUCTION MANIFEST // {title.upper()}", fill=(240, 246, 252))
    draw.text((width - 320, 28), f"WAN 2.2 LIGHTNING • 60 SECONDS", fill=(0, 240, 255))

    # 4 Scene Panels (2x2 Grid)
    panel_w = 750
    panel_h = 360
    coords = [
        (35, 110),
        (815, 110),
        (35, 500),
        (815, 500)
    ]

    colors = [
        (0, 240, 255),    # Cyan
        (245, 158, 11),   # Gold
        (168, 85, 247),   # Purple
        (16, 185, 129)    # Emerald
    ]

    for i, s in enumerate(scenes[:4]):
        px, py = coords[i]
        c = colors[i]

        # Panel Box
        draw.rectangle([(px, py), (px + panel_w, py + panel_h)], fill=(9, 14, 28), outline=(20, 35, 60), width=2)
        # Accent Corner
        draw.line([(px, py), (px + 20, py)], fill=c, width=3)
        draw.line([(px, py), (px, py + 20)], fill=c, width=3)

        # Header of Panel
        draw.rectangle([(px, py), (px + panel_w, py + 36)], fill=(13, 22, 44))
        draw.text((px + 14, py + 10), f"SCENE 0{s.get('scene_id', i+1)} // {s.get('timestamp', '')}", fill=c)
        draw.text((px + panel_w - 140, py + 10), f"DURATION: {s.get('duration_sec', 0)}s", fill=(148, 163, 184))

        # Visual Prompt Box
        draw.text((px + 16, py + 48), "VISUAL PROMPT (WAN 2.2 / COMFYUI):", fill=(100, 116, 139))
        vp = s.get("visual_prompt", "")
        # Simple wrap
        vp_lines = [vp[j:j+80] for j in range(0, min(len(vp), 160), 80)]
        for k, line in enumerate(vp_lines):
            draw.text((px + 16, py + 70 + (k * 18)), line, fill=(226, 232, 240))

        # Motion Direction Box
        draw.text((px + 16, py + 130), f"MOTION / CAMERA: {s.get('motion_direction', '')}", fill=(56, 189, 248))

        # Hook Voiceover
        draw.rectangle([(px + 10, py + 180), (px + panel_w - 10, py + panel_h - 15)], fill=(4, 8, 18), outline=(25, 40, 70), width=1)
        draw.text((px + 20, py + 192), "VOICEOVER AUDIO (KOKORO-82M / EDGE-TTS):", fill=c)
        vo = s.get("hook_voiceover", "")
        vo_lines = [vo[j:j+75] for j in range(0, min(len(vo), 225), 75)]
        for k, line in enumerate(vo_lines):
            draw.text((px + 20, py + 220 + (k * 22)), f"\"{line}\"", fill=(255, 255, 255))

    out_img = MANIFEST_DIR / f"Preview_{manifest_path.stem}.png"
    img.save(out_img, "PNG")
    print(f"[+] Rendered Storyboard Preview: {out_img}")
    return out_img


if __name__ == "__main__":
    manifests = list(MANIFEST_DIR.glob("*.json"))
    if manifests:
        render_storyboard_preview(manifests[0])
    else:
        print("[!] No manifests found in", MANIFEST_DIR)
