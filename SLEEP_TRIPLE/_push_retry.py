#!/usr/bin/env python3
"""Retry the push for the staged commit, preserving credential helper state."""
import subprocess

push = subprocess.run(
    ["git", "-C", r"C:\Users\karma", "push", "origin", "master"],
    capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"--- push rc={push.returncode} ---")
print(push.stdout)
print(push.stderr, file=__import__("sys").stderr)

log = subprocess.run(["git", "-C", r"C:\Users\karma", "log", "--oneline", "-3"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print("--- last 3 commits ---")
print(log.stdout)

# Show local vs remote
rev = subprocess.run(["git", "-C", r"C:\Users\karma", "rev-parse", "HEAD"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
remote = subprocess.run(["git", "-C", r"C:\Users\karma", "rev-parse", "origin/master"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
print(f"local HEAD:  {rev.stdout.strip()}")
print(f"remote HEAD: {remote.stdout.strip()}")
