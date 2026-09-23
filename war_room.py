#!/usr/bin/env python3
"""war_room.py — operator CLI dispatcher for the WAR ROOM portal.

Companion to WAR_ROOM.md (canonical source-of-truth) and WAR_ROOM.html
(operator HUD). Subcommands mirror the 6 war-room tiles plus extras:

    python war_room.py status                # RSS-style health overview
    python war_room.py list                  # all tiles (terse table)
    python war_room.py info <tile>           # full record for one tile
    python war_room.py launch <tile>         # execute a one-click argv-list
    python war_room.py open [--public]       # open the HUD in default browser
    python war_room.py health                # live TCP probes (no browser)
    python war_room.py validate-mobile       # check MOBILE_FILTERED.csv dynamic tiles
    python war_room.py validate-tools        # check java/apktool/jadx install (3-case FOUND/NOT_FOUND/BROKEN)
    python war_room.py doctor [--json] [--quiet]   # aggregate workspace health check (7 sections)
    python war_room.py archive-outbox [--dry-run] [--keep-last N] [--category X] [--json]   # roll SLEEP_TRIPLE/outbox -> archive/outbox_YYYY-MM-DD/
    python war_room.py snapshot-doctor [--list] [--keep-last N] [--json]   # write .cache/war_room/snapshots/snapshot__DATE.json (cmd_doctor --json dump)
    python war_room.py diff-doctor --a <date-or-prefix> --b <date-or-prefix> [--json]   # compare two snapshots (status transitions per section)
    python war_room.py trend-compare [--a Nd] [--b Nd] [--json]   # compare per-section transition RATE (transitions/day) between two windows (MORE_FLAPPING / STABLE / MORE_STABLE per section)
    python war_room.py launch-trend-compare [--a Nd] [--b Nd] [--emit-report] [--alert-on-degraded] [--json]   # launch wrapper: run trend-compare, write outbox report, fanout alert if MORE_FLAPPING found

Stdlib-only (argparse, csv, io, json, os, re, shutil, socket, subprocess, sys, time, webbrowser, zipfile).
No external deps. Cross-platform; safe no-op on any non-Windows runner.

DESIGN:
    Every TILE_REGISTRY row now carries a canonical `argv: List[str]` list
    in addition to the human-readable `invocation` string. cmd_launch uses
    `subprocess.Popen(argv, shell=False)` — NO shell=True, NO shell-injection
    surface, even if a future contributor adds user-input-bearing tiles.

Designed under the Golden Rules: append, preserve, protect.
New tile rows are add-only; existing rows are never removed.
"""
import argparse
import csv
import os
import re
import shutil
import socket
import subprocess
import sys
import webbrowser
import zipfile
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

# Ensure stdout can print middle-dot / arrow glyphs on Windows cp1252.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# Canonical schema version stamped on every snapshot by cmd_snapshot_doctor (cont.15+).
# cmd_diff_doctor reads it back and warns on mismatch (MINOR #1 cont.16).
# Bump only if the snapshot payload SHAPE changes (new required fields, removed fields, etc.).
DOCTOR_SNAPSHOT_SCHEMA_VERSION = "war_room.doctor.snapshot/1"

# ============================================================
# TILE_REGISTRY — append-only; do not remove rows.
# Each tile carries:
#   - argv: canonical executable list — used by cmd_launch with shell=False
#   - invocation: human-readable string — printed by cmd_launch / cmd_info
# ============================================================

TILE_REGISTRY: Dict[str, Dict] = {
    # Tile #1 — STATUS (live health probe; not a launchable action)
    "status": {
        "category": "ops", "tier": "t1",
        "name": "Live Health Probe",
        "path": "5 local services (Ollama/ComfyUI/Archon/n8n/AI Army)",
        "invocation": "python war_room.py health  # CLI version",
        "argv": [sys.executable, "war_room.py", "health"],
        "notes": "TCP/HTTP probe · 1500ms timeout · 8s interval in HTML",
        "urls": [
            "http://127.0.0.1:11434/api/tags",
            "http://127.0.0.1:8188/system_stats",
            "http://127.0.0.1:8181/health",
            "http://127.0.0.1:5678/healthz",
            "http://127.0.0.1:8001/health",
        ],
    },

    # Tile #2 — ACTION (one-click ops rail) -- argv lists below
    "vs-code": {
        "category": "ops", "tier": "t1",
        "name": "Open VS Code",
        "path": "system install: 'code' registered for shells",
        "invocation": "code .",
        "argv": ["code", "."],
        "notes": "Opens current directory",
    },
    "ai-army": {
        "category": "ops", "tier": "t1",
        "name": "Start AI Army server",
        "path": r"C:\Users\karma\AI_ARMY\server.py",
        "invocation": r"python C:\Users\karma\AI_ARMY\server.py",
        "argv": [sys.executable, r"C:\Users\karma\AI_ARMY\server.py"],
        "notes": "Boot FastAPI app on :8001",
    },
    "mobile-recovery": {
        "category": "ops", "tier": "t1",
        "name": "Mobile Recovery Suite",
        "path": r"C:\Users\karma\recovery.bat (top-level shim)",
        "invocation": r"C:\Users\karma\recovery.bat",
        "argv": [r"C:\Users\karma\recovery.bat"],
        "notes": "12-position menu · 15/15 PASS tests",
    },
    "reality-audit": {
        "category": "ops", "tier": "t2",
        "name": "REALITY_VS_CLAIM_AUDIT",
        "path": r"C:\Users\karma\REALITY_VS_CLAIM_AUDIT.py",
        "invocation": "python REALITY_VS_CLAIM_AUDIT.py --run --emit-summary",
        "argv": [sys.executable, r"C:\Users\karma\REALITY_VS_CLAIM_AUDIT.py", "--run", "--emit-summary"],
        "notes": "Cross-checks master-index headlines vs on-disk reality",
    },
    "pc-scan": {
        "category": "ops", "tier": "t3",
        "name": "Re-scan PC apps",
        "path": r"C:\Users\karma\scan_pc_apps.ps1",
        "invocation": r"powershell -NoProfile -ExecutionPolicy Bypass -File scan_pc_apps.ps1",
        "argv": ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                 r"C:\Users\karma\scan_pc_apps.ps1"],
        "notes": "Writes RAW_PC_APPS_INVENTORY.csv",
    },
    "fleet-summary": {
        "category": "ops", "tier": "t1",
        "name": "Tool Kit fleet summary",
        "path": r"C:\Users\karma\tool_kit.py",
        "invocation": "python tool_kit.py list   # terse 4-col table",
        "argv": [sys.executable, r"C:\Users\karma\tool_kit.py", "list"],
        "notes": "Companion CLI dispatcher · 101 entries",
    },

    # Tile #3 — RECON (anti-scam intel; reference rows — no argv)
    "anti-scam-playbook": {
        "category": "recon", "tier": "t2",
        "name": "Anti-scam playbook",
        "path": r"C:\Users\karma\ANTI_SCAM_PLAYBOOK.md",
        "invocation": "(open in markdown viewer)",
        "argv": [],
        "notes": "Operator-curated · golden-rules append-only · TBD if missing",
    },
    "known-scammers": {
        "category": "recon", "tier": "t2",
        "name": "Known scammers index",
        "path": r"C:\Users\karma\KNOWN_SCAMMERS.md",
        "invocation": "(open in markdown viewer)",
        "argv": [],
        "notes": "Operator-controlled entries · closed-list schema · TBD if missing",
    },
    "contributor-profile": {
        "category": "recon", "tier": "t2",
        "name": "Contributor profile (operator-self)",
        "path": r"C:\Users\karma\CONTRIBUTOR_PROFILE.md",
        "invocation": "(open in markdown viewer)",
        "argv": [],
        "notes": "Operator-context for future sessions · TBD if missing",
    },

    # Tile #4 — EVIDENCE (chain-of-custody + audit logs)
    "index-delta": {
        "category": "evidence", "tier": "t2",
        "name": "INDEX_DELTA_SCANNER",
        "path": r"C:\Users\karma\INDEX_DELTA_SCANNER.py",
        "invocation": "python INDEX_DELTA_SCANNER.py --run",
        "argv": [sys.executable, r"C:\Users\karma\INDEX_DELTA_SCANNER.py", "--run"],
        "notes": "Top-level (1-deep) entry divergence",
    },
    "index-delta-recursive": {
        "category": "evidence", "tier": "t2",
        "name": "INDEX_DELTA_RECURSIVE",
        "path": r"C:\Users\karma\INDEX_DELTA_RECURSIVE.py",
        "invocation": "python INDEX_DELTA_RECURSIVE.py --run --max-depth 2",
        "argv": [sys.executable, r"C:\Users\karma\INDEX_DELTA_RECURSIVE.py", "--run", "--max-depth", "2"],
        "notes": "Where-inside the disk tree the divergence happens",
    },
    "master-reconciler": {
        "category": "evidence", "tier": "t2",
        "name": "MASTER_INDEX_RECONCILER",
        "path": r"C:\Users\karma\MASTER_INDEX_RECONCILER.py",
        "invocation": "python MASTER_INDEX_RECONCILER.py --run --emit-summary",
        "argv": [sys.executable, r"C:\Users\karma\MASTER_INDEX_RECONCILER.py", "--run", "--emit-summary"],
        "notes": "Aggregates 3 source logs into MASTER_INDEX_RECONCILED.md",
    },
    "backup-audit": {
        "category": "evidence", "tier": "t3",
        "name": "BACKUP_AUDIT_RUN",
        "path": r"C:\Users\karma\BACKUP_AUDIT_RUN.ps1",
        "invocation": "powershell BACKUP_AUDIT_RUN.ps1 -Run",
        "argv": ["powershell", r"C:\Users\karma\BACKUP_AUDIT_RUN.ps1", "-Run"],
        "notes": "Reads BACKUP_MANIFEST.json · 6-element status enum",
    },
    "hygiene-runner": {
        "category": "evidence", "tier": "t3",
        "name": "append-only hygiene runner",
        "path": r"C:\Users\karma\append_only_hygiene_runner.py",
        "invocation": "python append_only_hygiene_runner.py --run",
        "argv": [sys.executable, r"C:\Users\karma\append_only_hygiene_runner.py", "--run"],
        "notes": "12-log closed list · size + ts monotonic check",
    },

    # Tile #5 — COMMS (tunneled comms apps)
    "telegram": {
        "category": "comms", "tier": "t2",
        "name": "Telegram Desktop",
        "path": r"C:\Users\karma\AppData\Roaming\Telegram Desktop",
        "invocation": 'start "" "Telegram.exe"',
        "argv": ["start", "", "Telegram.exe"],
        "notes": "1 hit in PC scan · E2E DMs + channel reads",
    },
    "discord": {
        "category": "comms", "tier": "t2",
        "name": "Discord",
        "path": r"C:\Users\karma\AppData\Local\Discord (typical)",
        "invocation": 'start "" discord',
        "argv": ["start", "", "discord"],
        "notes": "Voice channels · community workspaces",
    },
    "slack": {
        "category": "comms", "tier": "t2",
        "name": "Slack",
        "path": r"C:\Users\karma\AppData\Local\slack (typical)",
        "invocation": 'start "" slack',
        "argv": ["start", "", "slack"],
        "notes": "Daily team comms",
    },
    "footclan-bridge": {
        "category": "comms", "tier": "t3",
        "name": "Voice PA ↔ Footclan bridge",
        "path": r"C:\Users\karma\voice_pa_bridge.py",
        "invocation": "python voice_pa_bridge.py --dry-run",
        "argv": [sys.executable, r"C:\Users\karma\voice_pa_bridge.py", "--dry-run"],
        "notes": "Cross-system correlator by iso-minute prefix match",
    },

    # Tile #6 — REFERENCE (cross-links; no argv — these open files in browser/editor)
    "ref-toolkit": {
        "category": "reference", "tier": "t1",
        "name": "AI & IT Toolkit (12 cats · 100 cards)",
        "path": r"C:\Users\karma\AI_AND_IT_TOOLKIT.html",
        "invocation": "(open in browser)",
        "argv": [],
        "notes": "Co-generated with WAR_ROOM via same 4-shape pattern",
    },
    "ref-grand": {
        "category": "reference", "tier": "t1",
        "name": "Grand Summary (START HERE)",
        "path": r"C:\Users\karma\GRAND_SUMMARY.md",
        "invocation": "(open in markdown viewer)",
        "argv": [],
        "notes": "One-page printable cheat",
    },
    "ref-workspace": {
        "category": "reference", "tier": "t1",
        "name": "Workspace master index (18 systems)",
        "path": r"C:\Users\karma\WORKSPACE_INDEX.md",
        "invocation": "(open in markdown viewer)",
        "argv": [],
        "notes": "Cross-system discoverability",
    },
    "ref-changelog": {
        "category": "reference", "tier": "t1",
        "name": "CHANGELOG.md",
        "path": r"C:\Users\karma\CHANGELOG.md",
        "invocation": "(open in markdown viewer)",
        "argv": [],
        "notes": "Append-only history · 2026-07-09 cont.6 = this WAR_ROOM",
    },
    # --- mobile (4 new tiles; wave-4 extension 2026-07-09) ---
    "adb": {
        "category": "mobile", "tier": "t1",
        "name": "adb devices (Android Debug Bridge)",
        "path": r"C:\Program Files\Google\Android\platform-tools\adb.exe  (or PATH)",
        "invocation": "adb devices  # list connected devices",
        "argv": ["adb", "devices"],
        "notes": "Daily-driver mobile ops · pair over USB or wireless (adb pair IP:PORT)",
    },
    "apktool": {
        "category": "mobile", "tier": "t2",
        "name": "APKTool (reverse-engineer APK)",
        "path": r"C:\Program Files\apktool\apktool.jar",
        "invocation": "java -jar apktool.jar d -o out_dir foo.apk",
        "argv": ["java", "-jar", r"C:\Program Files\apktool\apktool.jar", "d", "-o", "out_dir", "foo.apk"],
        "notes": "Disassemble suspicious APKs · FB-evidence use-case · requires Java",
    },
    "jadx-gui": {
        "category": "mobile", "tier": "t2",
        "name": "jadx-gui (DEX decompiler GUI)",
        "path": r"C:\Program Files\jadx\bin\jadx-gui.exe",
        "invocation": 'start "" jadx-gui  # OR: jadx-gui foo.apk',
        "argv": ["jadx-gui"],
        "notes": "Inspect DEX/APK visually · companion to apktool",
    },
    "android-studio": {
        "category": "mobile", "tier": "t3",
        "name": "Android Studio",
        "path": r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
        "invocation": 'start "" "Android Studio"',
        "argv": [r"C:\Program Files\Android\Android Studio\bin\studio64.exe"],
        "notes": "Full APK dev environment · emulator · profiler ~5 GB install",
    },
    # NOTE (cont.13): the 3 'category alias' rows that lived here in cont.8
    # (mobile-alias / status-alias / comms-alias) were DELETED because they
    # collided with real tile keys -- 'status' had been overridden, leaving
    # `TILE_REGISTRY['status']` without a 'urls' key, which broke
    # cmd_doctor._section_health -> cmd_health with KeyError: 'urls'.
    # Operators querying a category should run `python war_room.py list`
    # directly (or `python war_room.py info <category-slug>` for any
    # individual tile in that category).
}

TILES_BY_CATEGORY: Dict[str, List[str]] = {
    "ops": ["status", "vs-code", "ai-army", "mobile-recovery", "reality-audit", "pc-scan", "fleet-summary"],
    "recon": ["anti-scam-playbook", "known-scammers", "contributor-profile"],
    "evidence": ["index-delta", "index-delta-recursive", "master-reconciler", "backup-audit", "hygiene-runner"],
    "comms": ["telegram", "discord", "slack", "footclan-bridge"],
    "reference": ["ref-toolkit", "ref-grand", "ref-workspace", "ref-changelog"],
    "mobile": ["adb", "apktool", "jadx-gui", "android-studio"],
    # NOTE (cont.13): the 3 '-alias' lists (mobile-alias / status-alias / comms-alias)
    # removed alongside the corresponding TILE_REGISTRY rows above.
}

# ============================================================
# Display helpers
# ============================================================

def _w(s: str, n: int) -> str:
    return (s[: n - 1] + "…") if len(s) > n else s.ljust(n)

def print_table(rows: List[List[str]]) -> None:
    print(f"  {'TIER':<6} {'NAME':<35} {'PATH':<50} {'INVOCATION':<60}")
    print("  " + "-" * 151)
    for r in rows:
        print(f"  {r[0]:<6} {r[1]:<35} {_w(r[2], 50):<50} {_w(r[3], 60):<60}")

# ============================================================
# Subcommands
# ============================================================

def cmd_status(args: argparse.Namespace) -> int:
    print(f"  Service categories: 6  (ops / recon / evidence / comms / reference / mobile)")
    print(f"  Total tiles:         {len(TILE_REGISTRY)}")
    print(f"  Tier T1 (daily):     {sum(1 for t in TILE_REGISTRY.values() if t['tier'] == 't1')}")
    print(f"  Tier T2 (weekly):    {sum(1 for t in TILE_REGISTRY.values() if t['tier'] == 't2')}")
    print(f"  Tier T3 (monthly):   {sum(1 for t in TILE_REGISTRY.values() if t['tier'] == 't3')}")
    print()
    print(f"  Open the HUD in browser:  python war_room.py open")
    print(f"  Live health probe:        python war_room.py health")
    return 0

def cmd_list(args: argparse.Namespace) -> int:
    rows = []
    for k, t in TILE_REGISTRY.items():
        rows.append([t["tier"].upper(), t["name"], t["path"], t["invocation"]])
    print_table(rows)
    return 0

def cmd_info(args: argparse.Namespace) -> int:
    key = args.tile.lower()
    tile = TILE_REGISTRY.get(key)
    if not tile:
        cands = [k for k in TILE_REGISTRY if key in k or key in TILE_REGISTRY[k]["name"].lower()]
        if not cands:
            print(f"[ERR] tile not found: {args.tile!r}")
            return 1
        if len(cands) > 1:
            print(f"[ERR] ambiguous: {args.tile!r} matches {len(cands)} tiles:")
            for c in cands:
                print(f"        {c}  ({TILE_REGISTRY[c]['name']})")
            return 1
        tile = TILE_REGISTRY[cands[0]]
        key = cands[0]
    print(f"  Name       : {tile['name']}")
    print(f"  Slug       : {key}")
    print(f"  Category   : {tile['category']}")
    print(f"  Tier       : {tile['tier']}")
    print(f"  Path       : {tile['path']}")
    print(f"  Invocation : {tile['invocation']}")
    print(f"  Argv       : {tile['argv']}")
    print(f"  Notes      : {tile['notes']}")
    return 0

def cmd_launch(args: argparse.Namespace) -> int:
    """Print + execute (or --dry-run) one-click invocation.

    Uses argv-list form with shell=False (added 2026-07-09 review-fixup).
    """
    key = args.tile.lower()
    tile = TILE_REGISTRY.get(key)
    if not tile:
        cands = [k for k in TILE_REGISTRY if key in k or key in TILE_REGISTRY[k]["name"].lower()]
        if cands:
            tile = TILE_REGISTRY[cands[0]]
            key = cands[0]
        else:
            print(f"[ERR] tile not found: {args.tile!r}")
            return 1
    argv = tile["argv"]
    print(f"  {tile['name']}  [{tile['tier']} / {tile['category']}]")
    print(f"  Argv : {argv}")
    print(f"  As   : {tile['invocation']}")
    if args.dry_run:
        print(f"  (--dry-run acknowledged; not executing.)")
        return 0
    if not argv:
        print(f"  (this tile has no argv — reference-only; open file manually.)")
        return 0
    try:
        subprocess.Popen(argv, shell=False)
        print(f"  launched.")
    except FileNotFoundError as e:
        print(f"  [ERR] executable not found: {e}")
        return 1
    except Exception as e:
        print(f"  [ERR] launch failed: {e}")
        return 1
    return 0

def cmd_open(args: argparse.Namespace) -> int:
    target = "WAR_ROOM_PUBLIC.html" if args.public else "WAR_ROOM.html"
    print(f"  Opening {target} in default browser...")
    try:
        webbrowser.open(target)
        print(f"  opened. (browser may have prompted for path; if not, open manually)")
    except Exception as e:
        print(f"  [ERR] webbrowser.open failed: {e}")
        print(f"  Manual workaround: open {target} manually in your browser.")
        return 1
    return 0

def cmd_health(args: argparse.Namespace) -> int:
    tile = TILE_REGISTRY["status"]
    print(f"\n  HEALTH PROBE — {tile['name']}:\n")
    print(f"  {'SERVICE':<10} {'URL':<48} {'STATE':<10} {'LATENCY':<10}")
    print("  " + "-" * 78)
    for url in tile["urls"]:
        try:
            import time
            if "://" in url:
                _, rest = url.split("://", 1)
                host_port = rest.split("/", 1)[0]
                if ":" in host_port:
                    host, port = host_port.rsplit(":", 1)
                    port = int(port)
                else:
                    host, port = host_port, 80
            t0 = int(time.time() * 1000)
            sock = socket.create_connection((host, port), timeout=1.5)
            sock.close()
            latency = int(time.time() * 1000) - t0
            state = "up"
        except (socket.timeout, ConnectionRefusedError, OSError):
            state = "down"
            latency = "n/a"
        svc = url.split("//")[1].split(":")[0].split(".")[0]
        print(f"  {svc:<10} {url[:48]:<48} {state:<10} {str(latency):<10}")
    return 0

# ============================================================
# MOBILE_FILTERED.csv dynamic-loader (added 2026-07-09 followup-wave cont.8)
# Auto-extends TILE_REGISTRY at import-time so the operator does NOT have
# to hand-edit REGISTRY every time a new mobile tool lands on the PC.
# Each detected DisplayName + matched_terms pair becomes a lookup-only
# tile (argv intentionally empty per safety rule).
#
# Concurrency: refresh_mobile_inventory.bat rewrites MOBILE_FILTERED.csv via
# tmp + Move-Item (atomic on the writer side); we use a tmp + copyfileobj
# snapshot here to mirror that atomicity and avoid partial-read on the
# reader side.
# ============================================================
def _extend_TILE_REGISTRY_from_MOBILE_FILTERED() -> None:
    """Read MOBILE_FILTERED.csv at import-time and add detected mobile tools as
    lookup-only tiles in TILE_REGISTRY. Silent no-op if the file is missing
    or fails to parse.

    Per safety rule: argv is left empty (no auto-launch for unknown tools).
    """
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MOBILE_FILTERED.csv")
    if not os.path.exists(csv_path):
        return
    try:
        import tempfile as _tempfile
        import shutil as _shutil
        # Single shot: copy CSV -> tmpfile, read from tmpfile, cleanup in finally.
        _tmp_fd, _tmp_path = _tempfile.mkstemp(suffix=".csv", prefix="mobile_filtered_import_")
        try:
            # Atomic-snapshot read: release the mkstemp fd, then copy
            # csv_path (real source) -> _tmp_path (snapshot).
            try:
                os.close(_tmp_fd)
            except OSError:
                pass
            with open(csv_path, "rb") as _src, open(_tmp_path, "wb") as _dst:
                _shutil.copyfileobj(_src, _dst)
            # utf-8-sig auto-strips PowerShell Export-Csv's UTF-8 BOM at file start.
            with open(_tmp_path, encoding="utf-8-sig") as _f:
                _reader = csv.DictReader(_f)
                for _row in _reader:
                    # Sanitize keys: strip BOM + surrounding double-quotes (combined set).
                    # .strip('"\ufeff') strips all leading/trailing chars in {"\"", "\ufeff"}.
                    # This handles the pattern BOM-then-quote-wrapped-header that PowerShell
                    # Export-Csv produces when the source CSV header is itself quoted.
                    _row = {str(k).strip().strip('"\ufeff'): v for k, v in _row.items()}
                    _name = (_row.get("DisplayName") or "").strip().strip('"\ufeff')
                    _terms = (_row.get("matched_terms") or "").strip().strip('"\ufeff')
                    if not _name or not _terms:
                        continue
                    _slug = "".join((c if c.isalnum() else "-") for c in _name.lower()).strip("-")[:40]
                    if not _slug or _slug in TILE_REGISTRY:
                        continue
                    TILE_REGISTRY[_slug] = {
                        "category": "mobile",
                        "tier": "t3",
                        "name": _name[:60],
                        "path": f"(MOBILE_FILTERED.csv: {_terms})",
                        "invocation": f"(auto-detected from MOBILE_FILTERED.csv · term={_terms.split(',')[0].strip().lower()}; lookup-only)",
                        "argv": [],
                        "notes": f"Dynamic tile from MOBILE_FILTERED.csv · matched_terms={_terms[:60]}",
                    }
        finally:
            try: os.remove(_tmp_path)
            except OSError: pass
    except (OSError, KeyError, UnicodeDecodeError):
        # Silent no-op per CLAUDE.md "do not crash on a single failure"
        pass

# Auto-call at import-time; runs after TILE_REGISTRY is fully populated above
_extend_TILE_REGISTRY_from_MOBILE_FILTERED()

# ============================================================
# validate-mobile subcommand (added 2026-07-09 followup-wave cont.10)
# Reads in-memory TILE_REGISTRY and counts dynamic MOBILE_FILTERED.csv tiles.
# Exits 0 if >=1 tile, 1 otherwise. Useful for pre-commit, post-task checks,
# or `schtasks` post-run validation.
# ============================================================
def cmd_validate_mobile(args: argparse.Namespace) -> int:
    """Verify the MOBILE_FILTERED.csv dynamic-loader picked up rows.

    Exit codes:
      0 = loader worked (may have 0 dynamic tiles if source CSV has 0 rows = clean PC, OR CSV missing = no inventory yet)
      1 = real loader bug: source CSV has rows but loader found 0 dynamic tiles
    """
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MOBILE_FILTERED.csv")
    if not os.path.exists(csv_path):
        print("  [INFO] MOBILE_FILTERED.csv missing (no mobile inventory yet).")
        print("         Run: refresh_mobile_inventory.bat   (full pipeline)")
        return 0
    # Count source rows independently of the dynamic loader (defensive: separate read).
    src_row_count = 0
    try:
        with open(csv_path, encoding="utf-8-sig") as _f:
            src_row_count = sum(1 for _ in csv.DictReader(_f))
    except (OSError, UnicodeDecodeError):
        pass
    dyn_tiles = [(k, t) for k, t in TILE_REGISTRY.items()
                 if "Dynamic tile from MOBILE_FILTERED.csv" in str(t.get("notes", ""))]
    if src_row_count == 0:
        print("  [INFO] MOBILE_FILTERED.csv has 0 rows (no mobile tools detected).")
        return 0
    if not dyn_tiles:
        print(f"  [FAIL] MOBILE_FILTERED.csv has {src_row_count} row(s) but loader found 0 dynamic tiles.")
        print("         This is a loader bug — check BOM/quote handling, encoding, field names.")
        return 1
    print(f"  [PASS] {len(dyn_tiles)} dynamic MOBILE_FILTERED.csv tile(s) detected (from {src_row_count} source row(s)):")
    for k, t in dyn_tiles:
        print(f"    {k:40s} | {t['name'][:50]}")
    return 0

# ============================================================
# validate-tools subcommand (added 2026-07-09 followup-wave cont.11)
# Checks java + apktool + jadx for FOUND/NOT_FOUND/BROKEN state.
# Mirrors the 3-case pattern established by validate-mobile:
#   FOUND    = tool exists AND version invocation returns rc=0
#   NOT_FOUND = tool missing from JAVA_HOME/PATH/portable install (legitimate clean-PC state)
#   BROKEN   = tool exists but invocation failed (real problem, exit 1)
# Flags:
#   --json     emit machine-readable JSON for CI / schtasks post-validation
#   --verbose  show captured version output (debugging)
# ============================================================
def cmd_validate_tools(args: argparse.Namespace) -> int:
    """Verify required Android-reverse engineering tools are installed.

    Exit codes:
      0 = all tools FOUND or legitimately NOT_FOUND (clean PC is OK)
      1 = any tool BROKEN (found but version invocation failed -- real problem)
    """
    tool_table: List[tuple] = []
    overall_broken = False
    remediation: List[str] = []

    def _record(label: str, status: str, version: str, path: str) -> None:
        tool_table.append((label, status, version, path))

    # --- 1. JAVA resolution chain ------------------------------------
    #     1a. JAVA_HOME\bin\java.exe            (operator-set env var)
    #     1b. Tools\jdk\jdk-17\bin\java.exe    (portable install via install_jdk_portable.ps1)
    #     1c. java.exe on system PATH          (default install)
    java_exe = None
    java_version = "-"
    if os.environ.get("JAVA_HOME") and os.path.exists(os.path.join(os.environ["JAVA_HOME"], "bin", "java.exe")):
        java_exe = os.path.join(os.environ["JAVA_HOME"], "bin", "java.exe")
    elif os.name == "nt" and os.path.exists(
        os.path.join(os.environ.get("USERPROFILE", ""), "Tools", "jdk", "jdk-17", "bin", "java.exe")
    ):
        java_exe = os.path.join(os.environ["USERPROFILE"], "Tools", "jdk", "jdk-17", "bin", "java.exe")
    elif shutil.which("java.exe") or shutil.which("java"):
        java_exe = shutil.which("java.exe") or shutil.which("java")

    java_status = "NOT_FOUND"
    if java_exe:
        try:
            _flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
            res = subprocess.run([java_exe, "-version"], capture_output=True, text=True, timeout=5, creationflags=_flags)
            ver_out = ((res.stdout or "") + "\n" + (res.stderr or "")).strip()
            if res.returncode == 0 and ("openjdk version" in ver_out or "java version" in ver_out):
                _parts = ver_out.split('"')
                java_version = _parts[1] if len(_parts) >= 2 else ver_out.split("\n")[0]
                java_status = "FOUND"
            else:
                java_status = "BROKEN"
                overall_broken = True
                remediation.append(f"java: -version returned rc={res.returncode}; try `install_jdk_portable.ps1 -force`")
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as _e:
            java_status = "BROKEN"
            overall_broken = True
            remediation.append(f"java: subprocess failed ({type(_e).__name__}: {_e})")
    else:
        remediation.append("java: not on PATH and no portable install -- run install_jdk_portable.ps1")
    _record("java", java_status, java_version, java_exe or "(not found)")

    # --- 2/3. APKTOOL + JADX (FAST-PATH: read META-INF/MANIFEST.MF directly) ---
    # Why fast-path instead of .bat subprocess:
    #   - apktool.jar does NOT support the --version flag (only -version); passing
    #     --version causes the JVM to hang waiting for input -- triggers a 30s+
    #     subprocess timeout that masks a real FOUND state.
    #   - Windows Defender + cold-start class-init can add 5-15s on first JVM launch.
    #   - Manifest.MF read is ~50ms via Python's zipfile module -- no JVM, no AV.
    # Trade-off: if Implementation-Version is absent from the JAR's META-INF/MANIFEST.MF,
    # we report NOT_FOUND (rare; apktool 2.x and jadx 1.x both ship with this field).
    JAR_LOCATIONS = [
        ("apktool", os.path.join(os.environ.get("USERPROFILE", ""), "Tools", "apktool")),
        ("jadx",    os.path.join(os.environ.get("USERPROFILE", ""), "Tools", "jadx", "lib")),
    ]
    for label, jar_dir in JAR_LOCATIONS:
        status = "NOT_FOUND"
        version = "-"
        actual_jar = ""
        candidates_scanned: List[str] = []
        corrupt_count = 0
        if os.path.isdir(jar_dir):
            # Iterate alphabetically; prefer highest version when multiple .jars match.
            # sorted() works for apktool_X.Y.Z.jar because alphabetic and version order
            # agree for fixed-precision numeric X.Y.Z triples.
            try:
                candidates = sorted(
                    os.path.join(jar_dir, fn) for fn in os.listdir(jar_dir) if fn.endswith(".jar")
                )
            except (FileNotFoundError, OSError):
                candidates = []
            for cand in candidates:
                candidates_scanned.append(os.path.basename(cand))
                try:
                    with zipfile.ZipFile(cand) as zf:
                        manifest_bytes = zf.read("META-INF/MANIFEST.MF")
                        manifest = manifest_bytes.decode("utf-8", errors="replace")
                        m = re.search(r"Implementation-Version:\s*([^\s]+)", manifest)
                        if m:
                            status = "FOUND"
                            version = m.group(1).strip()
                            actual_jar = cand
                            break
                except (KeyError, zipfile.BadZipFile, OSError):
                    corrupt_count += 1
                    continue
        if status == "NOT_FOUND":
            # Distinguish 4 distinct NOT_FOUND causes -- each maps to a specific
            # operator action (install dir / un-extracted / corrupted / non-standard).
            if not os.path.isdir(jar_dir):
                remediation.append(f"{label}: {jar_dir} not found -- unzip operator-supplied archive into Tools\\{label}\\")
            elif not candidates_scanned:
                remediation.append(f"{label}: {jar_dir} contains no .jar files -- re-extract the operator-supplied archive")
            elif corrupt_count == len(candidates_scanned):
                remediation.append(f"{label}: {jar_dir} contains {corrupt_count} .jar file(s) but ALL are corrupted -- re-download the archive")
            else:
                remediation.append(
                    f"{label}: {jar_dir} has {len(candidates_scanned)} .jar(s) ({corrupt_count} corrupted, "
                    f"{len(candidates_scanned) - corrupt_count} readable) but NONE have Implementation-Version "
                    f"-- the source archive is non-standard; META-INF/MANIFEST.MF missing or stripped"
                )
        _record(label, status, version, actual_jar or jar_dir)

    # --- Output rendering -------------------------------------------
    if getattr(args, "json", False):
        import json as _json
        result = {
            "aggregate_ok": not overall_broken,
            "tools": {label: {"status": st, "version": v, "path": p} for label, st, v, p in tool_table},
            "remediation": remediation,
        }
        print(_json.dumps(result, indent=2))
        return 1 if overall_broken else 0

    print()
    print(f"  TOOL STATUS (aggregate: {'FAIL' if overall_broken else 'OK'}):")
    print()
    print(f"  {'TOOL':<10} {'STATUS':<12} {'VERSION':<14} PATH")
    print("  " + "-" * 92)
    for label, status, version, path in tool_table:
        _badge = {"FOUND": "[PASS]", "NOT_FOUND": "[INFO]", "BROKEN": "[FAIL]"}.get(status, status)
        print(f"  {label:<10} {_badge:<12} {version[:14]:<14} {path}")
    print()

    if overall_broken:
        print("  [FAIL] at least one tool is BROKEN. Remediation hints:")
        for r in remediation:
            print(f"    - {r}")
        return 1

    found_count = sum(1 for _, s, _, _ in tool_table if s == "FOUND")
    if found_count == 0:
        print("  [INFO] no Android-reverse tools installed. To add JDK + tooling:")
        print("         powershell -NoProfile -ExecutionPolicy Bypass -File install_jdk_portable.ps1")
        print("         Then unzip apktool + jadx into Tools\\ (war_room.py stores expected paths).")
        return 0

    print(f"  [PASS] {found_count}/{len(tool_table)} Android-reverse tool(s) correctly resolvable.")
    if getattr(args, "verbose", False):
        print("  (--verbose: each tool's full --version output was captured at detection time.)")
    return 0

# ============================================================
# cmd_doctor: aggregate workspace health check (added cont.13)
# Bundles 7 per-section checks into a single "is my workspace healthy?" report.
# Sections (each returns a (status, detail_str) tuple):
#   1. validate-tools        FOUND / NOT_FOUND / BROKEN of java/apktool/jadx
#   2. validate-mobile       dynamic MOBILE_FILTERED.csv tile counts
#   3. health                5 local TCP probes (Ollama/ComfyUI/Archon/n8n/AI Army)
#   4. python                interpreter version
#   5. tools                 Tools/ inventory count + presence
#   6. mobile-csv            MOBILE_FILTERED.csv age (INFO if missing; WARN if >7d)
#   7. git                   working-tree status (INFO if uncommitted changes)
# Aggregate semantics:
#   rc=0  = aggregate OK  (no FAIL sections present)
#   rc=1  = aggregate FAIL (at least one FAIL section present)
#   WARN  = signal in iter mode; do NOT bump aggregate to FAIL
# Exit code is what schtasks / operator's eyes / pre-commit hooks key off.
# Flags:
#   --json   emit machine-readable JSON (CI-friendly)
#   --quiet  suppress per-section multi-line detail (emit only section badges)
# ============================================================
def _section_validate_tools() -> Tuple[str, str]:
    """Run cmd_validate_tools; capture stdout; return (status, detail_stripped)."""
    with _capture_stdout() as _buf:
        rc = cmd_validate_tools(argparse.Namespace(json=False, verbose=False))
    return ("FAIL" if rc == 1 else "OK", _buf.getvalue().strip())


def _section_validate_mobile() -> Tuple[str, str]:
    """Run cmd_validate_mobile; capture stdout; return (status, detail_stripped)."""
    with _capture_stdout() as _buf:
        rc = cmd_validate_mobile(argparse.Namespace())
    return ("FAIL" if rc == 1 else "OK", _buf.getvalue().strip())


def _section_health() -> Tuple[str, str]:
    """Run cmd_health; count up/down services; return (status, detail_stripped).

    cmd_health prints fixed-width lines: `<svc> <url> <state-padded-10> <latency-padded-10>`.
    The state's literal value is in column index 2 after whitespace-split.
    Earlier attempt used `line.rstrip().endswith(" up")` which never matched
    because the line ends with latency, not state -- always returned OK.
    """
    with _capture_stdout() as _buf:
        cmd_health(argparse.Namespace())
    text = _buf.getvalue()
    up_count = 0
    down_count = 0
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[2] in ("up", "down"):
            if parts[2] == "up":
                up_count += 1
            else:
                down_count += 1
    if down_count == 0:
        status = "OK"
    elif up_count > 0:
        status = "WARN"  # some up, some down -- iterate mode
    else:
        status = "FAIL"
    return (status, text.strip())


def _section_python() -> Tuple[str, str]:
    return ("OK", f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def _section_tools() -> Tuple[str, str]:
    """Tools/ inventory count + brief summary."""
    tools_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Tools")
    if not os.path.isdir(tools_dir):
        return ("INFO", f"{tools_dir} not present (portable install bare)")
    try:
        entries = sorted(os.listdir(tools_dir))
    except OSError as _e:
        return ("WARN", f"{tools_dir} exists but unreadable: {_e}")
    preview = ", ".join(entries[:8])
    suffix = "..." if len(entries) > 8 else ""
    return ("OK", f"{len(entries)} entries in {tools_dir}: {preview}{suffix}")


def _section_mobile_csv() -> Tuple[str, str]:
    """MOBILE_FILTERED.csv presence + age (WARN if >7d stale, INFO if missing)."""
    import time
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MOBILE_FILTERED.csv")
    if not os.path.exists(csv_path):
        return ("INFO", f"{csv_path} missing -- run refresh_mobile_inventory.bat")
    try:
        age_h = (time.time() - os.path.getmtime(csv_path)) / 3600.0
    except OSError as _e:
        return ("WARN", f"{csv_path} exists but mtime failed: {_e}")
    if age_h >= 24 * 7:
        return ("WARN", f"{csv_path} stale ({age_h:.1f}h ago; refresh-warn threshold 168h)")
    return ("OK", f"{csv_path} ({age_h:.1f}h ago)")


def _section_git() -> Tuple[str, str]:
    """git working-tree status (INFO if uncommitted, OK if clean)."""
    try:
        _flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        _gr = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5, creationflags=_flags,
        )
    except FileNotFoundError:
        return ("INFO", "git not on PATH (clean tree assumed)")
    except (subprocess.TimeoutExpired, OSError) as _e:
        return ("WARN", f"git check failed: {type(_e).__name__}: {_e}")
    git_lines = [l for l in (_gr.stdout or "").splitlines() if l.strip()]
    if git_lines:
        return ("INFO", f"{len(git_lines)} uncommitted change(s)")
    return ("OK", "working tree clean")


def cmd_doctor(args: argparse.Namespace) -> int:
    """Aggregate 7-section workspace health check.

    Exit codes:
      0 = aggregate OK (no FAIL sections)
      1 = aggregate FAIL (>=1 FAIL section -- tool broken, services all-down, etc.)
    WARN signals (iter-mode) and INFO signals (missing optional files) do NOT
    flip aggregate to FAIL -- they're legitimate while-iterating signals.
    """
    import json as _json

    sections: List[Tuple[str, str, str]] = []  # (name, status, detail)
    overall_fail = False

    raw_pairs: List[Tuple[str, Tuple[str, str]]] = [
        ("validate-tools", _section_validate_tools()),
        ("validate-mobile", _section_validate_mobile()),
        ("health", _section_health()),
        ("python", _section_python()),
        ("tools", _section_tools()),
        ("mobile-csv", _section_mobile_csv()),
        ("git", _section_git()),
    ]
    for name, (status, detail) in raw_pairs:
        if status == "FAIL":
            overall_fail = True
        sections.append((name, status, detail))

    # --- Output rendering ---
    if getattr(args, "json", False):
        # Trim detail to first line for compact JSON; full detail lives in text mode.
        result = {
            "aggregate_ok": not overall_fail,
            "sections": [
                {"name": n, "status": s, "detail": (d.splitlines()[0] if d else "")}
                for n, s, d in sections
            ],
        }
        print(_json.dumps(result, indent=2))
        return 0 if not overall_fail else 1

    quiet = getattr(args, "quiet", False)
    print()
    print(f"  WORKSPACE DOCTOR (aggregate: {'FAIL' if overall_fail else 'OK'}):")
    print()
    _badges = {"OK": "[PASS]", "WARN": "[WARN]", "INFO": "[INFO]", "FAIL": "[FAIL]"}
    for name, status, detail in sections:
        _badge = _badges.get(status, status)
        _first = detail.splitlines()[0] if detail else "(empty)"
        print(f"  {_badge:<7} {name:<16} {_first}")
        if not quiet:
            for line in detail.splitlines()[1:]:
                print(f"          {line}")
    print()
    if overall_fail:
        print("  [FAIL] workspace has issues. Address FAILs above.")
        return 1
    print("  [PASS] workspace is healthy.")
    return 0


# ============================================================
# cmd_archive_outbox: roll SLEEP_TRIPLE/outbox/* -> archive/outbox_YYYY-MM-DD/ (added cont.14)
# Why: outbox files (text scripts, PNG renders, JSON manifests) accumulate unboundedly.
# Daily-rolled archive keeps N days of operator-visible droppings, then moves them
# out of the hot path so subsequent SLEEP_TRIPLE nights don't repaint over them.
# Flags:
#   --dry-run           print what WOULD happen; do NOT move
#   --keep-last <N>     only archive files older than N days (default: archive everything)
#   --category <name>   only archive one specific outbox subdir (a_digital_factory / b_faceless_shorts / cover_art / e_pod / gumroad_packages)
#   --json              emit machine-readable JSON (CI-friendly, schtasks-post-archive audit)
# Exit codes:
#   0 = clean (nothing to archive OR all moves succeeded -- including --dry-run)
#   1 = at least one move failed (real OSError / PermissionError / disk-full)
# Safety:
#   - shutil.move on the same volume is atomic (rename); cross-volume falls back to copy+unlink.
#   - We never delete the source until dst is confirmed written (no in-place destructive ops).
#   - Empty outbox/ is NOT an error -- reports "[INFO] nothing to archive" with rc=0.
# ============================================================
def _walk_archivable_files(outbox_root: str, keep_last_days) -> List[Tuple[str, str, float]]:
    """Walk outbox_root/*/<files> recursively, yielding (src_abs, subdir_name, mtime).

    keep_last_days=None  -> archive all files regardless of age.
    keep_last_days=int   -> archive only files with mtime older than that many days.
    Silent no-op on missing outbox_root (returns empty list).
    """
    import time as _time_walk
    if not os.path.isdir(outbox_root):
        return []
    cutoff = None
    if isinstance(keep_last_days, int) and keep_last_days > 0:
        cutoff = _time_walk.time() - keep_last_days * 24 * 3600
    out: List[Tuple[str, str, float]] = []
    for subdir_name in sorted(os.listdir(outbox_root)):
        subdir_path = os.path.join(outbox_root, subdir_name)
        if not os.path.isdir(subdir_path):
            continue
        for dirpath, _dirs, filenames in os.walk(subdir_path):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                try:
                    mt = os.path.getmtime(fp)
                except OSError:
                    continue
                if cutoff is not None and mt > cutoff:
                    continue
                out.append((fp, subdir_name, mt))
    return out


def cmd_archive_outbox(args: argparse.Namespace) -> int:
    """Roll SLEEP_TRIPLE/outbox/* files into archive/outbox_YYYY-MM-DD/.

    Layout preserved: each outbox/<subdir_name>/<rest> becomes
    archive/outbox_<YYYY-MM-DD>/<subdir_name>/<rest>.
    """
    import json as _json
    import time as _time

    here = os.path.dirname(os.path.abspath(__file__))
    outbox_root = os.path.join(here, "SLEEP_TRIPLE", "outbox")
    archive_root = os.path.join(here, "SLEEP_TRIPLE", "archive")
    date_str = _time.strftime("%Y-%m-%d")
    keep_last = getattr(args, "keep_last", None)
    dry_run = getattr(args, "dry_run", False)
    only_category = getattr(args, "category", None)
    json_mode = getattr(args, "json", False)

    archivable = _walk_archivable_files(outbox_root, keep_last)
    if only_category:
        archivable = [(s, sub, mt) for (s, sub, mt) in archivable if sub == only_category]

    results: List[Dict[str, str]] = []
    overall_fail = False

    for src_path, subdir_name, _mt in archivable:
        subdir_full = os.path.join(outbox_root, subdir_name)
        rel = os.path.relpath(src_path, start=subdir_full)
        dst = os.path.join(archive_root, f"outbox_{date_str}", subdir_name, rel)
        entry: Dict[str, str] = {"src": src_path, "dst": dst, "status": "DRY_RUN"}
        if dry_run:
            results.append(entry)
            continue
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src_path, dst)
            entry["status"] = "OK"
            results.append(entry)
        except (OSError, shutil.Error) as _e:
            entry["status"] = "FAIL"
            entry["error"] = f"{type(_e).__name__}: {_e}"
            results.append(entry)
            overall_fail = True

    # --- Output rendering ---
    if json_mode:
        out = {
            "date_str": date_str,
            "dry_run": dry_run,
            "keep_last_days": keep_last,
            "category_filter": only_category,
            "outbox_root": outbox_root,
            "archive_root": archive_root,
            "aggregate_ok": not overall_fail,
            "file_counts": {
                "ok": sum(1 for r in results if r["status"] == "OK"),
                "dry_run": sum(1 for r in results if r["status"] == "DRY_RUN"),
                "failed": sum(1 for r in results if r["status"] == "FAIL"),
            },
            "results": results,
        }
        print(_json.dumps(out, indent=2))
        return 0 if not overall_fail else 1

    print()
    print(f"  ARCHIVE OUTBOX  (date={date_str}, dry_run={dry_run}, keep_last={keep_last!r}, category={only_category!r})")
    print()
    # Print summary table FIRST so empty outboxes show "moved: 0" too (operator scannability).
    moved = sum(1 for r in results if r["status"] == "OK")
    dry = sum(1 for r in results if r["status"] == "DRY_RUN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  moved     : {moved}")
    print(f"  dry-run   : {dry}")
    print(f"  failed    : {failed}")
    print()
    if not results:
        sub_count = sum(1 for s in os.listdir(outbox_root) if os.path.isdir(os.path.join(outbox_root, s))) if os.path.isdir(outbox_root) else 0
        print(f"  [INFO] no archiveable files in {outbox_root} (subdir count: {sub_count})")
        return 0
    if dry_run and dry > 0:
        print(f"  [INFO] --dry-run: listing up to first 10 source paths that WOULD move:")
        for r in results[:10]:
            print(f"    {r['src']}")
        if dry > 10:
            print(f"    ... +{dry - 10} more")
        return 0
    if failed > 0:
        print(f"  [FAIL] {failed} file(s) could not be moved. First 10 errors:")
        err_count = 0
        for r in results:
            if r["status"] == "FAIL":
                print(f"    - {r['src']}")
                print(f"        {r.get('error', '?')}")
                err_count += 1
                if err_count >= 10:
                    if err_count < failed:
                        print(f"    ... +{failed - err_count} more")
                    break
        return 1
    print(f"  [PASS] outbox archived to {os.path.join(archive_root, 'outbox_' + date_str)}")
    return 0


# ============================================================
# cmd_snapshot_doctor / cmd_diff_doctor (added cont.15)
# Capture cmd_doctor --json output to .cache/war_room/snapshots/ on a date-stamped file,
# then compare any two snapshots to surface health drift over time.
#
# Design:
#   - The snapshot file is a verbatim copy of `python war_room.py doctor --json`
#     output (schema-version field added at write time so future schema drift
#     is detectable by cmd_diff_doctor rather than silently mis-comparing).
#   - Cache dir: <USERPROFILE>/.cache/war_room/snapshots/   (operator-local)
#     Falls back to <here>/.cache/war_room/snapshots/        if USERPROFILE unset
#     or %USERPROFILE%\.cache\ not writable (CI runners / non-Windows).
#   - --list mode prints existing snapshot filename + utc-isofmt + first section
#     so the operator can eyeball how many snapshots exist + their timestamps
#     without parsing JSON themselves.
#   - --keep-last N prunes (deletes) the OLDEST snapshots, keeping N newest.
#     Safe no-op if list shorter than N.
# Flags:
#   cmd_snapshot_doctor:
#     --list         list existing snapshots (does NOT write a new one)
#     --keep-last N  prune oldest, keep N newest (NO new write)
#     --json         emit machine-readable JSON for the chosen sub-mode
# cmd_diff_doctor:
#     --a <prefix>   "a" snapshot (full filename OR date prefix e.g. 2026-07-09)
#     --b <prefix>   "b" snapshot (comparison side; defaults to most-recent if absent)
#     --json         emit machine-readable JSON (CI-friendly)
# Exit codes:
#   cmd_snapshot_doctor: 0 = clean write OR list OR prune
#   cmd_diff_doctor:     0 = diff printed (regardless of how many transitions)
#                       1 = cannot resolve --a/--b to existing snapshots
# ============================================================
def _snapshot_dir() -> str:
    """Resolve operator-local snapshot dir; create on demand."""
    base = os.environ.get("USERPROFILE") or os.environ.get("HOME") or os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(base, ".cache", "war_room", "snapshots")
    try:
        os.makedirs(d, exist_ok=True)
        return d
    except OSError:
        # Fall back to <here>/.cache/war_room/snapshots/ if HOME/USERPROFILE path not writable.
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "war_room", "snapshots")
        os.makedirs(d, exist_ok=True)
        return d


def _snapshot_filepath(sd: str, stamp: str) -> str:
    """Return a collision-safe snapshot path for the given stamp prefix.

    First write in a given second uses ``snapshot__<stamp>.json``. Rapid successive
    writes within the same second append ``_<NN>`` (02..999) so integration tests
    and nightly double-runs never silently overwrite an earlier capture.
    """
    base = os.path.join(sd, f"snapshot__{stamp}.json")
    if not os.path.exists(base):
        return base
    for seq in range(2, 1000):
        candidate = os.path.join(sd, f"snapshot__{stamp}_{seq:02d}.json")
        if not os.path.exists(candidate):
            return candidate
    raise OSError(f"could not find free snapshot filename for stamp {stamp!r} (>=1000 collisions in one second)")


def _list_snapshots() -> List[Tuple[str, float]]:
    """Return (filename, mtime_epoch) sorted oldest→newest. Silent empty list on missing dir.

    Sorts by MTIME (not filename) so the order is robust to stamp-format changes
    (e.g. a future epoch-ms stamp would still order correctly here, even though
    alphabetical filename ordering would silently break).
    """
    d = _snapshot_dir()
    if not os.path.isdir(d):
        return []
    out: List[Tuple[str, float]] = []
    for fn in os.listdir(d):
        if fn.startswith("snapshot__") and fn.endswith(".json"):
            try:
                mt = os.path.getmtime(os.path.join(d, fn))
            except OSError:
                continue
            out.append((fn, mt))
    out.sort(key=lambda x: x[1])  # mtime ascending
    return out


# ============================================================
# _capture_stdout -- context manager for capturing subcommand stdout (cont.20)
#
# Used by cmd_launch_trend (--json mode composite) to capture cmd_diff_doctor +
# cmd_trend_doctor output without polluting the real stdout. Guarantees stdout
# restoration via try/finally even if the caller raises.
# ============================================================
@contextmanager
def _capture_stdout():
    """Capture sys.stdout writes within the context; yield the StringIO buffer.

    Usage:
        with _capture_stdout() as buf:
            subcommand_that_prints()
        payload = json.loads(buf.getvalue())

    Guarantees sys.stdout is restored to its original value when the context exits,
    even if the wrapped block raises.
    """
    import io as _io
    _buf = _io.StringIO()
    _old = sys.stdout
    sys.stdout = _buf
    try:
        yield _buf
    finally:
        sys.stdout = _old


def _resolve_snapshot(prefix_or_full: str, *, snaps: Optional[List[Tuple[str, float]]] = None) -> Optional[str]:
    """Resolve a date prefix (e.g. '2026-07-09') OR exact filename to one absolute path.

    Strategy (deterministic):
      1. Exact filename match (full name OR `snapshot__<X>.json` form) -> try first.
         Ties (impossible in practice) -> most-recent by mtime.
      2. Prefix match against `snapshot__<p>` -> ZERO matches -> None.
      3. AMBIGUOUS prefix (>=2 matches) -> MOST-RECENT by mtime (per MINOR #4 cont.15)
         Rationale: typing `--a 2026-07-09` with 2 same-day snapshots almost
         certainly means "most recent of today", not an error.

    Returns None only when ZERO matches across both exact AND prefix paths.

    Performance: optional `snaps` arg (MINOR #2 cont.16) lets callers pass in
    a pre-computed snapshot list to avoid O(N) re-stat calls when the caller
    already has the list (e.g. cmd_diff_doctor resolves --a + --b in one shot).
    """
    if snaps is None:
        snaps = _list_snapshots()
    if not prefix_or_full:
        return None
    p = prefix_or_full
    # 1. Exact filename match
    exact_set = {fn for (fn, _mt) in snaps if fn == p or fn == f"snapshot__{p}.json"}
    if exact_set:
        targeted = [(fn, mt) for (fn, mt) in snaps if fn in exact_set]
        targeted.sort(key=lambda x: x[1], reverse=True)  # most-recent first
        return os.path.join(_snapshot_dir(), targeted[0][0])
    # 2. Prefix match (most-recent on ambiguity, MINOR #4 cont.15)
    pref = [(fn, mt) for (fn, mt) in snaps if fn.startswith(f"snapshot__{p}")]
    if not pref:
        return None
    pref.sort(key=lambda x: x[1], reverse=True)  # most-recent first
    return os.path.join(_snapshot_dir(), pref[0][0])


def cmd_snapshot_doctor(args: argparse.Namespace) -> int:
    """Write/manage .cache/war_room/snapshots/ of cmd_doctor --json output."""
    import json as _json
    import time as _time

    sd = _snapshot_dir()
    list_mode = getattr(args, "list", False)
    keep_last = getattr(args, "keep_last", None)
    json_mode = getattr(args, "json", False)

    # --- --list mode (read-only; safe to call before any snapshot exists) ---
    if list_mode:
        snaps = _list_snapshots()
        if json_mode:
            print(_json.dumps([{"file": fn, "mtime_epoch": mt} for fn, mt in snaps], indent=2))
        else:
            print()
            print(f"  SNAPSHOTS — .cache/war_room/snapshots/  ({len(snaps)} file(s)):")
            print()
            print(f"  {'FILE':<48} {'MTIME (iso-utc approximate)':<32}")
            print("  " + "-" * 82)
            for fn, mt in snaps:
                print(f"  {fn:<48} {_time.strftime('%Y-%m-%d %H:%M:%S', _time.localtime(mt)):<32}")
            print()
            if not snaps:
                print("  [INFO] no snapshots yet. Run: python war_room.py snapshot-doctor")
        return 0

    # --- --keep-last N prune mode (destructive but bounded) ---
    # MINOR (cont.15): `--keep-last 0` would wipe ALL snapshots -- prefer --list + manual del.
    # Floor at 1 so callers cannot bulk-nuke via this single-arg path.
    if keep_last is not None:
        if keep_last < 1:
            if json_mode:
                print(_json.dumps({"note": "noop", "reason": "--keep-last < 1 is not destructive via this command (use --list + manual rm)."}, indent=2))
            else:
                print(f"  [INFO] --keep-last must be >= 1 to use this prune path; use --list + manual `rm` for a full wipe.")
            return 0
    if keep_last is not None and keep_last >= 1:
        snaps = _list_snapshots()
        if len(snaps) > keep_last:
            pruned = snaps[: len(snaps) - keep_last]
            pruned_paths = []
            for fn, _mt in pruned:
                try:
                    os.remove(os.path.join(sd, fn))
                    pruned_paths.append(fn)
                except OSError:
                    pass
            if json_mode:
                print(_json.dumps({"kept": keep_last, "pruned": pruned_paths, "remaining": len(snaps) - len(pruned_paths)}, indent=2))
            else:
                print(f"  [PASS] pruned {len(pruned_paths)} snapshot(s); keeping {keep_last} newest.")
            return 0
        if json_mode:
            print(_json.dumps({"kept": keep_last, "pruned": [], "remaining": len(snaps)}, indent=2))
        else:
            print(f"  [INFO] {len(snaps)} snapshots already <= --keep-last {keep_last}; nothing pruned.")
        return 0

    # --- WRITE mode: invoke cmd_doctor --json, save with schema-version stamp ---
    # cont.21: reuse module-level _capture_stdout() (same DRY pattern as
    # cmd_launch_trend --json and the _section_* doctor helpers).
    with _capture_stdout() as _buf:
        _rc = cmd_doctor(argparse.Namespace(json=True, quiet=False))
    try:
        _payload = _json.loads(_buf.getvalue())
    except (_json.JSONDecodeError, ValueError) as _e:
        print(f"  [FAIL] cmd_doctor --json returned non-JSON: {_e}")
        return 1
    _payload["schema_version"] = DOCTOR_SNAPSHOT_SCHEMA_VERSION
    _payload["snapshot_iso"] = _time.strftime("%Y-%m-%dT%H:%M:%S")
    stamp = _time.strftime("%Y-%m-%d_%H%M%S")
    fp = _snapshot_filepath(sd, stamp)
    try:
        with open(fp, "w", encoding="utf-8") as _f:
            _json.dump(_payload, _f, indent=2)
    except OSError as _e:
        print(f"  [FAIL] could not write snapshot to {fp}: {_e}")
        return 1
    if json_mode:
        print(_json.dumps({"written": fp, "schema_version": _payload["schema_version"], "aggregate_ok": _payload.get("aggregate_ok", False)}, indent=2))
    else:
        print(f"  [PASS] snapshot written to {fp}")
        print(f"         aggregate_ok = {_payload.get('aggregate_ok', False)}")
    return 0


def cmd_diff_doctor(args: argparse.Namespace) -> int:
    """Compare two snapshots by status transition per section. --a is required."""
    import json as _json

    a_pref = getattr(args, "a", None)
    b_pref = getattr(args, "b", None)
    json_mode = getattr(args, "json", False)

    # MINOR #2 (cont.16): single-shot _list_snapshots() so we don't O(N)-stat twice.
    # Both _resolve_snapshot calls AND the --b default use the same snaps list.
    snaps = _list_snapshots()

    a_path = _resolve_snapshot(a_pref or "", snaps=snaps)
    if not a_path:
        print(f"  [FAIL] --a {a_pref!r} resolves to 0 OR >1 snapshot (use exact filename or unambiguous date prefix).")
        return 1
    # Default --b to most-recent snapshot if not provided.
    if b_pref is None:
        if snaps:
            b_pref = snaps[-1][0]  # full filename; unambiguous
    b_path = _resolve_snapshot(b_pref or "", snaps=snaps)
    if not b_path:
        print(f"  [FAIL] --b {b_pref!r} resolves to 0 OR >1 snapshot.")
        return 1

    # MINOR (cont.15): detect --a == --b explicitly so the operator doesn't mistake
    # `[PASS] no status transitions` for `workspace stable` when they actually got
    # a self-compare no-op. Most often hits when only ONE snapshot exists and --b
    # auto-picked the same file as --a.
    if os.path.samefile(a_path, b_path):
        print(f"  [INFO] --a and --b resolve to the SAME snapshot ({os.path.basename(a_path)}); no diff to compute. Provide two distinct timestamps for an actual diff.")
        return 0

    try:
        with open(a_path, encoding="utf-8") as _fa:
            a = _json.load(_fa)
        with open(b_path, encoding="utf-8") as _fb:
            b = _json.load(_fb)
    except (OSError, _json.JSONDecodeError) as _e:
        print(f"  [FAIL] could not read snapshots: {_e}")
        return 1

    # MINOR #1 (cont.16): validate schema_version at read-time. Missing/None is
    # treated as legacy (pre-cont.16 snapshots) and is OK; any other unknown OR
    # different-from-canonical version triggers [WARN] so silent miscomparison
    # is impossible when the schema is bumped.
    schema_a = a.get("schema_version")  # None if absent (legacy)
    schema_b = b.get("schema_version")
    canonical = DOCTOR_SNAPSHOT_SCHEMA_VERSION
    schema_warnings: List[str] = []
    if schema_a is not None and schema_a != canonical:
        schema_warnings.append(f"a is {schema_a!r} (current is {canonical!r})")
    if schema_b is not None and schema_b != canonical:
        schema_warnings.append(f"b is {schema_b!r} (current is {canonical!r})")
    if schema_a is not None and schema_b is not None and schema_a != schema_b:
        schema_warnings.append(f"a ({schema_a!r}) and b ({schema_b!r}) use different schemas")

    # Build sections-by-name dicts for direct lookup.
    a_secs = {s.get("name"): s.get("status", "") for s in a.get("sections", [])}
    b_secs = {s.get("name"): s.get("status", "") for s in b.get("sections", [])}
    transitions = []
    for name in sorted(set(a_secs) | set(b_secs)):
        a_st = a_secs.get(name, "MISSING")
        b_st = b_secs.get(name, "MISSING")
        if a_st != b_st:
            transitions.append({"section": name, "from": a_st, "to": b_st})

    out = {
        "a_file": os.path.basename(a_path),
        "b_file": os.path.basename(b_path),
        "a_aggregate_ok": a.get("aggregate_ok", False),
        "b_aggregate_ok": b.get("aggregate_ok", False),
        "schema_a": a.get("schema_version", "?"),
        "schema_b": b.get("schema_version", "?"),
        "schema_warnings": schema_warnings,
        "transition_count": len(transitions),
        "transitions": transitions,
    }
    if json_mode:
        print(_json.dumps(out, indent=2))
        return 0
    print()
    print(f"  DOCTOR DIFF")
    print(f"    a: {out['a_file']}  (aggregate_ok={out['a_aggregate_ok']}, schema={out['schema_a']})")
    print(f"    b: {out['b_file']}  (aggregate_ok={out['b_aggregate_ok']}, schema={out['schema_b']})")
    print()
    # Emit schema warnings BEFORE the transition table (cont.16 contract; restored cont.21
    # after a regression that computed schema_warnings but never printed or JSON-emitted them).
    for w in schema_warnings:
        print(f"  [WARN] schema: {w}")
    if schema_warnings:
        print()
    if not transitions:
        print("  [PASS] no status transitions between these snapshots (workspace stable).")
        return 0
    print(f"  [INFO] {len(transitions)} section status transition(s):")
    for t in transitions:
        print(f"    {t['section']:<16} {t['from']:<8} -> {t['to']}")
    return 0


# ============================================================
# cmd_trend_doctor (added cont.18, refactored cont.21) -- per-section status breakdown over time window
#
# Reads all snapshots in the last N days (Nd format), groups by section name,
# and reports:
#   - status_counts: {OK: 12, FAIL: 2} -- how many snapshots had each status
#   - transitions:   number of consecutive status changes for this section
#                     (e.g. OK -> FAIL -> OK = 2 transitions; operator-visible flapping)
#
# Section-list drift (a section added/removed mid-window) is handled by treating
# missing sections as having literal "MISSING" status -- consistent with
# cmd_diff_doctor's behavior and surfaces the addition/removal in transition counts.
#
# cont.21 refactor: the section_history + section_stats build (~50 LOC) was extracted
# into _compute_window_section_stats() so cmd_trend_compare can reuse the same
# per-window stats without copy-pasting. The window-format parser was extracted
# into _parse_window_days() for the same reason.
#
# Flags:
#   --window Nd     time window (strict Nd format; e.g. 1d, 7d, 30d; default 7d)
#   --json          emit machine-readable JSON (CI-friendly)
# Exit codes:
#   0 = clean (snapshots in window OR empty window with [INFO])
#   1 = --window not in Nd format
# ============================================================
def _parse_window_days(window_str: str) -> Optional[int]:
    """Parse strict Nd format (e.g. 7d, 1d, 30d); return days as int, or None on invalid.

    Centralized so cmd_trend_doctor + cmd_trend_compare share the same parser.
    Strict format (just digits + 'd'); rejects '7', '7days', '1.5d', '', '0d'.

    '0d' is rejected (returns None) because:
      - cmd_trend_doctor: a 0d cutoff = now, so every snapshot is outside the
        window -- the user gets a silent 'no snapshots' which is misleading.
      - cmd_trend_compare: a 0d window would cause ZeroDivisionError in
        `transitions / days` for every section.
    The error message in the caller notes the 'Nd' format which implicitly
    excludes 0d.
    """
    m = re.match(r"^(\d+)d$", window_str or "")
    if not m:
        return None
    days = int(m.group(1))
    return days if days > 0 else None


def _compute_window_section_stats(sorted_snaps: List[Tuple[str, float]]) -> Dict[str, Dict]:
    """Build per-section history from a list of (filename, mtime) sorted ASC and
    compute status_counts + transition count per section.

    Reused by cmd_trend_doctor (single-window summary) and cmd_trend_compare
    (two-window A vs B comparison). See cmd_trend_doctor for the MISSING-status
    semantics for sections that disappear mid-window.
    """
    import json as _json
    section_history: Dict[str, List[Tuple[int, str]]] = {}
    for idx, (fn, _mt) in enumerate(sorted_snaps):
        try:
            with open(os.path.join(_snapshot_dir(), fn), encoding="utf-8") as _f:
                _data = _json.load(_f)
        except (OSError, _json.JSONDecodeError):
            continue
        present_names = set()
        for section in _data.get("sections", []):
            name = section.get("name", "?")
            status = section.get("status", "?")
            present_names.add(name)
            if name not in section_history:
                section_history[name] = []
            section_history[name].append((idx, status))
        for name in list(section_history.keys()):
            if name not in present_names:
                section_history[name].append((idx, "MISSING"))
    section_stats: Dict[str, Dict] = {}
    for name, history in section_history.items():
        status_counts: Dict[str, int] = {}
        transitions = 0
        prev_status: Optional[str] = None
        for _idx, status in history:
            status_counts[status] = status_counts.get(status, 0) + 1
            if prev_status is not None and prev_status != status:
                transitions += 1
            prev_status = status
        section_stats[name] = {
            "snapshot_count": len(history),
            "status_counts": status_counts,
            "transitions": transitions,
        }
    return section_stats


def cmd_trend_doctor(args: argparse.Namespace) -> int:
    """Aggregate per-section status breakdown + transition count over a time window."""
    import json as _json
    import time as _time

    window_str = getattr(args, "window", "7d")
    json_mode = getattr(args, "json", False)

    days = _parse_window_days(window_str)
    if days is None:
        print(f"  [FAIL] --window must be Nd format with days >= 1 (e.g. 7d, 1d, 30d; not 0d); got {window_str!r}")
        return 1
    cutoff = _time.time() - days * 24 * 3600

    # Get snapshots in window (mtime-based, uses MINOR #1 sort-by-mtime contract).
    snaps_in_window = [(fn, mt) for (fn, mt) in _list_snapshots() if mt >= cutoff]
    if not snaps_in_window:
        if json_mode:
            print(_json.dumps({"window_days": days, "snapshot_count": 0, "sections": {}}, indent=2))
        else:
            print()
            print(f"  TREND DOCTOR (window: {days}d, snapshots: 0)")
            print(f"  [INFO] no snapshots in last {days}d window")
        return 0

    # Sort by mtime ascending so the transition scan reads chronologically.
    sorted_snaps = sorted(snaps_in_window, key=lambda x: x[1])

    # cont.21 refactor: the section_history + section_stats build (50+ LOC) was
    # extracted into _compute_window_section_stats() so cmd_trend_compare can
    # reuse the per-window stats without copy-pasting.
    section_stats = _compute_window_section_stats(sorted_snaps)

    # --- Output rendering ---
    if json_mode:
        out = {
            "window_days": days,
            "snapshot_count": len(sorted_snaps),
            "sections": section_stats,
        }
        print(_json.dumps(out, indent=2))
        return 0
    print()
    print(f"  TREND DOCTOR (window: {days}d, snapshots: {len(sorted_snaps)})")
    print()
    print(f"  {'SECTION':<20} {'STATUS BREAKDOWN':<32} {'TRANSITIONS':<12}")
    print("  " + "-" * 64)
    for name in sorted(section_stats.keys()):
        s = section_stats[name]
        counts = s["status_counts"]
        breakdown = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
        print(f"  {name:<20} {breakdown:<32} {s['transitions']:<12}")
    print()
    return 0


# ============================================================
# cmd_trend_compare (added cont.21) -- compare per-section transition RATE between two windows
#
# Answers the operator question: "Is today more or less stable than the past week?"
# For each section that appears in either window, computes transitions/day for
# both windows and classifies as:
#   MORE_FLAPPING : rate_a > rate_b  (current window is flapping at a higher rate)
#   STABLE        : rate_a == rate_b
#   MORE_STABLE   : rate_a < rate_b  (current window is flapping at a lower rate)
#
# RATE-BASED (not raw) because the default --a=1d --b=7d has nested windows
# (1d is a subset of 7d in clock time). Raw comparison would make MORE_FLAPPING
# impossible for the default --a=1d --b=7d case (transitions in 1d <= transitions
# in 7d always). Rate normalization (transitions / days) makes the default useful
# AND any other window pair comparable on equal footing.
#
# Caveat: rate is transitions/day (NOT weighted by snapshot density). A section
# with sparse snapshots will show a low rate even if every transition is severe.
# Operators wanting density-aware comparison should compute it from the raw
# transitions_a/transitions_b/snapshot_count_* fields in --json output.
#
# Flags:
#   --a Nd        "current" window (default 1d; strict Nd format)
#   --b Nd        "baseline" window (default 7d; strict Nd format)
#   --json        emit machine-readable JSON (CI-friendly)
# Exit codes:
#   0 = clean (per-section verdict rendered; empty windows are [INFO] not [FAIL])
#   1 = invalid --a or --b format
# ============================================================
def cmd_trend_compare(args: argparse.Namespace) -> int:
    """Compare per-section transition RATE (transitions/day) between two time windows."""
    import json as _json
    import time as _time

    a_str = getattr(args, "a", "1d")
    b_str = getattr(args, "b", "7d")
    json_mode = getattr(args, "json", False)

    days_a = _parse_window_days(a_str)
    if days_a is None:
        print(f"  [FAIL] --a must be Nd format with days >= 1 (e.g. 1d, 7d, 30d; not 0d); got {a_str!r}")
        return 1
    days_b = _parse_window_days(b_str)
    if days_b is None:
        print(f"  [FAIL] --b must be Nd format with days >= 1 (e.g. 1d, 7d, 30d; not 0d); got {b_str!r}")
        return 1

    now = _time.time()
    snaps_all = _list_snapshots()
    snaps_a = sorted([(fn, mt) for fn, mt in snaps_all if mt >= now - days_a * 24 * 3600], key=lambda x: x[1])
    snaps_b = sorted([(fn, mt) for fn, mt in snaps_all if mt >= now - days_b * 24 * 3600], key=lambda x: x[1])

    # Reuse the per-window stats helper (cont.21 refactor extracted this from cmd_trend_doctor).
    stats_a = _compute_window_section_stats(snaps_a)
    stats_b = _compute_window_section_stats(snaps_b)

    # Per-section RATE comparison (transitions/day, NOT raw counts).
    # days_a/days_b are >= 1 by the strict Nd format, so no div-by-zero.
    all_sections = sorted(set(stats_a.keys()) | set(stats_b.keys()))
    comparison: Dict[str, Dict] = {}
    for name in all_sections:
        ta = stats_a.get(name, {}).get("transitions", 0)
        tb = stats_b.get(name, {}).get("transitions", 0)
        rate_a = ta / days_a
        rate_b = tb / days_b
        if rate_a > rate_b:
            verdict = "MORE_FLAPPING"
        elif rate_a < rate_b:
            verdict = "MORE_STABLE"
        else:
            verdict = "STABLE"
        comparison[name] = {
            "transitions_a": ta,
            "transitions_b": tb,
            "rate_a_per_day": round(rate_a, 4),
            "rate_b_per_day": round(rate_b, 4),
            "verdict": verdict,
        }

    # --- Output rendering ---
    if json_mode:
        out = {
            "window_a_days": days_a,
            "window_b_days": days_b,
            "snapshot_count_a": len(snaps_a),
            "snapshot_count_b": len(snaps_b),
            "sections": comparison,
        }
        print(_json.dumps(out, indent=2))
        return 0

    print()
    print(f"  TREND COMPARE (a: {days_a}d, b: {days_b}d, snapshots a: {len(snaps_a)}, b: {len(snaps_b)})")
    print(f"  (verdict based on RATE = transitions/day; raw counts shown in <count>/<days>d form)")
    print()
    if not all_sections:
        print(f"  [INFO] no sections to compare (both windows empty)")
        return 0
    print(f"  {'SECTION':<20} {'A (rate)':<14} {'B (rate)':<14} {'VERDICT':<14}")
    print("  " + "-" * 62)
    for name in all_sections:
        c = comparison[name]
        a_disp = f"{c['transitions_a']}/{days_a}d"
        b_disp = f"{c['transitions_b']}/{days_b}d"
        print(f"  {name:<20} {a_disp:<14} {b_disp:<14} {c['verdict']:<14}")
    print()
    return 0


# ============================================================
# cmd_launch_trend (added cont.19) -- 1-click trending wrapper
#
# Composes cmd_snapshot_doctor + sleep + cmd_snapshot_doctor + cmd_diff_doctor +
# cmd_trend_doctor into a single operator-facing subcommand. Useful for ad-hoc
# trending after operator-triggered workspace changes (e.g. after restarting a
# service): run launch-trend, wait a few seconds for the change to take effect,
# and the output shows the diff + trend without manually chaining commands.
#
# Flags:
#   --sleep N    seconds to sleep between A and B snapshots (default 2; int)
#   --window Nd  trend window (default 1d; strict Nd format)
#   --json       emit machine-readable JSON (composite of diff + trend under
#                'diff' + 'trend' keys; reuses existing cmd_diff_doctor +
#                cmd_trend_doctor --json shapes so CI consumers don't break)
# Exit codes:
#   max(snapshot_rc, diff_rc, trend_rc) -- propagates hard failures (file
#   read/write errors); expected health transitions stay rc=0.
# Side effects:
#   Writes to the REAL operator cache (%USERPROFILE%/.cache/war_room/snapshots/).
#   These snapshots ARE picked up by future trend-doctor calls -- this is the
#   intended enrichment of the long-term trending dataset.
# ============================================================
def cmd_launch_trend(args: argparse.Namespace) -> int:
    """Snapshot A + sleep + Snapshot B + diff + trend, in one call."""
    import time as _time

    sleep_seconds = int(getattr(args, "sleep", 2))

    # MINOR #2 (cont.19): validate --sleep is non-negative. argparse `type=int` accepts
    # negative values, but `time.sleep(-1)` raises ValueError. Cheap runtime check.
    if sleep_seconds < 0:
        print(f"  [FAIL] --sleep must be >= 0 (got {sleep_seconds})")
        return 1
    window_str = getattr(args, "window", "1d")
    json_mode = getattr(args, "json", False)

    if not json_mode:
        print()
        print(f"  LAUNCH-TREND (sleep: {sleep_seconds}s, window: {window_str})")
        print()

    # 1/4: snapshot A
    if not json_mode:
        print("  [1/4] snapshot A...")
    rc_a = cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=None, json=False))
    if rc_a != 0:
        return rc_a
    snaps = _list_snapshots()
    if not snaps:
        print("  [FAIL] no snapshot written (snapshot A)")
        return 1
    snap_a = snaps[-1][0]  # most-recent file (just written)

    # 2/4: sleep for state-change opportunity
    if not json_mode:
        print(f"  [2/4] sleeping {sleep_seconds}s for state-change opportunity...")
    _time.sleep(sleep_seconds)

    # 3/4: snapshot B
    if not json_mode:
        print("  [3/4] snapshot B...")
    rc_b = cmd_snapshot_doctor(argparse.Namespace(list=False, keep_last=None, json=False))
    if rc_b != 0:
        return rc_b
    snaps = _list_snapshots()
    snap_b = snaps[-1][0]

    # 4/4: diff + trend
    if json_mode:
        # CRITICAL fix (cont.19, after reviewer found): in json_mode, capture diff+trend
        # stdout to build a SINGLE composite JSON. Without this, the two subcommands each
        # print their own --json, resulting in 2 separate JSON objects (invalid JSON when
        # parsed as a single document). Capture via _capture_stdout() helper (cont.20
        # refactor: 2x duplicated StringIO + try/finally pattern consolidated into the
        # module-level @contextmanager), parse each, assemble composite, print once.
        import json as _json

        with _capture_stdout() as _buf_diff:
            rc_diff = cmd_diff_doctor(argparse.Namespace(a=snap_a, b=snap_b, json=True))
        with _capture_stdout() as _buf_trend:
            rc_trend = cmd_trend_doctor(argparse.Namespace(window=window_str, json=True))

        try:
            _diff_payload = _json.loads(_buf_diff.getvalue())
        except (_json.JSONDecodeError, ValueError) as _e:
            print(f"  [FAIL] cmd_diff_doctor --json returned non-JSON: {_e}")
            return 1
        try:
            _trend_payload = _json.loads(_buf_trend.getvalue())
        except (_json.JSONDecodeError, ValueError) as _e:
            print(f"  [FAIL] cmd_trend_doctor --json returned non-JSON: {_e}")
            return 1

        _composite = {
            "snapshots": {"a": snap_a, "b": snap_b},
            "diff": _diff_payload,
            "trend": _trend_payload,
        }
        print(_json.dumps(_composite, indent=2))
    else:
        print("  [4/4] diff + trend...")
        print()
        print("  === DIFF A vs B ===")
        rc_diff = cmd_diff_doctor(argparse.Namespace(a=snap_a, b=snap_b, json=False))
        print()
        print(f"  === TREND (window: {window_str}) ===")
        rc_trend = cmd_trend_doctor(argparse.Namespace(window=window_str, json=False))

    # Aggregate: max of subcommand rcs (propagates hard failures, expected
    # health transitions stay rc=0 per cmd_diff/cmd_trend's contract).
    return max(rc_a, rc_b, rc_diff, rc_trend)


# ============================================================
# cmd_launch_trend_compare (added cont.22) -- launch wrapper for cmd_trend_compare
#
# Answers: "Is the workspace degrading right now? Save a report and notify if so."
# Reuses cmd_trend_compare's rate-based verdict. Adds two operator-facing hooks:
#   --emit-report       write a .md + .json report to SLEEP_TRIPLE/outbox/trend_reports/
#   --alert-on-degraded if any section verdict == MORE_FLAPPING, fanout via opt_d_alerts.py
#
# WHY a wrapper (not just chaining trend-compare | opt_d_alerts):
#   - Single command captures the verdict, decides degraded-set, and conditionally
#     fires the alert -- the operator doesn't need to remember the exact JSON
#     filter ("verdict == MORE_FLAPPING") or the opt_d_alerts flag spelling.
#   - Keeps cmd_trend_compare pure (read-only); the new side effects (file write,
#     subprocess fanout) live entirely in this wrapper.
#   - Composable: --json mode emits a composite payload so CI consumers can
#     programmatically distinguish "degraded + alert fired" from "degraded + alert
#     suppressed (no degraded sections)".
#
# Flags:
#   --a Nd               pass-through to cmd_trend_compare (default 1d)
#   --b Nd               pass-through to cmd_trend_compare (default 7d)
#   --emit-report        write trend_reports/report__<stamp>.{md,json} to outbox
#   --alert-on-degraded  fire opt_d_alerts.py if any section is MORE_FLAPPING
#   --json               emit machine-readable composite (CI-friendly)
# Exit codes:
#   0 = trend-compare ran (with or without alert-fanout success). Alert DELIVERY
#       failures (opt_d_alerts missing / timed out) do NOT bump rc to 1 because
#       the trend-compare report was still produced -- the failure is a side-effect
#       failure, not a primary-output failure. To detect alert delivery failures
#       specifically, check the --json output's `alert_rc` field, OR rely on the
#       text-mode `[FAIL] alert not delivered:` line. CI consumers that need to
#       know "did the alert fire?" should key on `alert_rc`, NOT the main rc.
#       -- EXCEPT in the opt-in --strict-alert-rc mode (added cont.22 followups #2):
#       when set, an alert-DELIVERY failure (alert_fired=True AND alert_rc != 0)
#       bumps the wrapper rc to 1 so a strict-CI pipeline can fail loud.
#   1 = --a or --b invalid format, OR trend-compare failed internally, OR
#       outbox write failed, OR --strict-alert-rc was set and alert delivery
#       failed (opt-in strict mode only -- default rc=0 contract preserved)
# Side effects (when flags set):
#   - mkdir SLEEP_TRIPLE/outbox/trend_reports/ (idempotent)
#   - subprocess.run([sys.executable, opt_d_alerts.py, --msg, ...], timeout=30s)
#     -- ONLY when --alert-on-degraded AND degraded_sections is non-empty.
# ============================================================
def cmd_launch_trend_compare(args: argparse.Namespace) -> int:
    """Launch wrapper: run trend-compare, write outbox report, alert on degraded."""
    import json as _json
    from datetime import datetime as _dt

    a_str = getattr(args, "a", "1d")
    b_str = getattr(args, "b", "7d")
    emit_report = getattr(args, "emit_report", False)
    alert_on_degraded = getattr(args, "alert_on_degraded", False)
    strict_alert_rc = getattr(args, "strict_alert_rc", False)
    json_mode = getattr(args, "json", False)

    # Validate --a/--b upfront (clear error; avoids 0d ZeroDivisionError downstream).
    days_a = _parse_window_days(a_str)
    if days_a is None:
        print(f"  [FAIL] --a must be Nd format with days >= 1 (e.g. 1d, 7d, 30d; not 0d); got {a_str!r}")
        return 1
    days_b = _parse_window_days(b_str)
    if days_b is None:
        print(f"  [FAIL] --b must be Nd format with days >= 1 (e.g. 1d, 7d, 30d; not 0d); got {b_str!r}")
        return 1

    # Reuse cmd_trend_compare --json via _capture_stdout (DRY with cmd_launch_trend).
    with _capture_stdout() as _buf:
        _rc = cmd_trend_compare(argparse.Namespace(a=a_str, b=b_str, json=True))
    if _rc != 0:
        # Should be unreachable since we validated --a/--b above, but be defensive.
        print(f"  [FAIL] cmd_trend_compare --json returned rc={_rc}")
        return _rc
    try:
        _payload = _json.loads(_buf.getvalue())
    except (_json.JSONDecodeError, ValueError) as _e:
        print(f"  [FAIL] cmd_trend_compare --json returned non-JSON: {_e}")
        return 1

    # Identify degraded sections (verdict == MORE_FLAPPING).
    _sections = _payload.get("sections", {}) or {}
    _degraded: List[Tuple[str, Dict]] = [
        (name, sec) for name, sec in _sections.items() if sec.get("verdict") == "MORE_FLAPPING"
    ]

    # --- Step A: --emit-report (write .md + .json to outbox) ---
    _report_paths: List[str] = []
    if emit_report:
        _outbox_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "SLEEP_TRIPLE", "outbox", "trend_reports",
        )
        try:
            os.makedirs(_outbox_dir, exist_ok=True)
        except OSError as _e:
            print(f"  [FAIL] could not create outbox dir {_outbox_dir}: {_e}")
            return 1
        _stamp = _dt.now().strftime("%Y-%m-%d_%H%M%S")
        _md_path = os.path.join(_outbox_dir, f"report__{_stamp}.md")
        _json_path = os.path.join(_outbox_dir, f"report__{_stamp}.json")
        try:
            with open(_json_path, "w", encoding="utf-8") as _f:
                _json.dump(_payload, _f, indent=2)
        except OSError as _e:
            print(f"  [FAIL] could not write {_json_path}: {_e}")
            return 1
        # Build .md table mirroring cmd_trend_compare text output.
        _lines: List[str] = [
            "# Trend Compare Report",
            "",
            f"Generated: {_dt.now().isoformat(timespec='seconds')}",
            f"Window A: {days_a}d &middot; Window B: {days_b}d",
            f"Snapshots A: {_payload.get('snapshot_count_a', 0)} &middot; "
            f"Snapshots B: {_payload.get('snapshot_count_b', 0)}",
            "",
            "## Per-section verdict",
            "",
            "| Section | A (rate) | B (rate) | Verdict |",
            "|---------|----------|----------|---------|",
        ]
        for _name in sorted(_sections.keys()):
            _sec = _sections[_name]
            _lines.append(
                f"| {_name} | {_sec['transitions_a']}/{days_a}d "
                f"({_sec['rate_a_per_day']}/d) "
                f"| {_sec['transitions_b']}/{days_b}d ({_sec['rate_b_per_day']}/d) "
                f"| {_sec['verdict']} |"
            )
        if _degraded:
            _lines.append("")
            _lines.append(f"## \u26a0\ufe0f Degraded sections ({len(_degraded)})")
            _lines.append("")
            for _name, _sec in _degraded:
                _lines.append(
                    f"- **{_name}**: rate {_sec['rate_a_per_day']}/d (A) "
                    f"vs {_sec['rate_b_per_day']}/d (B)"
                )
        try:
            with open(_md_path, "w", encoding="utf-8") as _f:
                _f.write("\n".join(_lines) + "\n")
        except OSError as _e:
            print(f"  [FAIL] could not write {_md_path}: {_e}")
            return 1
        _report_paths = [_md_path, _json_path]

    # --- Step B: --alert-on-degraded (fire opt_d_alerts.py if degraded) ---
    _alert_fired = False
    _alert_rc: Optional[int] = None
    _alert_error: Optional[str] = None
    if alert_on_degraded and _degraded:
        _msg_parts = [
            f"[WARN] Workspace degraded ({len(_degraded)} section(s) MORE_FLAPPING):"
        ]
        for _name, _sec in _degraded:
            _msg_parts.append(
                f"  - {_name}: rate {_sec['rate_a_per_day']}/d (A) vs {_sec['rate_b_per_day']}/d (B)"
            )
        _alert_msg = "\n".join(_msg_parts)
        _opt_d = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "SLEEP_TRIPLE", "opt_d_alerts.py",
        )
        if not os.path.exists(_opt_d):
            _alert_error = f"opt_d_alerts.py not found at {_opt_d}"
            _alert_rc = 1
        else:
            try:
                _flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
                _res = subprocess.run(
                    [sys.executable, _opt_d, "--msg", _alert_msg, "--channel", "discord"],
                    capture_output=True, text=True, timeout=30, shell=False, creationflags=_flags,
                )
                _alert_rc = _res.returncode
                _alert_fired = True
            except subprocess.TimeoutExpired as _e:
                _alert_error = f"opt_d_alerts timed out: {_e}"
                _alert_rc = 1
            except OSError as _e:
                _alert_error = f"opt_d_alerts subprocess failed: {_e}"
                _alert_rc = 1

    # --- Output rendering ---
    if json_mode:
        _out = {
            "payload": _payload,
            "degraded_count": len(_degraded),
            "degraded_sections": [n for n, _ in _degraded],
            "report_paths": _report_paths,
            "alert_requested": alert_on_degraded,
            "alert_fired": _alert_fired,
            "alert_rc": _alert_rc,
            "alert_error": _alert_error,
        }
        print(_json.dumps(_out, indent=2))
        return 0

    print()
    print(f"  LAUNCH-TREND-COMPARE (a: {days_a}d, b: {days_b}d)")
    print()
    print(f"  degraded sections: {len(_degraded)}")
    if _degraded:
        for _name, _sec in _degraded:
            print(f"    - {_name}: rate {_sec['rate_a_per_day']}/d (A) vs {_sec['rate_b_per_day']}/d (B)")
    else:
        print("    (none -- workspace stable or improving)")
    if emit_report:
        print()
        print("  reports written:")
        for _p in _report_paths:
            print(f"    {_p}")
    if alert_on_degraded:
        print()
        if _degraded:
            if _alert_error:
                print(f"  [FAIL] alert not delivered: {_alert_error}")
            else:
                print(f"  [WARN] alert fired (opt_d_alerts rc={_alert_rc})")
        else:
            print("  [INFO] --alert-on-degraded: no degraded sections, no alert fired")
    print()

    # MINOR #1 (cont.22 followups #2): --strict-alert-rc opt-in ONLY mode.
    # Default rc=0 contract preserved (existing CI consumers keep the same
    # semantics). With --strict-alert-rc, an alert that FIRED but had a
    # non-zero subprocess rc bumps the wrapper rc to 1 -- so a strict CI
    # pipeline that needs "did the alert actually deliver?" can fail loud
    # instead of silently returning 0. An alert that was NOT FIRED (no
    # degraded sections) still returns rc=0 even under strict mode because
    # no delivery was attempted (= the delivery CELLS logic is irrelevant).
    # REVISION (reviewer-feedback MAJOR cont.22 followups #2): the condition now catches BOTH
    # delivery-failure modes (subprocess returned nonzero, OR opt_d_alerts script
    # missing/raised) when an alert was actually REQUESTED (alert_on_degraded=True
    # AND degraded_sections non-empty). The OLD condition short-circuited on
    # _alert_fired alone and silently returned rc=0 when opt_d_alerts.py was missing
    # -- violating the operator strict-mode 'fail loud if delivery did not happen'
    # contract. Tested by 3rd test test_strict_alert_rc_fails_when_opt_d_alerts_missing.
    _alert_was_requested = bool(alert_on_degraded) and bool(_degraded)
    _alert_delivery_failed = (
        _alert_error is not None
        or (_alert_fired and _alert_rc not in (None, 0))
    )
    if strict_alert_rc and _alert_was_requested and _alert_delivery_failed:
        print(f"  [FAIL] --strict-alert-rc: alert delivery failed (opt_d_alerts rc={_alert_rc}); bumping wrapper rc to 1")
        return 1
    return 0


# ============================================================
# Argparse
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="war_room",
        description="WAR ROOM operator CLI dispatcher — companion to WAR_ROOM.{md,html}",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_st = sub.add_parser("status", help="RSS-style status overview")
    sp_st.set_defaults(func=cmd_status)

    sp_ls = sub.add_parser("list", help="list all tiles (terse table)")
    sp_ls.set_defaults(func=cmd_list)

    sp_info = sub.add_parser("info", help="full record for one tile")
    sp_info.add_argument("tile", help="tile slug or partial name (e.g. 'vs-code', 'recon', 'telegram')")
    sp_info.set_defaults(func=cmd_info)

    sp_launch = sub.add_parser("launch", help="execute a one-click invocation (or --dry-run)")
    sp_launch.add_argument("tile", help="tile slug to launch")
    sp_launch.add_argument("--dry-run", action="store_true", help="print but don't execute")
    sp_launch.set_defaults(func=cmd_launch)

    sp_open = sub.add_parser("open", help="open WAR_ROOM.html (or WAR_ROOM_PUBLIC.html) in default browser")
    sp_open.add_argument("--public", action="store_true", help="open the public-shareable teaser")
    sp_open.set_defaults(func=cmd_open)

    sp_health = sub.add_parser("health", help="live TCP/HTTP probes for 5 local services (no browser)")
    sp_health.set_defaults(func=cmd_health)

    sp_vm = sub.add_parser("validate-mobile", help="verify MOBILE_FILTERED.csv dynamic tiles loaded (exit 0 if >=1, 1 otherwise)")
    sp_vm.set_defaults(func=cmd_validate_mobile)

    sp_vt = sub.add_parser("validate-tools", help="verify java/apktool/jadx install status (3-case FOUND/NOT_FOUND/BROKEN per tool)")
    sp_vt.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_vt.add_argument("--verbose", action="store_true", help="show captured version output (debugging)")
    sp_vt.set_defaults(func=cmd_validate_tools)

    sp_doc = sub.add_parser("doctor", help="aggregate workspace health check (validate-tools + health + git + Tools/ + MOBILE_FILTERED + ...)")
    sp_doc.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_doc.add_argument("--quiet", action="store_true", help="suppress per-section multi-line detail (badge-only)")
    sp_doc.set_defaults(func=cmd_doctor)

    sp_ob = sub.add_parser("archive-outbox", help="roll SLEEP_TRIPLE/outbox/* -> archive/outbox_YYYY-MM-DD/ (daily archive)")
    sp_ob.add_argument("--dry-run", action="store_true", help="list what WOULD happen without moving")
    sp_ob.add_argument("--keep-last", type=int, default=None, help="only archive files older than N days (default: archive all)")
    sp_ob.add_argument("--category", default=None, help="only archive one specific outbox subdir (e.g. e_pod)")
    sp_ob.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_ob.set_defaults(func=cmd_archive_outbox)

    sp_snap = sub.add_parser("snapshot-doctor", help="write .cache/war_room/snapshots/snapshot__DATE.json (cmd_doctor --json dump)")
    sp_snap.add_argument("--list", action="store_true", help="list existing snapshots (no write)")
    sp_snap.add_argument("--keep-last", type=int, default=None, help="prune oldest snapshots, keep N newest")
    sp_snap.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_snap.set_defaults(func=cmd_snapshot_doctor)

    sp_diff = sub.add_parser("diff-doctor", help="compare two snapshots by status transition per section")
    sp_diff.add_argument("--a", default=None, help="'a' snapshot (exact filename or date prefix, e.g. 2026-07-09)")
    sp_diff.add_argument("--b", default=None, help="'b' snapshot (defaults to most-recent)")
    sp_diff.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_diff.set_defaults(func=cmd_diff_doctor)

    sp_trend = sub.add_parser("trend-doctor", help="aggregate per-section status breakdown + transition count over a time window")
    sp_trend.add_argument("--window", default="7d", help="time window in Nd format (e.g. 1d, 7d, 30d; default 7d)")
    sp_trend.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_trend.set_defaults(func=cmd_trend_doctor)

    sp_launch = sub.add_parser("launch-trend", help="1-click trend: snapshot A + sleep + snapshot B + diff + trend")
    sp_launch.add_argument("--sleep", type=int, default=2, help="seconds to sleep between A and B snapshots (default 2; int)")
    sp_launch.add_argument("--window", default="1d", help="trend window (Nd format; default 1d)")
    sp_launch.add_argument("--json", action="store_true", help="emit machine-readable JSON (composite of diff + trend)")
    sp_launch.set_defaults(func=cmd_launch_trend)

    sp_compare = sub.add_parser("trend-compare", help="compare per-section transition RATE (transitions/day) between two windows (MORE_FLAPPING / STABLE / MORE_STABLE)")
    sp_compare.add_argument("--a", default="1d", help="'current' window in Nd format (e.g. 1d, 7d; default 1d)")
    sp_compare.add_argument("--b", default="7d", help="'baseline' window in Nd format (e.g. 7d, 30d; default 7d)")
    sp_compare.add_argument("--json", action="store_true", help="emit machine-readable JSON (CI-friendly)")
    sp_compare.set_defaults(func=cmd_trend_compare)

    sp_ltc = sub.add_parser("launch-trend-compare", help="launch wrapper: run trend-compare, write outbox report, alert if MORE_FLAPPING found")
    sp_ltc.add_argument("--a", default="1d", help="'current' window in Nd format (e.g. 1d, 7d; default 1d)")
    sp_ltc.add_argument("--b", default="7d", help="'baseline' window in Nd format (e.g. 7d, 30d; default 7d)")
    sp_ltc.add_argument("--emit-report", action="store_true", help="write a .md + .json report to SLEEP_TRIPLE/outbox/trend_reports/")
    sp_ltc.add_argument("--alert-on-degraded", action="store_true", help="fanout via opt_d_alerts.py if any section is MORE_FLAPPING")
    sp_ltc.add_argument("--strict-alert-rc", action="store_true", help="opt-in strict mode: return rc=1 if alert was REQUESTED and delivery failed (subprocess nonzero OR opt_d_alerts.py missing). Default (flag off): rc=0 even on delivery failure -- key on --json's alert_rc field instead.")
    sp_ltc.add_argument("--json", action="store_true", help="emit machine-readable JSON (composite: payload + degraded_count + report_paths + alert_fired)")
    sp_ltc.set_defaults(func=cmd_launch_trend_compare)

    return p

def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
