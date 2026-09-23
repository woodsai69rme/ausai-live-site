#!/usr/bin/env python3
"""
JARVIS Fast Hybrid Memory & RAG Engine.
Indexes content vault, agency campaigns, and session knowledge into an optimized SQLite FTS5 database
for sub-5ms contextual recall across all AI employees and War Room endpoints.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
DB_PATH = JARVIS_DIR / "core" / "jarvis_fast_rag.db"


class JarvisFastRAG:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS rag_documents USING fts5(
                    filepath UNINDEXED,
                    filename,
                    category,
                    content,
                    tokenize='porter unicode61'
                )
            """)
            conn.commit()

    def ingest_directories(self, dirs: List[Path]) -> int:
        count = 0
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM rag_documents")
            for d in dirs:
                if not d.exists():
                    continue
                for f in d.rglob("*.md"):
                    try:
                        text = f.read_text(encoding="utf-8", errors="ignore")
                        cat = d.name
                        conn.execute(
                            "INSERT INTO rag_documents (filepath, filename, category, content) VALUES (?, ?, ?, ?)",
                            (str(f), f.name, cat, text)
                        )
                        count += 1
                    except Exception:
                        pass
            conn.commit()
        return count

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        clean_q = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
        if not clean_q:
            return []

        results = []
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT filepath, filename, category, snippet(rag_documents, 3, '<b>', '</b>', '...', 25) as snippet,
                       rank
                FROM rag_documents
                WHERE rag_documents MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (f"{clean_q}*", limit)).fetchall()
            for r in rows:
                results.append(dict(r))
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Fast RAG Engine")
    parser.add_argument("--ingest", action="store_true", help="Ingest all content vault and agency folders")
    parser.add_argument("--query", type=str, help="Search memory database")
    args = parser.parse_args()

    rag = JarvisFastRAG()
    if args.ingest:
        target_dirs = [
            JARVIS_DIR / "content_vault",
            JARVIS_DIR / "agency_offerings",
            Path(r"C:\Users\karma\MEMORY")
        ]
        indexed_count = rag.ingest_directories(target_dirs)
        print(f"[✓] Fast RAG Ingestion Complete: Indexed {indexed_count} documents into SQLite FTS5 database.")
    elif args.query:
        hits = rag.search(args.query)
        print(f"[+] Search Results for: \"{args.query}\" ({len(hits)} hits):")
        for h in hits:
            print(f" • [{h['category']}] {h['filename']} -> {h['snippet']}")
    else:
        print("[+] JARVIS Fast RAG Ready. Use --ingest or --query <term>.")
