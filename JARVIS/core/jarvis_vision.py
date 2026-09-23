#!/usr/bin/env python3
"""
JARVIS Vision Engine — High-Speed Screen Perception & Multi-Modal Visual Grounding.
Captures screen state, analyzes UI layouts, and extracts precise (X, Y) pixel coordinates.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyautogui
from PIL import Image

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
SCREENSHOT_DIR = JARVIS_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "REDACTED_API_KEY"
)

VISION_MODELS = [
    "openrouter/free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free",
]



class JarvisVisionEngine:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()

    def capture_screen(self, filename: str = "current_view.png") -> Tuple[Path, str]:
        """Capture ultra-fast screenshot of primary display."""
        path = SCREENSHOT_DIR / filename
        try:
            import mss
            import mss.tools
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                img = sct.grab(monitor)
                mss.tools.to_png(img.rgb, img.size, output=str(path))
        except Exception:
            try:
                shot = pyautogui.screenshot()
                shot.save(path)
            except Exception:
                img = Image.new("RGB", (self.screen_w, self.screen_h), color=(20, 20, 25))
                img.save(path)

        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return path, b64

    def query_vision_llm(self, prompt: str, image_b64: Optional[str] = None, model_idx: int = 0) -> str:
        """Query vision models with automatic failover across free models and Ollama."""
        models_to_try = [VISION_MODELS[model_idx % len(VISION_MODELS)]] + [
            m for i, m in enumerate(VISION_MODELS) if i != (model_idx % len(VISION_MODELS))
        ]

        for model in models_to_try:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://jarvis.local",
                    "X-Title": "JARVIS Autonomous Copilot",
                }

                content_payload: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
                if image_b64:
                    content_payload.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    })

                body = {
                    "model": model,
                    "messages": [{"role": "user", "content": content_payload}],
                    "temperature": 0.1,
                    "max_tokens": 1000,
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    result = data["choices"][0]["message"]["content"]
                    if result and result.strip():
                        return result.strip()
            except Exception as e:
                # Try next model
                continue

        # Local Ollama fallback
        return self._query_ollama(prompt, image_b64)

    def _query_ollama(self, prompt: str, image_b64: Optional[str] = None) -> str:
        """Local Ollama vision/text fallback with UI-TARS, MiniCPM-V, and Ornith support."""
        local_candidates = ["ui-tars:7b", "minicpm-v:latest", "ornith:9b", "qwen3.5:9b"]
        for cand in local_candidates:
            try:
                url = "http://localhost:11434/api/generate"
                body: Dict[str, Any] = {
                    "model": cand,
                    "prompt": prompt,
                    "stream": False,
                }
                if image_b64 and cand in ("ui-tars:7b", "minicpm-v:latest"):
                    body["images"] = [image_b64]

                req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    res = data.get("response", "").strip()
                    if res:
                        return res
            except Exception:
                continue
        return ""


    def locate_element(self, element_description: str, screenshot_b64: Optional[str] = None) -> Optional[Tuple[int, int]]:
        """Find the exact (X, Y) pixel coordinates of a UI element on the screen."""
        if not screenshot_b64:
            _, screenshot_b64 = self.capture_screen("temp_locate.png")

        prompt = (
            f"You are the visual coordinate locator for JARVIS on a Windows 11 system.\n"
            f"Screen Resolution: {self.screen_w} x {self.screen_h}\n\n"
            f"Target Element: '{element_description}'\n\n"
            "Analyze the image carefully. Locate the exact center of this element.\n"
            "Respond ONLY with the pixel coordinates in the exact format: (X, Y)\n"
            f"Example: ({self.screen_w // 2}, {self.screen_h // 2})\n"
            "Do not include any other markdown or conversational filler."
        )

        response = self.query_vision_llm(prompt, screenshot_b64, model_idx=1)
        coords = self.extract_coordinates(response)
        return coords

    def extract_coordinates(self, text: str) -> Optional[Tuple[int, int]]:
        """Parse (X, Y) pixel coordinates from text."""
        if not text:
            return None

        # Look for explicit (X, Y) pattern
        matches = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", text)
        if matches:
            x, y = int(matches[0][0]), int(matches[0][1])
            # Handle normalized [0, 1000] space if applicable
            if x <= 1000 and y <= 1000 and (self.screen_w > 1000 or self.screen_h > 1000):
                x = int((x / 1000.0) * self.screen_w)
                y = int((y / 1000.0) * self.screen_h)
            x = max(10, min(self.screen_w - 10, x))
            y = max(10, min(self.screen_h - 10, y))
            return x, y

        # Look for "x: 123, y: 456"
        xy_match = re.search(r"x\s*[:=]\s*(\d+).*?y\s*[:=]\s*(\d+)", text, re.IGNORECASE)
        if xy_match:
            x, y = int(xy_match.group(1)), int(xy_match.group(2))
            x = max(10, min(self.screen_w - 10, x))
            y = max(10, min(self.screen_h - 10, y))
            return x, y

        return None

    def describe_screen(self, screenshot_b64: Optional[str] = None) -> str:
        """Provide a rich situational awareness description of the current screen."""
        if not screenshot_b64:
            _, screenshot_b64 = self.capture_screen("temp_describe.png")

        prompt = (
            "Describe what is currently visible on the screen in 2-3 concise bullet points. "
            "Identify the active application window, main content, and any pending notifications or buttons."
        )
        return self.query_vision_llm(prompt, screenshot_b64, model_idx=0)


_vision_instance: Optional[JarvisVisionEngine] = None

def get_vision() -> JarvisVisionEngine:
    global _vision_instance
    if _vision_instance is None:
        _vision_instance = JarvisVisionEngine()
    return _vision_instance

if __name__ == "__main__":
    v = get_vision()
    path, b64 = v.capture_screen("test.png")
    print(f"[+] Screen captured: {path} ({v.screen_w}x{v.screen_h})")
    desc = v.describe_screen(b64)
    print(f"[+] Description:\n{desc}")
