#!/usr/bin/env python3
"""
JARVIS Unified Master CLI — v2.2.0 Complete Empire Edition.
The central command center for AI Arrow, Autonomous Desktop Takeover, SoM Grounding,
Voice Note Invoicing, Mem0 Persistent Memory, TARS/SPARK AI Employees, Chrome CDP, and Phone Assistant.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_arrow import show_ai_arrow, show_ai_arrow_by_query
from jarvis_brain import JarvisBrain
from jarvis_browser import JarvisBrowserBridge
from jarvis_employees import SPARKEmployee, TARSEmployee
from jarvis_invoice import JarvisInvoiceEngine
from jarvis_kokoro import get_neural_voice
from jarvis_memory import get_memory
from jarvis_phone import JarvisPhoneAssistant
from jarvis_som import get_som
from jarvis_takeover import JarvisAutonomousTakeover
from jarvis_telegram import JarvisTelegramBridge
from jarvis_vision import get_vision
from jarvis_voice import get_voice


def print_banner():
    banner = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
  Autonomous Computer-Control & Multi-Modal Copilot (v2.2.0)
    """
    print(banner)
    print("=" * 68)


def interactive_menu():
    print_banner()
    voice = get_neural_voice()
    voice.speak("Welcome back, sir. JARVIS 2.2 Complete Empire Systems are online.")

    while True:
        print("\n[JARVIS MASTER COMMAND MENU]")
        print("  1. 🎯 AI Arrow Guidance ('Where Do I Click?')")
        print("  2. 🤖 Full Autonomous Desktop Takeover")
        print("  3. 📑 Voice Note to Instant Invoice (PDF/HTML)")
        print("  4. 💼 TARS AI: Generate 3-Tier Client Proposal")
        print("  5. ⚡ SPARK AI: 1-Click Content Explosion (1 -> 15+ Assets)")
        print("  6. 🏷️ Set-of-Marks (SoM) Numbered UI Visualizer")
        print("  7. 🧠 Mem0 Persistent Long-Term Memory & Profile")
        print("  8. 📱 Start Telegram Mobile Voice Bridge")
        print("  9. 🌐 Chrome Zero-Login CDP Browser Controller")
        print(" 10. 📞 AI Telephony & Inbound Phone Assistant")
        print(" 11. 🎙️ Hands-Free Voice Assistant (Continuous Wake Word)")
        print(" 12. 👁️ Screen Vision Perception (Describe Active Screen)")
        print(" 13. 🚀 Launch Live Web HUD (Port 6970)")
        print("  0. ❌ Exit JARVIS")

        try:
            choice = input("\nSelect an option (0-13): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting JARVIS. Goodbye, sir.")
            break

        if choice == "1":
            q = input("What button or element would you like me to point to? ").strip()
            if q:
                show_ai_arrow_by_query(q, mode="guide")

        elif choice == "2":
            task = input("Enter autonomous goal / task: ").strip()
            if task:
                agent = JarvisAutonomousTakeover()
                agent.run_takeover(task)

        elif choice == "3":
            prompt = input("Enter invoice details (or voice note text): ").strip()
            if prompt:
                inv = JarvisInvoiceEngine()
                inv.process_voice_note_to_invoice(prompt)

        elif choice == "4":
            client = input("Enter client name [Stark Industries]: ").strip() or "Stark Industries"
            scope = input("Enter requested scope [Autonomous AI Copilot Deployment]: ").strip() or "Autonomous AI Copilot Deployment"
            tars = TARSEmployee()
            tars.generate_proposal(client, scope)

        elif choice == "5":
            topic = input("Enter core topic to explode [I Gave JARVIS Full Control of My Computer]: ").strip() or "I Gave JARVIS Full Control of My Computer"
            spark = SPARKEmployee()
            spark.explode_content(topic)

        elif choice == "6":
            som = get_som()
            shot_path, _ = som.vision.capture_screen("som_interactive.png")
            out_path, _, emap = som.generate_som_overlay(shot_path)
            print(f"[+] SoM Overlay Generated: {out_path} ({len(emap)} tagged UI elements)")
            os.system(f'start "" "{out_path}"')

        elif choice == "7":
            mem = get_memory()
            print("\n=== USER PROFILE & PERSISTENT FACTS ===")
            for k, v in mem.get_profile().items():
                print(f"  • {k}: {v}")
            sq = input("\nEnter query to search memories (or Enter to skip): ").strip()
            if sq:
                res = mem.search_memories(sq)
                print(f"[+] Found {len(res)} memories for '{sq}':")
                for m in res:
                    print(f"    - [{m['category']}] {m['content']}")

        elif choice == "8":
            bridge = JarvisTelegramBridge()
            bridge.poll_updates()

        elif choice == "9":
            browser = JarvisBrowserBridge()
            if not browser.is_chrome_cdp_active():
                browser.launch_chrome_with_cdp()
            print(f"[+] Chrome CDP active on port {browser.cdp_port}")
            url = input("Enter URL to navigate to (or press Enter for Meta Ads): ").strip()
            if url:
                browser.open_url(url)
            else:
                browser.automate_meta_ad_campaign()

        elif choice == "10":
            phone = JarvisPhoneAssistant()
            name = input("Enter caller name [Bruce Wayne]: ").strip() or "Bruce Wayne"
            inquiry = input("Enter inquiry [What AI automation services do you provide?]: ").strip() or "What AI automation services do you provide?"
            phone.handle_incoming_call_simulation(name, "+1 (555) 019-2834", inquiry)

        elif choice == "11":
            print("[+] Starting continuous voice listening. Say 'Jarvis' followed by your command.")
            def on_voice_command(cmd: str):
                print(f"[!] Voice: '{cmd}'")
                if "invoice" in cmd or "bill" in cmd:
                    JarvisInvoiceEngine().process_voice_note_to_invoice(cmd)
                elif "proposal" in cmd:
                    TARSEmployee().generate_proposal("Prospective Client", cmd)
                elif "content" in cmd or "explode" in cmd:
                    SPARKEmployee().explode_content(cmd)
                elif "where" in cmd or "click" in cmd or "arrow" in cmd:
                    show_ai_arrow_by_query(cmd, mode="guide")
                elif "take over" in cmd or "open" in cmd:
                    JarvisAutonomousTakeover().run_takeover(cmd)
                else:
                    ans = JarvisBrain().ask_second_brain(cmd)
                    voice.speak(ans)

            get_voice().continuous_listen(on_voice_command, wake_word="jarvis")

        elif choice == "12":
            vis = get_vision()
            _, shot_b64 = vis.capture_screen("cli_describe.png")
            desc = vis.describe_screen(shot_b64)
            print(f"\n[JARVIS Screen Analysis]:\n{desc}")
            voice.speak("Screen analysis complete.")

        elif choice == "13":
            print("[+] Starting JARVIS Web HUD on http://127.0.0.1:6970 ...")
            subprocess.Popen([sys.executable, str(JARVIS_DIR / "web_hud" / "server.py")], shell=True)
            import webbrowser
            time.sleep(1.5)
            webbrowser.open("http://127.0.0.1:6970")

        elif choice == "0":
            print("Shutting down JARVIS. Have a productive day, sir.")
            break


def main():
    parser = argparse.ArgumentParser(description="JARVIS Autonomous AI Copilot")
    subparsers = parser.add_subparsers(dest="command")

    # Arrow
    p_arrow = subparsers.add_parser("arrow", help="Locate and point AI arrow at UI element")
    p_arrow.add_argument("query", type=str, help="Element description")
    p_arrow.add_argument("--mode", choices=["guide", "takeover"], default="guide")

    # Takeover
    p_takeover = subparsers.add_parser("takeover", help="Autonomous desktop takeover")
    p_takeover.add_argument("task", type=str, help="Goal description")

    # Invoice
    p_inv = subparsers.add_parser("invoice", help="Generate PDF/HTML invoice from prompt")
    p_inv.add_argument("prompt", type=str, help="Invoice details")

    # TARS
    p_tars = subparsers.add_parser("tars", help="TARS 3-Tier Proposal Generator")
    p_tars.add_argument("client", type=str, help="Client name")
    p_tars.add_argument("--scope", type=str, default="AI Agency Automation")

    # SPARK
    p_spark = subparsers.add_parser("spark", help="SPARK Content Explosion Engine")
    p_spark.add_argument("topic", type=str, help="Core topic to explode")

    # SoM
    subparsers.add_parser("som", help="Generate Set-of-Marks element overlay")

    # Memory
    p_mem = subparsers.add_parser("memory", help="Query or add to Mem0 persistent memory")
    p_mem.add_argument("--query", type=str, default=None)
    p_mem.add_argument("--add", type=str, default=None)

    # Telegram
    subparsers.add_parser("telegram", help="Start Telegram mobile bridge daemon")

    # Browser
    subparsers.add_parser("browser", help="Launch and control Chrome via CDP")

    # Phone
    subparsers.add_parser("phone", help="Simulate AI telephony call")

    # Voice
    subparsers.add_parser("voice", help="Start continuous hands-free voice assistant")

    # Describe
    subparsers.add_parser("describe", help="Visually describe active screen")

    # HUD
    subparsers.add_parser("hud", help="Launch JARVIS Web HUD")

    args = parser.parse_args()

    if not args.command:
        interactive_menu()
        return

    if args.command == "arrow":
        show_ai_arrow_by_query(args.query, mode=args.mode)
    elif args.command == "takeover":
        JarvisAutonomousTakeover().run_takeover(args.task)
    elif args.command == "invoice":
        JarvisInvoiceEngine().process_voice_note_to_invoice(args.prompt)
    elif args.command == "tars":
        TARSEmployee().generate_proposal(args.client, args.scope)
    elif args.command == "spark":
        SPARKEmployee().explode_content(args.topic)
    elif args.command == "som":
        som = get_som()
        p, _ = som.vision.capture_screen()
        out, _, _ = som.generate_som_overlay(p)
        print(f"[+] SoM Output: {out}")
    elif args.command == "memory":
        mem = get_memory()
        if args.add:
            mem.add_memory(args.add)
        elif args.query:
            res = mem.search_memories(args.query)
            for m in res:
                print(f"• [{m['category']}] {m['content']}")
    elif args.command == "telegram":
        JarvisTelegramBridge().poll_updates()
    elif args.command == "browser":
        JarvisBrowserBridge().launch_chrome_with_cdp()
    elif args.command == "phone":
        JarvisPhoneAssistant().handle_incoming_call_simulation("Test Caller", "+1 555 019 2834", "Pricing inquiry")
    elif args.command == "voice":
        get_voice().continuous_listen(lambda cmd: print(f"Command: {cmd}"), wake_word="jarvis")
    elif args.command == "describe":
        vis = get_vision()
        _, b64 = vis.capture_screen()
        print(vis.describe_screen(b64))
    elif args.command == "hud":
        os.system(f'python "{JARVIS_DIR / "web_hud" / "server.py"}"')


if __name__ == "__main__":
    main()
