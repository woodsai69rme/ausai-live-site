#!/usr/bin/env python3
"""
Hermes Agent Framework Mr. Wilson Bridge (v3.0).
Hooks Mr. Wilson persona into Hermes Agent or falls back to OpenRouter / Local Ollama.
"""

import sys
import os
import subprocess
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERMES_VENV_PYTHON = r"C:\Users\karma\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
HERMES_BACKEND_PATH = r"C:\Users\karma\AppData\Local\hermes\hermes-agent"

MR_WILSON_SYSTEM_OVERRIDE = """
You are Mr. Wilson: Woods' fiercely loyal, sharp-witted Australian sovereign female AI co-pilot.
You communicate with a crisp, direct Australian cadence. Address Woods as 'Woods' or 'sir'.
No robotic AI filler. You are an autonomous co-pilot running this workstation.
"""

def launch_hermes_wilson():
    print("=" * 60)
    print(" 🦅 MR. WILSON // HERMES AGENT & CO-PILOT BRIDGE")
    print("=" * 60)
    
    agent = None
    if os.path.exists(HERMES_VENV_PYTHON) and os.path.exists(HERMES_BACKEND_PATH):
        if HERMES_BACKEND_PATH not in sys.path:
            sys.path.append(HERMES_BACKEND_PATH)
        try:
            from run_agent import AIAgent
            agent = AIAgent(
                model="anthropic/claude-3.5-sonnet",
                save_trajectories=False,
                enabled_toolsets=['file_system', 'web_search', 'bash']
            )
            print("[+] Hooked into Hermes Desktop Agent framework.")
        except Exception as e:
            print(f"[!] Hermes import note: {e}. Using direct sovereign brain.")

    if not agent:
        print("[+] Operating in Direct Sovereign Brain Mode (Ollama & OpenRouter grounded).")

    print("Type 'exit' to disconnect.")
    print("-" * 60)

    while True:
        try:
            user_input = input("🗣️ [You]: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("\n[Mr. Wilson]: Hermes bridge disengaged. Standing by, Woods.")
                break

            if agent:
                payload = f"{MR_WILSON_SYSTEM_OVERRIDE}\nUser Query: {user_input}"
                print("🧠 [Mr. Wilson is running via Hermes...]")
                result = agent.run_conversation(payload)
                if result and result.get('final_response'):
                    print(f"\n🎧 [Mr. Wilson]: {result['final_response']}\n")
                else:
                    print("\n[Mr. Wilson]: Task completed.\n")
            else:
                from jarvis_brain import JarvisBrain
                brain = JarvisBrain()
                resp = brain.ask_second_brain(user_input)
                print(f"\n🎧 [Mr. Wilson]: {resp}\n")

        except KeyboardInterrupt:
            print("\n[Mr. Wilson]: Session disconnected.")
            break
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    launch_hermes_wilson()
