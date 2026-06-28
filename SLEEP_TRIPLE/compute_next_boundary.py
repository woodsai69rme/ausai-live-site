#!/usr/bin/env python3
"""
compute_next_boundary.py — emit the next sleep_window[0] in user-local HH:MM.

install_scheduler.bat captures this via `for /f` and passes it to
`schtasks /create /sc daily /st HH:MM`, so the nightly trigger fires at the
correct wall-clock moment regardless of what timezone the Windows box is set to.

Reads:
  C:\\Users\\karma\\SLEEP_TRIPLE\\sleep_config.json
Outputs to stdout:
  HH:MM (24-hour, suitable for schtasks /st).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CFG = Path(r"C:\Users\karma\SLEEP_TRIPLE\sleep_config.json")


def main() -> int:
    if not CFG.exists():
        print(f"compute_next_boundary: missing {CFG}", file=sys.stderr)
        return 1
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    tz_name = cfg.get("tz", "Australia/Sydney")
    window_start = cfg["sleep_window"][0]  # "HH:MM"
    try:
        hh, mm = map(int, window_start.split(":"))
    except (ValueError, AttributeError) as exc:
        print(f"compute_next_boundary: bad sleep_window[0] {window_start!r}: {exc}",
              file=sys.stderr)
        return 2
    tz = ZoneInfo(tz_name)
    now_tz = datetime.now(tz)
    # DST safety: detect two failure modes for non-23:00 windows.
    #   - Spring-forward gap: the requested wall-clock doesn't exist
    #     (Australia/Sydney: 02:00 jumps to 03:00). .replace() silently maps
    #     to post-transition, giving a 1-hour mis-fire. Verify by roundtripping.
    #   - Autumn-fallback overlap: 02:00–03:00 repeats once. fold=0 = pre-transition,
    #     fold=1 = post-transition. Pick fold=1 explicitly.
    fold0 = now_tz.replace(hour=hh, minute=mm, second=0, microsecond=0, fold=0)
    rt = fold0.astimezone(tz)
    if rt.hour != hh or rt.minute != mm:
        print(f"compute_next_boundary: non-existent time {hh:02d}:{mm:02d} on "
              f"{now_tz.date()} in {tz_name} (DST spring-forward gap); aborting.",
              file=sys.stderr)
        return 3
    fold1 = now_tz.replace(hour=hh, minute=mm, second=0, microsecond=0, fold=1)
    if fold0.utcoffset() != fold1.utcoffset():
        print(f"compute_next_boundary: DST-ambiguous {hh:02d}:{mm:02d} in {tz_name}; "
              f"using fold=1 (post-transition)", file=sys.stderr)
        target_tz = fold1
    else:
        target_tz = fold0
    if target_tz <= now_tz:
        target_tz += timedelta(days=1)
    target_local = target_tz.astimezone()
    sys.stdout.write(target_local.strftime("%H:%M") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
