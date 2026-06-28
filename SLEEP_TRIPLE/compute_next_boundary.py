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

Return codes:
  0 — success.
  1 — sleep_config.json missing.
  2 — sleep_window[0] not parseable as HH:MM.
  3 — DST spring-forward gap (requested wall-clock doesn't exist on this date).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
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

    # DST safety: detect spring-forward gap (requested wall-clock doesn't
    # exist on this date) and autumn-fallback overlap (wall-clock exists
    # twice). Build naive datetime + ZoneInfo with explicit fold values so
    # the UTC instant is computed *from the requested wall-clock*. Crucially,
    # we DON'T use now_tz.replace(hour=hh) because that preserves the UTC
    # instant of "now" — astimezone() roundtrips to the same wall-clock
    # representation and the gap is unreachable. The naive-construct idiom
    # is the canonical zoneinfo way to surface non-existent local time.
    naive = datetime(now_tz.year, now_tz.month, now_tz.day, hh, mm,
                     second=0, microsecond=0)
    fold0 = naive.replace(tzinfo=tz, fold=0)
    fold1 = naive.replace(tzinfo=tz, fold=1)

    # Spring-forward gap detection: roundtrip through UTC. During gap the
    # naive+tinfo+fold=0 lands on a UTC instant that's *earlier* than the
    # minutes-math allows (because zoneinfo maps to pre-transition offset),
    # and astimezone(tz) re-renders that UTC instant in tz which lands at
    # a DIFFERENT wall-clock than the one we asked for.
    rt = fold0.astimezone(timezone.utc).astimezone(tz)
    if rt.hour != hh or rt.minute != mm:
        print(f"compute_next_boundary: non-existent time "
              f"{hh:02d}:{mm:02d} on {now_tz.date()} in {tz_name} "
              f"(DST spring-forward gap); aborting.", file=sys.stderr)
        return 3

    if fold0.utcoffset() != fold1.utcoffset():
        # Overlap (autumn fallback): wall-clock exists twice today; pick
        # the *later* UTC instant (fold=1 = post-transition) so the daily
        # recurrence keeps firing at the same wall-clock after DST ends.
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
