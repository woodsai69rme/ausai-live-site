# War-Room Nightly Snapshot — Operator Runbook

This runbook documents the install / verify / test / uninstall procedure for the nightly `war_room.py snapshot-doctor` scheduled task. The task fires at 23:55 daily, capturing real workspace state into the trending pipeline (`snapshot-doctor` + `diff-doctor` + `trend-doctor`).

## Pre-reqs

1. **Elevated cmd.exe**: `schtasks /Create` requires Administrator privileges.
2. **Python on PATH**: the scheduled task calls `python` directly. Operator's `C:\Users\karma` is the working directory; ensure `python` is accessible from that cwd.
3. **bin/ files present**:
   - `bin\install_nightly_snapshot.bat` — installer
   - `bin\verify_nightly_task.bat` — read-only check
   - `bin\nightly_snapshot.xml` — task template

## Install (one-time)

```cmd
cd C:\Users\karma
bin\install_nightly_snapshot.bat
```

Note on `StartBoundary` (CONT.14 footnote): the XML hardcodes
`<StartBoundary>2026-07-10T23:55:00</StartBoundary>` as the FIRST-fire date only;
daily recurrence continues thereafter via `<DaysInterval>1</DaysInterval>`. For
an install AFTER 2026-07-10, the task waits for the next daily 23:55 boundary --
this is by design. The XML also sets `<StartWhenAvailable>true</StartWhenAvailable>`
so missed runs (e.g. laptop asleep at 23:55) are caught up the next time the
system wakes. To force an immediate first fire for testing, run
`schtasks /Run /TN "WarRoomNightlySnapshot"` after install.

Expected output:

```
Installing scheduled task "WarRoomNightlySnapshot":
  template:   C:\Users\karma\bin\nightly_snapshot.xml
  USERPROFILE: C:\Users\karma
  (substituting hardcoded C:\Users\karma with %USERPROFILE% for portability)

[PASS] installed. Verify with:
  bin\verify_nightly_task.bat
  schtasks /Query /TN "WarRoomNightlySnapshot" /V /FO LIST
```

The `.bat` reads `bin\nightly_snapshot.xml` as a template, substitutes the hardcoded `C:\Users\karma` with the actual `%USERPROFILE%` via PowerShell `.Replace()` (literal string method, no regex), writes a temp XML, and runs `schtasks /Create /XML` (Win32 native API).

## Verify

```cmd
bin\verify_nightly_task.bat
```

If installed: prints full `schtasks /Query` output + `[PASS]`.
If not installed: prints `[INFO] Task "WarRoomNightlySnapshot" is NOT installed.` + exit 1.

## Test immediately (do NOT wait for 23:55)

```cmd
schtasks /Run /TN "WarRoomNightlySnapshot"
```

Then check the snapshot was captured:

```cmd
python war_room.py snapshot-doctor --list
```

A new `snapshot__<timestamp>.json` should appear. If it does, the task is fully functional.

## Validate the trending pipeline end-to-end

```cmd
python war_room.py trend-doctor --window 1d
```

Should show the captured snapshot in the trend output (1 snapshot in window, per-section status breakdown).

For a quicker sanity check that exercises the full snapshot+diff+trend pipeline in one call:

```cmd
python war_room.py launch-trend --sleep 0
```

This takes 2 back-to-back snapshots + diff + trend in one call. Should show "0 transitions" if the workspace is stable, or actual transitions if anything changed between the 2 snapshots.

**Note (cont.19 MINOR):** `launch-trend` writes 2 snapshots to the **real** operator cache (`%USERPROFILE%\.cache\war_room\snapshots\`) per invocation — intentional enrichment of the long-term trending dataset. If you run it many times, prune old snapshots with:

```cmd
python war_room.py snapshot-doctor --keep-last 30
```

## Uninstall

```cmd
schtasks /Delete /TN "WarRoomNightlySnapshot" /F
```

## Troubleshooting

### `ERROR: Access is denied.` from `schtasks /Create`

**Cause**: cmd.exe is not elevated (not running as Administrator).
**Fix**: Right-click cmd.exe → "Run as administrator", then re-run `bin\install_nightly_snapshot.bat`.

### `ERROR: Access is denied.` from `schtasks /Create` (CONT.14 clarification)

**Cause A (most common)**: cmd.exe is not elevated (not running as Administrator).
**Fix**: Right-click cmd.exe -> "Run as administrator", then re-run `bin\install_nightly_snapshot.bat`.
**Cause B (XML still wrong)**: the pre-flight schema test (added in cont.14, between
PowerShell substitution and the real schtasks /Create call) failed too;
the template-level error was masked by the elevation error. Re-run from an elevated cmd
to see the real schtasks error verbatim -- the `:schema_fail` banner prints the literal
schtasks error plus a Task Scheduler GUI `Import Task...` fallback.

### `No mapping between account names and security IDs` (FU1)

**Cause**: PowerShell `Register-ScheduledTask -Xml` (CIM API) fails on this host.
**Fix**: The `.bat` uses `schtasks /Create /XML` (Win32 native API) which bypasses this error. If you see this error, check that you're using `bin\install_nightly_snapshot.bat` (not a manual PowerShell command).

### Task fires but no snapshot appears in `snapshot-doctor --list`

**Cause 1**: cmd.exe session not running the task (laptop asleep at 23:55).
**Fix**: `StartWhenAvailable=true` in the XML catches up missed runs. Verify with:

```cmd
schtasks /Query /TN "WarRoomNightlySnapshot" /V /FO LIST
```

…then check `Last Run Time` + `Next Run Time`.

**Cause 2**: PowerShell call inside the task failed (e.g. `.Replace()` error).
**Fix**: Run `schtasks /Run /TN "WarRoomNightlySnapshot"` to trigger immediately, then check `python war_room.py snapshot-doctor --list`. If still no snapshot, the .bat's PowerShell substitution is failing silently. Re-run the .bat in a non-elevated cmd.exe to see the error message.

### Snapshots accumulate in `~/.cache/war_room/snapshots/`

**Not a bug**: snapshots are append-only by design (golden rules: append, preserve, protect). To prune old snapshots:

```cmd
python war_room.py snapshot-doctor --keep-last 30
```

Keeps the 30 most recent snapshots, deletes the rest.

## See also

- `bin\install_nightly_snapshot.bat` — installer (this runbook)
- `bin\verify_nightly_task.bat` — verify install
- `bin\nightly_snapshot.xml` — task template
- `python war_room.py snapshot-doctor --help` — subcommand help
- `python war_room.py trend-doctor --help` — trending help
- `python war_room.py launch-trend --help` — 1-click trend wrapper
- `python war_room.py diff-doctor --help` — snapshot-to-snapshot diff
