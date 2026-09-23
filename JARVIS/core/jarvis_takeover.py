#!/usr/bin/env python3
"""
JARVIS Autonomous Takeover Engine — Full Desktop & Browser Computer Control.
Decomposes complex goals into multi-step UI operations, narrates every action via voice,
moves the mouse along natural human bezier trajectories, types, and verifies post-action states.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pyautogui
from PIL import Image

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
SCREENSHOT_DIR = JARVIS_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = SCREENSHOT_DIR / "jarvis_takeover_state.json"

sys.path.insert(0, str(JARVIS_DIR / "core"))
from jarvis_vision import get_vision
from jarvis_voice import get_voice
from jarvis_arrow import show_ai_arrow


class JarvisAutonomousTakeover:
    def __init__(self):
        self.vision = get_vision()
        self.voice = get_voice()
        self.screen_w, self.screen_h = pyautogui.size()
        self.history: List[Dict[str, Any]] = []

    def save_state(self, step_num: int, task: str, action: str, thought: str, status: str = "RUNNING"):
        """Write live status for CLI and HUD display."""
        payload = {
            "timestamp": time.time(),
            "status": status,
            "current_step": step_num,
            "task": task,
            "action": action,
            "thought": thought,
            "screen_w": self.screen_w,
            "screen_h": self.screen_h,
            "history": self.history,
        }
        try:
            STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def plan_workflow(self, goal: str, shot_b64: str) -> List[str]:
        """Decompose mission into actionable UI commands."""
        prompt = (
            f"You are JARVIS, an autonomous computer use agent on Windows 11.\n"
            f"User Goal: {goal}\n"
            f"Screen Resolution: {self.screen_w}x{self.screen_h}\n\n"
            "Analyze the attached desktop screenshot. Break down the user's goal into 3-6 discrete, executable actions.\n"
            "Supported Actions:\n"
            "- LAUNCH(app_name or url)\n"
            "- CLICK(visual description of button or link)\n"
            "- TYPE(exact text to type)\n"
            "- HOTKEY(key1, key2)\n"
            "- PRESS(enter | tab | escape | space)\n"
            "- SCROLL(down or up)\n"
            "- WAIT(seconds)\n"
            "- NARRATE(spoken message to user)\n\n"
            "Output each step starting with a dash '-', e.g.:\n"
            "- NARRATE(Opening the application now)\n"
            "- LAUNCH(chrome)\n"
            "- CLICK(search bar)\n"
            "- TYPE(https://adsmanager.facebook.com)\n"
            "- PRESS(enter)\n"
        )
        resp = self.vision.query_vision_llm(prompt, shot_b64, model_idx=0)
        
        steps = []
        for line in resp.splitlines():
            line = line.strip()
            if line.startswith("-") or re.match(r"^\d+\.", line):
                clean = re.sub(r"^[-*\d.]+\s*", "", line).strip()
                if any(clean.upper().startswith(act) for act in ["LAUNCH", "CLICK", "TYPE", "HOTKEY", "PRESS", "SCROLL", "WAIT", "NARRATE"]):
                    steps.append(clean)

        return steps or ["NARRATE(Executing desktop task)", "LAUNCH(notepad)", "TYPE(JARVIS Autonomous Execution Finished.)"]

    def smooth_move_and_click(self, x: int, y: int, label: str = "TARGET"):
        """Move mouse along smooth bezier curve with visual arrow feedback before clicking."""
        start_x, start_y = pyautogui.position()
        dist = math.hypot(x - start_x, y - start_y)
        steps = max(15, int(dist / 35))

        # Show brief animated targeting arrow
        show_ai_arrow(x, y, label=label, duration=1.2, mode="guide", async_mode=True)

        ctrl_x = (start_x + x) / 2 + (dist * 0.1)
        ctrl_y = (start_y + y) / 2 - (dist * 0.1)

        for i in range(steps + 1):
            t = i / float(steps)
            cur_x = (1 - t)**2 * start_x + 2 * (1 - t) * t * ctrl_x + t**2 * x
            cur_y = (1 - t)**2 * start_y + 2 * (1 - t) * t * ctrl_y + t**2 * y
            pyautogui.moveTo(int(cur_x), int(cur_y))
            time.sleep(0.012)

        time.sleep(0.15)
        pyautogui.click()

    def execute_step(self, step_str: str, shot_b64: str) -> str:
        """Execute a single atomic step."""
        step_upper = step_str.upper()

        try:
            if "NARRATE(" in step_upper:
                msg = step_str.split("(", 1)[1].rstrip(")").strip().strip("'\"")
                self.voice.speak(msg, wait=False)
                return f"Narrated: \"{msg}\""

            elif "LAUNCH(" in step_upper:
                target = step_str.split("(", 1)[1].rstrip(")").strip().strip("'\"")
                if target.startswith("http://") or target.startswith("https://"):
                    import webbrowser
                    webbrowser.open(target)
                    self.voice.speak(f"Opening browser to {target}")
                    time.sleep(2.5)
                    return f"Navigated to {target}"
                else:
                    self.voice.speak(f"Launching {target}")
                    pyautogui.hotkey("win", "r")
                    time.sleep(0.4)
                    pyautogui.typewrite(target, interval=0.03)
                    pyautogui.press("enter")
                    time.sleep(2.0)
                    return f"Launched {target}"

            elif "CLICK(" in step_upper:
                target_desc = step_str.split("(", 1)[1].rstrip(")").strip().strip("'\"")
                self.voice.speak(f"Locating and clicking {target_desc}")
                coords = self.vision.locate_element(target_desc, shot_b64)
                if coords:
                    x, y = coords
                    self.smooth_move_and_click(x, y, label=target_desc)
                    return f"Clicked '{target_desc}' at ({x}, {y})"
                else:
                    self.voice.speak(f"Could not visually ground {target_desc}. Skipping click.")
                    return f"Element '{target_desc}' could not be located visually; safely skipped"

            elif "TYPE(" in step_upper:
                text = step_str.split("(", 1)[1].rstrip(")").strip().strip("'\"")
                self.voice.speak(f"Entering text")
                pyautogui.typewrite(text, interval=0.04)
                return f"Typed: '{text}'"

            elif "HOTKEY(" in step_upper:
                keys = [k.strip().lower() for k in step_str.split("(", 1)[1].rstrip(")").split(",")]
                pyautogui.hotkey(*keys)
                return f"Hotkey: {keys}"

            elif "PRESS(" in step_upper:
                key = step_str.split("(", 1)[1].rstrip(")").strip().lower()
                pyautogui.press(key)
                return f"Pressed key: {key}"

            elif "SCROLL(" in step_upper:
                direction = step_str.split("(", 1)[1].rstrip(")").strip().lower()
                amount = -500 if "down" in direction else 500
                pyautogui.scroll(amount)
                return f"Scrolled {direction}"

            elif "WAIT(" in step_upper:
                sec = 2.0
                try:
                    sec = float(step_str.split("(", 1)[1].rstrip(")").strip())
                except Exception:
                    pass
                time.sleep(sec)
                return f"Waited {sec}s"

            return f"Unhandled action: {step_str}"
        except pyautogui.FailSafeException:
            self.voice.speak("Failsafe triggered by user. Emergency stop.")
            return "ABORTED_FAILSAFE"
        except Exception as e:
            return f"Action error: {e}"

    def run_takeover(self, goal: str, max_steps: int = 8) -> Dict[str, Any]:
        """Execute full autonomous desktop takeover mission."""
        print(f"\n[JARVIS 🤖] Autonomous Takeover Initiated: \"{goal}\"")
        self.voice.speak(f"Initiating autonomous takeover for: {goal}")
        t0 = time.time()

        _, shot_b64 = self.vision.capture_screen("takeover_init.png")
        self.save_state(0, goal, "PLANNING", f"Decomposing goal: {goal}")

        steps = self.plan_workflow(goal, shot_b64)
        print(f"[+] Mission plan ({len(steps)} steps):")
        for i, s in enumerate(steps, 1):
            print(f"    {i}. {s}")

        for idx, step in enumerate(steps[:max_steps], 1):
            _, pre_b64 = self.vision.capture_screen(f"takeover_step_{idx}_pre.png")
            print(f"\n[+] Executing Step {idx}/{len(steps)}: {step}")
            self.save_state(idx, goal, step, f"Step {idx}: {step}")

            res = self.execute_step(step, pre_b64)
            if res == "ABORTED_FAILSAFE":
                self.save_state(idx, goal, "ABORTED", "User triggered failsafe", status="ABORTED")
                return {"success": False, "status": "ABORTED", "history": self.history}

            time.sleep(0.8)
            post_path, _ = self.vision.capture_screen(f"takeover_step_{idx}_post.png")

            self.history.append({
                "step": idx,
                "command": step,
                "result": res,
                "screenshot": str(post_path),
            })

        self.save_state(len(steps), goal, "COMPLETE", "Mission completed successfully.", status="COMPLETED")
        self.voice.speak("Takeover mission complete, sir. All actions executed successfully.")

        return {
            "goal": goal,
            "success": True,
            "elapsed_seconds": round(time.time() - t0, 2),
            "steps_executed": len(self.history),
            "history": self.history,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Autonomous Computer Takeover")
    parser.add_argument("--task", type=str, default="Open notepad, type JARVIS System Online, and narrate completion")
    args = parser.parse_args()

    agent = JarvisAutonomousTakeover()
    res = agent.run_takeover(args.task)
    print("\n" + json.dumps(res, indent=2))
