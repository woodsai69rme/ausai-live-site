# Operator UAC Handoff: Cont.14 Finalization — Install BOTH `WarRoom*` Scheduled Tasks

**Status:** All required files are READY (commit `9005b47e1` for cont.14 nightly + commit `1702a64ac` for cont.13 daily + commit `dfd0dc6f6` for handoff doc refresh). Only the operator-side UAC handoff remains.

This runbook consolidates the `bin\install_nightly_snapshot.bat` (cont.14) and `bin\install_daily_trend_compare.bat` (cont.13) install paths into a single cascade the operator can complete from one elevated cmd.exe session. Each step is copy-paste ready with explicit expected output and what to do on failure.

## Pre-reqs (verify BEFORE UAC)

1. **Elevated cmd.exe available**: Both installs need Administrator. Right-click cmd.exe -> "Run as administrator". The bat auto-launches the UAC prompt, but you must accept it interactively from the prompt window.
2. **Python on PATH**: each scheduled task calls `python` directly. With your `C:\Users\karma` as the working directory, ensure `python` is callable from that cwd.
3. **Files present** (already committed):
   - `bin\nightly_snapshot.xml` (3736 bytes, UTF-16-LE-BOM, ET parse PASS) -- committed in `9005b47e1`
   - `bin\daily_trend_compare.xml` (5148 bytes, UTF-16-LE-BOM, ET parse PASS) -- committed in `1702a64ac`
   - `bin\install_nightly_snapshot.bat` (pre-flight schema test added) -- committed in `9005b47e1`
   - `bin\install_daily_trend_compare.bat` (pre-flight schema test added) -- committed in `1702a64ac`
   - `bin\validate_nightly_install.bat`, `bin\verify_nightly_task.bat` (read-only verifiers)
   - `bin\validate_daily_trend_compare.bat` (live-fire + count new-report validator)

## Sanity check BEFORE UAC (run from non-elevated cmd.exe)

```cmd
:: Verify both XML templates parse cleanly under stdlib ET
python -c "import xml.etree.ElementTree as ET; ET.parse(r'C:\Users\karma\bin\nightly_snapshot.xml'); ET.parse(r'C:\Users\karma\bin\daily_trend_compare.xml'); print('OK')"

:: Verify both bats parse cleanly (no v26 `(...)` parse-trip risk)
cmd /c "C:\Users\karma\bin\install_daily_trend_compare.bat --dry-run"
```

If the dry-run completes with `[DRY-RUN] WarRoomDailyTrendCompare (no install will happen)` then both bats are byte-for-byte clean. Skip to "The Cascade".

If either fails, do NOT proceed -- it means a hand-edit past the v26-friendly goto :label rewrite happened. Use git to inspect `bin\*.bat` and revert any offending change.

## The Cascade (single elevated session)

### Step 1: Install the daily trend-compare (cont.13 fix)

```cmd
cd C:\Users\karma
bin\install_daily_trend_compare.bat
```

Expected output (the bat's pre-flight schema test should pass with `[PASS] XML schema validation OK` before the real install):

```
[PASS] XML schema validation OK (test task created + cleaned up).

[PASS] installed. Verify with:
  schtasks /Query /TN "WarRoomDailyTrendCompare" /V /FO LIST
  bin\validate_daily_trend_compare.bat

To test immediately (does NOT wait for 23:59 trigger):
  schtasks /Run /TN "WarRoomDailyTrendCompare"
```

Then to see the captured report:

```cmd
dir /od /b "%USERPROFILE%\SLEEP_TRIPLE\outbox\trend_reports\report__*.md"
```

### Step 2: Live-validate the daily install

```cmd
bin\validate_daily_trend_compare.bat
```

This script:
1. Fires the task immediately via `schtasks /Run`.
2. Waits `WAIT_SECONDS` seconds (default 30; override via env var).
3. Counts reports before vs after; PASS if a new one materializes.

Expected: `[PASS] trend-compare task fired + captured a new trend report`.

### Step 3: Install the nightly snapshot (cont.14 fix)

```cmd
bin\install_nightly_snapshot.bat
```

Expected output (the bat's pre-flight schema test added in cont.14):

```
Installing scheduled task "WarRoomNightlySnapshot":
  template:   C:\Users\karma\bin\nightly_snapshot.xml
  USERPROFILE: C:\Users\karma
  (substituting hardcoded C:\Users\karma with %USERPROFILE% for portability)

[PASS] XML schema validation OK (test task created + cleaned up).

[PASS] installed. Verify with:
  bin\verify_nightly_task.bat
  schtasks /Query /TN "WarRoomNightlySnapshot" /V /FO LIST
```

### Step 4: Verify the nightly install + live test-fire

```cmd
bin\verify_nightly_task.bat
:: Expected: full schtasks /Query output + [PASS] Task is installed and enabled.
```

To bypass the 23:55 trigger and fire immediately:

```cmd
schtasks /Run /TN "WarRoomNightlySnapshot"
timeout /t 30 /nobreak >nul
python war_room.py snapshot-doctor --list
:: Expected: a new snapshot__<timestamp>.json appears in the listing.
```

### Step 5: Pipeline sanity check (end-to-end)

```cmd
python war_room.py launch-trend-compare --a 1d --b 7d --json
```

Expected: `degraded_count = 0` on a stable workspace. The `--json` flag returns a composite payload so you can distinguish "degraded + alert fired" from "degraded + alert suppressed".

This step proves both pipelines are end-to-end live: the 23:55 nightly snapshot populates trending and the 23:59 daily trend-compare consumes the freshest 1d/7d snapshot set.

## Uninstall (symmetric, idempotent)

```cmd
bin\install_daily_trend_compare.bat --uninstall
schtasks /Delete /TN "WarRoomNightlySnapshot" /F
```

Both are idempotent. The daily uninstall prints `[INFO] task was not installed or not deletable` if the task doesn't exist. The nightly uninstall via raw `schtasks /Delete` prints `ERROR: The system cannot find the file specified.` if the task doesn't exist.

## Failure modes

### Pre-flight schema test fails in any `bin/install_*.bat`

The XML is structurally invalid. The bat's `:schema_fail` banner prints the LITERAL schtasks error verbatim plus a clear WHAT/CAUSE/FIX block plus a Task Scheduler GUI `Import Task...` fallback. Use the GUI flow instead of static-XML install:

1. Open `taskschd.msc` (Task Scheduler).
2. Click "Import Task..." in the right rail.
3. Select the failed XML file.
4. In "Security Options" set "Run as" to your operator user; uncheck "Run whether user is logged on or not" if you want a quieter install.
5. Save with the documented task name (`WarRoomDailyTrendCompare` or `WarRoomNightlySnapshot`).

### `Access is denied` AFTER pre-flight passes

You're not in an elevated cmd.exe. Re-launch cmd.exe as Administrator. The pre-flight deliberately returns `Access is denied` on non-elevated shells because that's the success signal -- it means the XML is structurally valid and only the elevation gate is in the way.

### Both installs succeed but Step 5 fails (pipeline sanity check)

Pre-flight guards against SCHEDULER XML issues. Pipeline failure means the `war_room.py` SDK itself is misbehaving. Diagnostic entry point:

```cmd
python war_room.py health
python war_room.py status
python snapshot-doctor
```

This is NOT a cont.13 / cont.14 issue. Investigate the python subcommand plumbing directly.

### `schtasks /Run /TN "WarRoomNightlySnapshot"` returns nonzero in Step 4

**Cause A (most common)**: the task was registered successfully but cannot run `python war_room.py snapshot-doctor` because Python is not on the scheduler PATH. Test from the operator shell first:

```cmd
python war_room.py snapshot-doctor
```

If that fails with `ModuleNotFoundError` or `python is not recognized`, fix the PATH before re-running the schedule.

**Cause B**: scheduler-side ACL denied per `LASTEXITCODE=1`. Read `schtasks /Query /TN "WarRoomNightlySnapshot" /V /FO LIST` to see `Last Run Result`. If `0x1` (general failure), the `:schema_fail` issue resurfaced -- re-run the bat to re-validate the XML.

**Cause C (silent)**: `snapshot-doctor` ran but failed to write the snapshot file. Inspect `%USERPROFILE%\.cache\war_room\snapshots\` directly. Empty directory after a successful `schtasks /Run` means snapshot-doctor crashed mid-write; check `python` stderr via `schtasks /Query /TN ...` -> "Last Run Result" field.

## See also

- `daily_install_handoff.md` -- source-of-truth for the daily half (pre-dates this consolidate runbook; still canonical)
- `bin\install_nightly_snapshot_RUNBOOK.md` -- source-of-truth for the nightly half (also covers `--dry-run` arm in cont.13 daily sibling)
- `CHANGELOG.md` -- `## 2026-07-09 (cont.13)` + `## 2026-07-09 (cont.14)` for full XML-fix context
- WAR_ROOM.md (row added in this propagation round) -- the highest-level hub for both installers
