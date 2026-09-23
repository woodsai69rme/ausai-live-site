# Canonical Test Runner

> All 4 active test suites, their invocation modes, and the scoreboard.
> Last verified: 2026-07-01, HEAD `2d354a107`.

## Scoreboard

| Suite | File | Tests | Module invocation | File-canonical invocation |
|---|---|---|---|---|
| Monitor regression | `SLEEP_CASH_API/test_monitor.py` | 23 | `python -m unittest SLEEP_CASH_API.test_monitor` | ⚠️ BROKEN (relative import — use module invocation) |
| SLEEP_TRIPLE preflight | `SLEEP_TRIPLE/test_preflight.py` | 24 | `python -m unittest SLEEP_TRIPLE.test_preflight` | `python SLEEP_TRIPLE/test_preflight.py` |
| SLEEP_TRIPLE opt-e | `SLEEP_TRIPLE/test_opt_e_pod.py` | 10 | `python -m unittest SLEEP_TRIPLE.test_opt_e_pod` | `python SLEEP_TRIPLE/test_opt_e_pod.py` |
| YouTube transcript API | `SLEEP_CASH_API/test_yt_transcript_api.py` | 10 | `python -m unittest SLEEP_CASH_API.test_yt_transcript_api` | `python SLEEP_CASH_API/test_yt_transcript_api.py` |
| **TOTAL** | | **67** | | |

## Invocation-mode pitfall

`python -m unittest <module>` and `python <file>.py` do NOT behave identically for
`SLEEP_CASH_API/test_monitor.py`.

- **File-canonical** (`python SLEEP_CASH_API/test_monitor.py`): **BROKEN since
  `__init__.py` was added** (relative import `from . import monitor` not allowed in
  `__main__` scripts). Per golden rule "break things to improve them" — the old
  `sys.path.insert` shim and `import monitor` were deprecated when `__init__.py`
  made it a proper package.
- **Module invocation** (`python -m unittest SLEEP_CASH_API.test_monitor`): works
  because `from . import monitor` resolves through the package `SLEEP_CASH_API`
  (Python's `-m` flag adds the package root to `sys.path`).

**For test_monitor, only run `-m unittest`** after the `__init__.py` addition.
The other 3 suites support both invocation modes.

## One-liner regression

```bash
python -m unittest SLEEP_CASH_API.test_monitor SLEEP_TRIPLE.test_preflight SLEEP_TRIPLE.test_opt_e_pod SLEEP_CASH_API.test_yt_transcript_api -v 2>&1 | tail -5
```

Expect: `OK (67 tests)` or `Ran 67 tests ... OK`.

## Adding a new suite

1. Add a row to the scoreboard table above.
2. Verify the suite passes under **both** invocation modes.
3. If the suite imports from a sibling `.py` file (like `import monitor`), add the
   `sys.path.insert` pattern or add `__init__.py` to make it a proper package.
4. Update the one-liner regression command.
