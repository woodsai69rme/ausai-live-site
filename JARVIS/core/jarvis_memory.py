#!/usr/bin/env python3
"""
JARVIS Persistent Memory Layer — Mem0 & State-of-the-Art Cross-Session Memory Engine.
Provides continuous user preference learning, factual extraction, cross-session recall,
and hybrid semantic retrieval using SQLite.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
DB_PATH = JARVIS_DIR / "jarvis_memory.db"

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "REDACTED_API_KEY"
)


class JarvisMemoryEngine:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_database()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initialize SQLite schema for memories, facts, and session logs."""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT DEFAULT 'general',
                    content TEXT NOT NULL,
                    source TEXT DEFAULT 'chat',
                    importance INTEGER DEFAULT 1,
                    access_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mission_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

        # Seed initial core knowledge if empty
        self._seed_default_profile()

    def _seed_default_profile(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM user_profile")
            if cur.fetchone()[0] == 0:
                defaults = [
                    ("user_name", "Commander Karma"),
                    ("role", "AI Agency & Systems Architect"),
                    ("hardware", "NVIDIA RTX 4060 8GB VRAM / 64GB DDR4 RAM"),
                    ("core_company", "JARVIS AI Automations"),
                    ("primary_currency", "USD ($)"),
                    ("default_hourly_rate", "$150/hr"),
                    ("standard_invoice_terms", "Net 14 Days"),
                ]
                cur.executemany("INSERT INTO user_profile (key, value) VALUES (?, ?)", defaults)
                conn.commit()

    def add_memory(self, content: str, category: str = "general", source: str = "interaction", importance: int = 1):
        """Save a new memory unit into the database."""
        clean = content.strip()
        if not clean:
            return

        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO memories (category, content, source, importance) VALUES (?, ?, ?, ?)",
                (category, clean, source, importance)
            )
            conn.commit()
        print(f"[+] Memory stored [{category}]: \"{clean[:60]}...\"")

    def log_mission(self, task: str, status: str = "SUCCESS", details: str = ""):
        """Record an autonomous takeover or automation task."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO mission_logs (task, status, details) VALUES (?, ?, ?)",
                (task, status, details)
            )
            conn.commit()

    def set_profile_fact(self, key: str, value: str):
        """Update or insert a key-value fact into user profile."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO user_profile (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                (key, value)
            )
            conn.commit()

    def get_profile(self) -> Dict[str, str]:
        """Fetch all facts in user profile."""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT key, value FROM user_profile").fetchall()
            return {r["key"]: r["value"] for r in rows}

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search combining keyword frequency and category scoring."""
        q_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
        if not q_terms:
            q_terms = [query.lower()]

        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM memories ORDER BY id DESC LIMIT 100").fetchall()
            
            scored_results = []
            for r in rows:
                content = r["content"].lower()
                category = r["category"].lower()
                
                # Term matching score
                matches = sum(1 for term in q_terms if term in content or term in category)
                if matches > 0:
                    score = matches * r["importance"] + (r["access_count"] * 0.1)
                    scored_results.append((score, dict(r)))

            # Sort by highest score
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            # Increment access count
            top_items = [item for _, item in scored_results[:limit]]
            for item in top_items:
                conn.execute("UPDATE memories SET access_count = access_count + 1 WHERE id = ?", (item["id"],))
            conn.commit()

            return top_items

    def synthesize_context(self, current_task: str) -> str:
        """Compile a concise contextual briefing for LLM prompts."""
        profile = self.get_profile()
        profile_str = "\n".join([f"• {k}: {v}" for k, v in profile.items()])
        
        relevant_mems = self.search_memories(current_task, limit=4)
        mem_str = "\n".join([f"• [{m['category']}] {m['content']}" for m in relevant_mems]) if relevant_mems else "• None"

        return f"=== USER PROFILE ===\n{profile_str}\n\n=== RELEVANT MEMORIES ===\n{mem_str}"


_memory_instance: Optional[JarvisMemoryEngine] = None

def get_memory() -> JarvisMemoryEngine:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = JarvisMemoryEngine()
    return _memory_instance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Mem0 Memory Engine")
    parser.add_argument("--add", type=str, default=None, help="Add memory")
    parser.add_argument("--category", type=str, default="general")
    parser.add_argument("--search", type=str, default=None, help="Search memory")
    parser.add_argument("--profile", action="store_true", help="Print user profile")
    args = parser.parse_args()

    mem = get_memory()
    if args.add:
        mem.add_memory(args.add, category=args.category)
    elif args.search:
        res = mem.search_memories(args.search)
        print(f"[+] Found {len(res)} memories for '{args.search}':")
        for m in res:
            print(f"  • [{m['category']}] {m['content']}")
    elif args.profile:
        print("[+] User Profile:")
        for k, v in mem.get_profile().items():
            print(f"  {k}: {v}")
    else:
        print(mem.synthesize_context("General Assistant Query"))
