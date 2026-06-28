#!/usr/bin/env python3
"""
_test_dst.py — synthetic DST detection test for compute_next_boundary.py.

Runs three scenarios:
  1. Normal day: 23:00 AEST/AEDT in Australia/Sydney → rc=0 with HH:MM
  2. Spring-forward gap: 02:30 on 2026-10-04 (Sydney first Sunday in October) → rc=3
  3. Autumn-fallback overlap: 02:30 on 2026-04-05 (Sydney first Sunday in April) → rc=0 with fold=1 noted
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(r"C:\Users\karma\SLEEP_TRIPLE")
sys.path.insert(0, str(ROOT))
import compute_next_boundary as cnb  # noqa: E402

# Temporarily patch sleep_window[0] for tests 2 and 3.
CFG = cnb.CFG
ORIG_CFG = CFG.read_text(encoding="utf-8")


def run_scenario(label: str, mock_now_iso: str, mock_window: str) -> int:
    cfg_text = ORIG_CFG.replace('"sleep_window": ["23:00", "07:00"]',
                                f'"sleep_window": ["{mock_window}", "07:00"]')
    with patch.object(cnb, "CFG", CFG) as _:  # noqa: F841 — context unused
        pass
    # Patch the module's read by writing temp file works for our needs;
    # instead, patch json.loads to remap. Simpler: patch directly on CFG
    # by swapping read_text via monkeypatch on the module.
    with patch("compute_next_boundary.CFG") as mock_cfg:  # noqa: F841
        pass  # We'll just write the file for tests.

    print(f"\n=== {label} ===")
    print(f"  now = {mock_now_iso}, sleep_window[0] = '{mock_window}'")
    CFG.write_text(cfg_text, encoding="utf-8")
    try:
        mock_dt = datetime.fromisoformat(mock_now_iso)
        with patch("compute_next_boundary.datetime") as md:
            md.now.return_value = mock_dt
            md.side_effect = lambda *a, **k: datetime(*a, **k)
            rc = cnb.main()
        print(f"  result rc={rc} (captured stdout above)")
        return rc
    finally:
        CFG.write_text(ORIG_CFG, encoding="utf-8")


# Scenarios.
rc1 = run_scenario(
    "1. Normal day at 23:00 (today)",
    datetime.now(ZoneInfo("Australia/Sydney")).isoformat(),
    "23:00",
)
rc2 = run_scenario(
    "2. Spring-forward gap: 02:30 on 2026-10-04 (Sydney)",
    "2026-10-04T01:30:00+11:00",
    "02:30",
)
rc3 = run_scenario(
    "3. Autumn-fallback overlap: 02:30 on 2026-04-05 (Sydney)",
    "2026-04-05T01:30:00+10:00",
    "02:30",
)

print()
print(f"=== summary ===")
print(f"  scenario 1 (normal): rc={rc1}  expect 0  -> {'PASS' if rc1 == 0 else 'FAIL'}")
print(f"  scenario 2 (gap):    rc={rc2}  expect 3  -> {'PASS' if rc2 == 3 else 'FAIL'}")
print(f"  scenario 3 (overlap):rc={rc3}  expect 0  -> {'PASS' if rc3 == 0 else 'FAIL'}")

# Restore original CFG (defensive).
CFG.write_text(ORIG_CFG, encoding="utf-8")
