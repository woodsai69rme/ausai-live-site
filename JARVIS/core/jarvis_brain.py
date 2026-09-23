#!/usr/bin/env python3
"""
JARVIS Brain & Workspace Operations Engine — Second Brain, Agenda & Local Knowledge.
Indexes markdown documents, memory transcripts, active project catalogs, and schedules tasks.
Supports OpenRouter with local Ollama offline fallback.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
KNOWLEDGE_ROOTS = [
    Path(r"C:\Users\karma\MEMORY"),
    Path(r"C:\Users\karma"),
    Path(r"C:\Users\karma\ACTIVE_PROJECTS"),
    Path(r"C:\Users\karma\ATO_TAX_COMPLIANCE"),
    Path(r"C:\WOODATO"),
    Path(r"C:\Users\karma\aigf"),
    Path(r"C:\Users\karma\.agents"),
]

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "REDACTED_API_KEY"
)


class JarvisBrain:
    def __init__(self):
        self.agenda_file = JARVIS_DIR / "agenda.json"
        self._init_agenda()

    def _init_agenda(self):
        if not self.agenda_file.exists():
            default_agenda = {
                "tasks": [
                    {"id": 1, "title": "Launch Mr. Wilson Autonomous Copilot", "priority": "HIGH", "completed": True},
                    {"id": 2, "title": "Verify AI Arrow Visual Guidance Overlay", "priority": "HIGH", "completed": True},
                    {"id": 3, "title": "Maintain ATO $0 Net Liability Shelter", "priority": "HIGH", "completed": True},
                    {"id": 4, "title": "Monitor Crypto Whale Radar on Port 8088", "priority": "HIGH", "completed": True},
                ],
                "events": [
                    {"time": "09:00", "title": "Daily AI Empire Standup & Mission Review"},
                    {"time": "14:00", "title": "Workstation Optimization & Alpha Monitoring"},
                ]
            }
            self.agenda_file.write_text(json.dumps(default_agenda, indent=2), encoding="utf-8")

    def search_second_brain(self, query: str, max_results: int = 6) -> List[Dict[str, Any]]:
        """Search local documents, notes, markdown files, and memory catalogs recursively."""
        results = []
        q_lower = query.lower()
        terms = q_lower.split()

        scanned = 0
        for root in KNOWLEDGE_ROOTS:
            if not root.exists():
                continue
            
            # Search both .md and .txt files
            candidates = list(root.glob("*.md")) + list(root.glob("*.txt"))
            # If in MEMORY, search all files
            if "MEMORY" in str(root):
                candidates.extend(list(root.rglob("*.md")))

            for doc_file in candidates:
                if not doc_file.is_file():
                    continue
                scanned += 1
                if scanned > 150:
                    break
                try:
                    text = doc_file.read_text(encoding="utf-8", errors="ignore")
                    if q_lower in text.lower() or any(term in text.lower() for term in terms if len(term) > 3):
                        pos = text.lower().find(q_lower)
                        if pos == -1:
                            for term in terms:
                                pos = text.lower().find(term)
                                if pos != -1:
                                    break
                        if pos == -1:
                            pos = 0
                        start = max(0, pos - 100)
                        end = min(len(text), pos + 350)
                        snippet = text[start:end].replace("\n", " ").strip()
                        results.append({
                            "file": str(doc_file),
                            "name": doc_file.name,
                            "snippet": f"...{snippet}...",
                        })
                        if len(results) >= max_results:
                            return results
                except Exception:
                    continue

        return results

    def get_agenda_summary(self) -> str:
        """Return formatted summary of daily tasks and calendar events."""
        try:
            data = json.loads(self.agenda_file.read_text(encoding="utf-8"))
            tasks = data.get("tasks", [])
            events = data.get("events", [])
            
            lines = [f"📅 MR. WILSON DAILY BRIEFING ({datetime.date.today().strftime('%B %d, %Y')}):"]
            lines.append("\nUpcoming Schedule:")
            for ev in events:
                lines.append(f"  • [{ev.get('time', 'ALL-DAY')}] {ev.get('title')}")
            
            lines.append("\nActive Tasks:")
            for t in tasks:
                status = "✅" if t.get("completed") else "⏳"
                lines.append(f"  {status} [{t.get('priority', 'NORMAL')}] {t.get('title')}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading agenda: {e}"

    def ask_second_brain(self, question: str) -> str:
        """Answer queries using second brain notes with OpenRouter and local Ollama failover."""
        docs = self.search_second_brain(question)
        context = "\n\n".join([f"Source [{d['name']}]: {d['snippet']}" for d in docs])
        
        prompt = (
            f"You are Mr. Wilson, Woods' loyal, sharp Australian female sovereign co-pilot.\n"
            f"Ground your answer in the user's workspace notes & second brain:\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Provide a concise, direct, professional Australian co-pilot answer addressed to Woods or sir. No robotic AI filler."
        )

        # 1. Try OpenRouter
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            body = {
                "model": "google/gemma-4-26b-a4b-it:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            pass

        # 2. Local Ollama Fallback (deepseek-r1:8b or qwen2.5-coder)
        try:
            ollama_url = "http://localhost:11434/api/chat"
            ollama_body = {
                "model": "deepseek-r1:8b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            req = urllib.request.Request(ollama_url, data=json.dumps(ollama_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                msg = data.get("message", {}).get("content", "").strip()
                if msg:
                    # Strip <think> tags if deepseek
                    msg = re.sub(r"<think>.*?</think>", "", msg, flags=re.DOTALL).strip()
                    return msg
        except Exception:
            pass

        # 3. Direct snippet synthesis fallback
        if docs:
            return f"According to your records in {docs[0]['name']}: {docs[0]['snippet']}"
        return "I've scanned your second brain and records, Woods, but found no matching entry for that query."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Second Brain Operations")
    parser.add_argument("--agenda", action="store_true")
    parser.add_argument("--query", type=str, default=None)
    args = parser.parse_args()

    brain = JarvisBrain()
    if args.agenda:
        print(brain.get_agenda_summary())
    elif args.query:
        print(f"[+] Query: {args.query}\n")
        print(brain.ask_second_brain(args.query))
    else:
        print(brain.get_agenda_summary())
