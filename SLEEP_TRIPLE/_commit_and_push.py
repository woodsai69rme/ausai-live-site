#!/usr/bin/env python3
"""Finalize SLEEP_TRIPLE wiring commit: cleanup test task + git push."""
import subprocess
from pathlib import Path

# 1. Remove any leftover schtasks test registration
r = subprocess.run(["schtasks", "/delete", "/tn", r"SLEEP_TRIPLE\Nightly_Test", "/f"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"cleanup rc={r.returncode}; stderr={r.stderr.strip()!r}")

# 2. Stage the SLEEP_TRIPLE files for this batch
files = [
    "SLEEP_TRIPLE/_verify_schtasks.py",
    "SLEEP_TRIPLE/sleep_orchestrator.py",
    "SLEEP_TRIPLE/opt_a_digital_factory.py",
    "SLEEP_TRIPLE/opt_b_faceless_shorts.py",
    "SLEEP_TRIPLE/opt_c_crypto_yield.py",
    "SLEEP_TRIPLE/dashboard_server.py",
    "SLEEP_TRIPLE/dashboard.html",
    "SLEEP_TRIPLE/install_scheduler.bat",
    "SLEEP_TRIPLE/uninstall_scheduler.bat",
    "SLEEP_TRIPLE/sleep_task.xml",
    "SLEEP_TRIPLE/launch_dashboard.bat",
]
add = subprocess.run(["git", "-C", r"C:\Users\karma", "add", "-f"] + files,
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"git add rc={add.returncode}; stderr={add.stderr.strip()!r}")

status = subprocess.run(["git", "-C", r"C:\Users\karma", "status", "--short"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
print("--- git status (cached) ---")
print(status.stdout)

commit = subprocess.run(
    ["git", "-C", r"C:\Users\karma", "commit", "-m", "feat: real APIs + scheduler + dashboard"],
    capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"--- commit rc={commit.returncode} ---")
print(commit.stdout)
print(commit.stderr, file=__import__("sys").stderr)

push = subprocess.run(["git", "-C", r"C:\Users\karma", "push", "origin", "master"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"--- push rc={push.returncode} ---")
print(push.stdout)
print(push.stderr, file=__import__("sys").stderr)

log = subprocess.run(["git", "-C", r"C:\Users\karma", "log", "--oneline", "-5"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print("--- last 5 commits ---")
print(log.stdout)
