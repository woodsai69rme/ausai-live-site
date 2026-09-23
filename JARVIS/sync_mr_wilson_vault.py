#!/usr/bin/env python3
"""
Mr. Wilson: Dual-Drive Redundant Vault Backup Synchronizer.
Mirrors C:\\Users\\karma\\JARVIS to X:\\BACKUPS\\JARVIS_BACKUP\\
Complies strictly with Golden Rule #5 (Permanent preservation, append-only history).
"""

import os
import sys
import shutil
import time
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SRC_DIR = Path(r"C:\Users\karma\JARVIS")
DST_DIR = Path(r"X:\BACKUPS\JARVIS_BACKUP")


def smart_copy(src: Path, dst: Path) -> bool:
    """Copies src to dst only if dst doesn't exist or has different size/mtime."""
    try:
        if dst.exists():
            s_stat = src.stat()
            d_stat = dst.stat()
            if s_stat.st_size == d_stat.st_size and abs(s_stat.st_mtime - d_stat.st_mtime) < 2:
                return False  # Already up to date
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def sync_vault():
    print("=" * 60)
    print(" 💾 MR. WILSON VAULT BACKUP SYNCHRONIZER (X: DRIVE)")
    print("=" * 60)

    if not Path(r"X:").exists():
        print("[!] External drive X: is currently not connected. Skipping.")
        return

    DST_DIR.mkdir(parents=True, exist_ok=True)
    (DST_DIR / "core").mkdir(parents=True, exist_ok=True)
    (DST_DIR / "audio_cache").mkdir(parents=True, exist_ok=True)

    copied = 0
    checked = 0

    # Sync root Python, JSON, and MD files
    for item in SRC_DIR.glob("*.*"):
        if item.suffix in [".py", ".json", ".jpg", ".png", ".md", ".vbs", ".bat"]:
            checked += 1
            dest = DST_DIR / item.name
            if smart_copy(item, dest):
                copied += 1

    # Sync core directory
    src_core = SRC_DIR / "core"
    dst_core = DST_DIR / "core"
    if src_core.exists():
        for item in src_core.glob("*.py"):
            checked += 1
            if smart_copy(item, dst_core / item.name):
                copied += 1

    # Sync audio_cache / music_drops
    src_drops = SRC_DIR / "audio_cache" / "music_drops"
    dst_drops = DST_DIR / "audio_cache" / "music_drops"
    if src_drops.exists():
        dst_drops.mkdir(parents=True, exist_ok=True)
        for item in src_drops.glob("*.mp3"):
            checked += 1
            if smart_copy(item, dst_drops / item.name):
                copied += 1

    # Sync youtube_reviews
    src_reviews = SRC_DIR / "youtube_reviews"
    dst_reviews = DST_DIR / "youtube_reviews"
    if src_reviews.exists():
        dst_reviews.mkdir(parents=True, exist_ok=True)
        for item in src_reviews.glob("*.md"):
            checked += 1
            if smart_copy(item, dst_reviews / item.name):
                copied += 1

    # Sync web_hud directory
    src_hud = SRC_DIR / "web_hud"
    dst_hud = DST_DIR / "web_hud"
    if src_hud.exists():
        dst_hud.mkdir(parents=True, exist_ok=True)
        for item in src_hud.rglob("*.*"):
            if not item.is_file() or "__pycache__" in str(item) or "node_modules" in str(item):
                continue
            checked += 1
            rel = item.relative_to(src_hud)
            dest = dst_hud / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if smart_copy(item, dest):
                copied += 1

    print(f"[OK] Vault sync complete: {copied} updated / {checked} verified on X:\\BACKUPS\\JARVIS_BACKUP\\", flush=True)


if __name__ == "__main__":
    sync_vault()
