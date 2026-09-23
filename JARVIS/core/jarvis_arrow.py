#!/usr/bin/env python3
"""
JARVIS AI Arrow & Visual Guidance Overlay — As Featured in the Iron Man JARVIS Demo.
Renders a transparent, click-through, animated holographic arrow and targeting HUD directly on top
of any Windows application to show the user exactly where to click.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing
import os
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from typing import Optional, Tuple

import pyautogui

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

TRANSPARENT_COLOR = "#010101"
NEON_CYAN = "#00f0ff"
NEON_GLOW = "#0088ff"
NEON_GOLD = "#ffcc00"
DARK_HUD_BG = "#0a101f"


class JarvisArrowOverlay:
    def __init__(self, target_x: int, target_y: int, label: str = "CLICK HERE", duration_sec: float = 5.0, mode: str = "guide"):
        self.target_x = target_x
        self.target_y = target_y
        self.label = label
        self.duration_sec = duration_sec
        self.mode = mode
        self.start_time = time.time()
        self.pulse_phase = 0.0

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Set transparency key for Windows
        self.root.config(bg=TRANSPARENT_COLOR)
        try:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        except Exception:
            pass

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Hotkeys to close overlay
        self.root.bind("<Escape>", lambda e: self.close())
        self.canvas.bind("<Button-1>", lambda e: self.on_click(e))

        # Schedule animation
        self.animate()

        if self.mode == "takeover":
            threading.Thread(target=self._smooth_takeover_action, daemon=True).start()

    def on_click(self, event):
        """Allow clicking through or dismiss."""
        self.close()

    def close(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def _smooth_takeover_action(self):
        """Take over mouse, move along bezier curve, click and ripple."""
        time.sleep(0.8)
        start_x, start_y = pyautogui.position()
        dist = math.hypot(self.target_x - start_x, self.target_y - start_y)
        steps = max(20, int(dist / 30))

        # Human-like bezier trajectory
        ctrl_x = (start_x + self.target_x) / 2 + (dist * 0.15)
        ctrl_y = (start_y + self.target_y) / 2 - (dist * 0.15)

        for i in range(steps + 1):
            t = i / float(steps)
            # Quadratic Bezier
            cur_x = (1 - t)**2 * start_x + 2 * (1 - t) * t * ctrl_x + t**2 * self.target_x
            cur_y = (1 - t)**2 * start_y + 2 * (1 - t) * t * ctrl_y + t**2 * self.target_y
            pyautogui.moveTo(int(cur_x), int(cur_y))
            time.sleep(0.015)

        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.5)
        self.close()

    def draw_hud(self):
        self.canvas.delete("all")

        elapsed = time.time() - self.start_time
        if elapsed > self.duration_sec and self.mode != "takeover":
            self.close()
            return

        self.pulse_phase += 0.15
        pulse = math.sin(self.pulse_phase)
        scale = 1.0 + (pulse * 0.12)
        offset_bounce = int(pulse * 8)

        tx, ty = self.target_x, self.target_y

        # 1. Target Reticle / Concentric Hologram Rings
        r_inner = 18 * scale
        r_outer = 32 * scale
        
        # Outer glow ring
        self.canvas.create_oval(tx - r_outer, ty - r_outer, tx + r_outer, ty + r_outer, outline=NEON_GLOW, width=2)
        # Inner sharp ring
        self.canvas.create_oval(tx - r_inner, ty - r_inner, tx + r_inner, ty + r_inner, outline=NEON_CYAN, width=3)
        # Center target dot
        self.canvas.create_oval(tx - 4, ty - 4, tx + 4, ty + 4, fill=NEON_GOLD, outline=NEON_CYAN)

        # Crosshairs
        self.canvas.create_line(tx - r_outer - 10, ty, tx - r_inner, ty, fill=NEON_CYAN, width=2)
        self.canvas.create_line(tx + r_inner, ty, tx + r_outer + 10, ty, fill=NEON_CYAN, width=2)
        self.canvas.create_line(tx, ty - r_outer - 10, tx, ty - r_inner, fill=NEON_CYAN, width=2)
        self.canvas.create_line(tx, ty + r_inner, tx, ty + r_outer + 10, fill=NEON_CYAN, width=2)

        # 2. Pulsating Arrow Pointing at Target
        # Determine best arrow placement (above target if space permits, else below)
        arrow_len = 65
        tip_x = tx
        tip_y = ty - int(r_outer) - 6 + offset_bounce
        
        base_x = tip_x
        base_y = tip_y - arrow_len
        
        if tip_y < 100:
            # Place arrow below target pointing UP
            tip_y = ty + int(r_outer) + 6 - offset_bounce
            base_y = tip_y + arrow_len
            
            # Arrow head pointing UP
            self.canvas.create_line(base_x, base_y, tip_x, tip_y, fill=NEON_CYAN, width=6)
            self.canvas.create_polygon(
                tip_x, tip_y,
                tip_x - 18, tip_y + 24,
                tip_x + 18, tip_y + 24,
                fill=NEON_GOLD, outline=NEON_CYAN, width=2
            )
            # Label Position Below Arrow
            box_y = base_y + 20
        else:
            # Arrow head pointing DOWN
            self.canvas.create_line(base_x, base_y, tip_x, tip_y, fill=NEON_CYAN, width=6)
            self.canvas.create_polygon(
                tip_x, tip_y,
                tip_x - 18, tip_y - 24,
                tip_x + 18, tip_y - 24,
                fill=NEON_GOLD, outline=NEON_CYAN, width=2
            )
            # Label Position Above Arrow
            box_y = base_y - 20

        # 3. Sleek Floating JARVIS Tooltip Badge
        text_content = f"🎯 JARVIS AI ARROW: {self.label} ({tx}, {ty})"
        char_w = 9
        box_w = max(240, len(text_content) * char_w)
        box_h = 36
        box_x = max(10, min(self.screen_w - box_w - 10, base_x - (box_w // 2)))

        # Rounded background box
        self.canvas.create_rectangle(
            box_x, box_y - (box_h // 2),
            box_x + box_w, box_y + (box_h // 2),
            fill=DARK_HUD_BG, outline=NEON_CYAN, width=2
        )
        self.canvas.create_text(
            box_x + (box_w // 2), box_y,
            text=text_content,
            fill="#ffffff",
            font=("Segoe UI", 10, "bold")
        )

    def animate(self):
        try:
            self.draw_hud()
            self.root.after(40, self.animate)
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


def _spawn_overlay_process(x: int, y: int, label: str, duration: float, mode: str):
    overlay = JarvisArrowOverlay(x, y, label, duration, mode)
    overlay.run()


def show_ai_arrow(x: int, y: int, label: str = "TARGET", duration: float = 5.0, mode: str = "guide", async_mode: bool = True):
    """Show the pulsating JARVIS AI Arrow at given screen coordinates."""
    if async_mode:
        p = multiprocessing.Process(
            target=_spawn_overlay_process,
            args=(x, y, label, duration, mode),
            daemon=True
        )
        p.start()
        return p
    else:
        _spawn_overlay_process(x, y, label, duration, mode)


def show_ai_arrow_by_query(query: str, mode: str = "guide", duration: float = 6.0) -> Optional[Tuple[int, int]]:
    """Locate element on screen via vision and point JARVIS AI arrow at it."""
    from jarvis_vision import get_vision
    from jarvis_voice import get_voice

    vision = get_vision()
    voice = get_voice()

    voice.speak(f"Locating {query} on your screen.")
    coords = vision.locate_element(query)

    if coords:
        x, y = coords
        voice.speak(f"Found it. Pointing arrow at coordinates {x}, {y}.")
        show_ai_arrow(x, y, label=query.upper(), duration=duration, mode=mode, async_mode=False)
        return coords
    else:
        voice.speak(f"I could not visually identify {query} on your screen.")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS AI Arrow Overlay")
    parser.add_argument("--x", type=int, default=None)
    parser.add_argument("--y", type=int, default=None)
    parser.add_argument("--query", type=str, default=None, help="Visual query, e.g., 'Instagram Settings' or 'Submit button'")
    parser.add_argument("--label", type=str, default="TARGET ELEMENT")
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--mode", choices=["guide", "takeover"], default="guide")
    args = parser.parse_args()

    if args.query:
        show_ai_arrow_by_query(args.query, mode=args.mode, duration=args.duration)
    elif args.x is not None and args.y is not None:
        show_ai_arrow(args.x, args.y, label=args.label, duration=args.duration, mode=args.mode, async_mode=False)
    else:
        # Default demo at center of screen
        sw, sh = pyautogui.size()
        show_ai_arrow(sw // 2, sh // 2, label="CENTER DEMO", duration=5.0, mode="guide", async_mode=False)
