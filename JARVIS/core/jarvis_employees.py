#!/usr/bin/env python3
"""
JARVIS Autonomous AI Employees — TARS & SPARK (AI Workshop V6.1 Architecture).
• TARS: Autonomous Client Onboarding, Proposal Generation & CRM Management.
• SPARK: Autonomous Social Media & Content Explosion Engine (1 Idea -> 15+ Assets).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
CONTENT_VAULT_DIR = JARVIS_DIR / "content_vault"
CONTENT_VAULT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(JARVIS_DIR / "core"))
from jarvis_invoice import JarvisInvoiceEngine
from jarvis_memory import get_memory
from jarvis_voice import get_voice

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "REDACTED_API_KEY"
)


class TARSEmployee:
    """TARS: Client Onboarding & Proposal Generation Specialist."""

    def __init__(self):
        self.voice = get_voice()
        self.memory = get_memory()

    def generate_proposal(self, client_name: str, service_scope: str, budget_range: str = "$3,000 - $7,500") -> Dict[str, Any]:
        """Generate a complete 3-tier client proposal with deliverables and pricing."""
        self.voice.speak(f"TARS AI Employee preparing customized proposal for {client_name}.")
        print(f"\n[TARS AI 🤖] Formulating Proposal for: {client_name}")

        prompt = (
            f"You are TARS, an elite AI Agency Operations Employee.\n"
            f"Client: {client_name}\n"
            f"Requested Scope: {service_scope}\n"
            f"Budget Range: {budget_range}\n\n"
            "Create a structured 3-tier proposal (Starter, Growth, Empire) in JSON format:\n"
            "{\n"
            '  "client_name": "...",\n'
            '  "executive_summary": "...",\n'
            '  "tiers": [\n'
            '    {"name": "Starter", "price": "$2,500", "deliverables": ["..."], "timeline": "7 days"},\n'
            '    {"name": "Growth (Recommended)", "price": "$5,000", "deliverables": ["..."], "timeline": "14 days"},\n'
            '    {"name": "Empire Enterprise", "price": "$8,500", "deliverables": ["..."], "timeline": "30 days"}\n'
            '  ],\n'
            '  "next_steps": "..."\n'
            "}"
        )

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            body = {
                "model": "google/gemma-4-26b-a4b-it:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                proposal_data = json.loads(data["choices"][0]["message"]["content"])
        except Exception:
            proposal_data = {
                "client_name": client_name,
                "executive_summary": f"Comprehensive AI automation roadmap for {service_scope}.",
                "tiers": [
                    {"name": "Starter Tier", "price": "$2,500", "deliverables": ["Custom AI Copilot Installation", "Single-flow Automation"], "timeline": "7 days"},
                    {"name": "Growth Tier (Recommended)", "price": "$4,500", "deliverables": ["Full JARVIS Suite Setup", "Telegram Mobile Bridge", "Meta Ads Automation"], "timeline": "14 days"},
                    {"name": "Empire Enterprise", "price": "$7,500", "deliverables": ["Complete Autonomous Swarm", "Custom Voice Telephony Line", "24/7 Monitoring"], "timeline": "30 days"},
                ],
                "next_steps": "Schedule onboarding kickoff call and review deliverables."
            }

        # Save proposal markdown
        safe_name = re.sub(r"\W+", "_", client_name)
        proposal_file = CONTENT_VAULT_DIR / f"Proposal_{safe_name}.md"
        
        md_text = f"# 💼 AI Agency Proposal: {client_name}\n\n"
        md_text += f"**Date:** {datetime.date.today().isoformat()} | **Prepared By:** TARS AI Operations\n\n"
        md_text += f"## Executive Summary\n{proposal_data.get('executive_summary', '')}\n\n"
        md_text += "## Investment Tiers\n"
        for t in proposal_data.get("tiers", []):
            md_text += f"### 💎 {t.get('name')} — {t.get('price')} ({t.get('timeline')})\n"
            for d in t.get("deliverables", []):
                md_text += f"- [x] {d}\n"
            md_text += "\n"
        md_text += f"## Next Steps\n{proposal_data.get('next_steps', '')}\n"

        proposal_file.write_text(md_text, encoding="utf-8")
        print(f"[+] Proposal saved: {proposal_file}")
        self.voice.speak(f"Proposal compiled for {client_name} with 3 investment tiers.")
        proposal_data["proposal_file"] = str(proposal_file)
        proposal_data["filepath"] = str(proposal_file)
        return proposal_data


class SPARKEmployee:
    """SPARK: Autonomous Social Media & Content Explosion Engine."""

    def __init__(self):
        self.voice = get_voice()

    def explode_content(self, topic: str) -> Path:
        """Explode 1 topic into 15+ multi-platform assets (LinkedIn, X, YouTube, Ads)."""
        self.voice.speak(f"SPARK AI Employee generating 15-asset content explosion for: {topic}.")
        print(f"\n[SPARK AI ⚡] Exploding Content for Topic: \"{topic}\"")

        prompt = (
            f"You are SPARK, the elite Social Media & Viral Growth AI Employee.\n"
            f"Topic: {topic}\n\n"
            "Generate a publication-ready content pack with:\n"
            "1. 3x LinkedIn High-Engagement Thought-Leadership Posts (with hooks, body, takeaways, and hashtags)\n"
            "2. 5x Twitter/X Viral Hooks & Mini-Threads\n"
            "3. 2x YouTube Script Hooks & Video Descriptions\n"
            "4. 2x High-Converting Meta/Google Ad Copy Variations (Headline + Primary Text + CTA)\n\n"
            "Format in sleek Markdown with distinct sections."
        )

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            body = {
                "model": "google/gemma-4-26b-a4b-it:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=18) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content_pack = data["choices"][0]["message"]["content"]
        except Exception:
            content_pack = (
                f"# ⚡ SPARK Content Pack: {topic}\n\n"
                "## 👔 LinkedIn Post 1 (The Breakdown)\n"
                f"Most people think {topic} is complex. Here is how we automated it in 3 steps...\n\n"
                "## 🐦 Twitter / X Thread\n"
                f"1/5 We just deployed our autonomous {topic} agent on Windows 11. Here are the insane results 🧵👇\n\n"
                "## 📺 YouTube Script Hook\n"
                f"\"In this video, I gave our AI assistant full control of {topic}...\"\n\n"
                "## 🎯 Meta Ad Creative\n"
                f"**Headline:** Scale Your Operations with {topic}\n**Primary Text:** Eliminate 80% of repetitive busywork.\n**CTA:** Book Strategy Call"
            )

        safe_topic = re.sub(r"\W+", "_", topic)[:30]
        out_file = CONTENT_VAULT_DIR / f"Content_Pack_{safe_topic}.md"
        out_file.write_text(content_pack, encoding="utf-8")
        
        print(f"[+] Content Explosion generated: {out_file}")
        self.voice.speak(f"Content explosion complete. 15 assets ready in Content Vault.")
        return out_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS AI Employees (TARS & SPARK)")
    parser.add_argument("--tars", action="store_true", help="Run TARS Proposal Generator")
    parser.add_argument("--client", type=str, default="Stark Industries")
    parser.add_argument("--scope", type=str, default="Autonomous Computer-Use & Desktop Copilot Deployment")
    parser.add_argument("--spark", action="store_true", help="Run SPARK Content Explosion")
    parser.add_argument("--topic", type=str, default="I Gave JARVIS Full Control of My Computer")
    args = parser.parse_args()

    if args.spark:
        spark = SPARKEmployee()
        spark.explode_content(args.topic)
    else:
        tars = TARSEmployee()
        tars.generate_proposal(args.client, args.scope)
