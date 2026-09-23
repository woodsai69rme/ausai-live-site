# bin/install_AUDIT_scheduler_RUNBOOK.md

Operator runbook for the **WarRoomDailyAuditPreFlight** scheduled task.

## What it does

Runs `bin\install_ALL_TASKS_AUDIT.bat` (the 14-test smoke-test runner) every day
at **06:00 local time**, before any other WarRoom scheduled tasks. The audit
ran via `python bin\run_audit_subprocess.py` (the **cont.16-fup-3** cross-platform
deadlock-free wrapper) which:

- prints an ISO timestamp preamble to `tmp\_wrap_out.txt` (via `--log-timestamp`)
- prints tail of the audit-runner's stdout (~20 lines) to systemd-event-log via schtasks
- exits with the audit's child rc (0 if all 14 T-cases PASS, non-zero on any FAIL)

If ANY T-case fails the operator will see the failure in tomorrow morning's
schtasks history (use Task Scheduler GUI or `schtasks /Query /TN WarRoomDailyAuditPreFlight`).

## Install (once, elevated cmd)

```cmd
cd C:\Users\karma
bin\install_AUDIT_scheduler.bat
```

Verify:

```cmd
schtasks /Query /TN WarRoomDailyAuditPreFlight /V /FO LIST
```

Confirm the action contains the `python bin\run_audit_subprocess.py --cmd "..."` line.

## Verify-flag tests (idempotent)

1. `--help` — flag inventory + exit 0
   ```cmd
   bin\install_AUDIT_scheduler.bat --help
   ```

2. `--dry-run` — previews the WOULD-BE schtasks invocation + does NOT modify
   any scheduler state. Run this BEFORE the bare install for safety.
   ```cmd
   bin\install_AUDIT_scheduler.bat --dry-run
   ```

3. `--status` — read-only Query (always rc=0 even if task absent)
   ```cmd
   bin\install_AUDIT_scheduler.bat --status
   ```

4. `--uninstall` — delete the task + exit 0 (idempotent: rc=0 even if absent)
   ```cmd
   bin\install_AUDIT_scheduler.bat --uninstall
   ```

## Day-of manual test-fire

Don't wait for 06:00 — manually fire the task to confirm end-to-end:

```cmd
schtasks /Run /TN WarRoomDailyAuditPreFlight
type tmp\_wrap_out.txt
```

Expect to see `AUDIT: 14 PASS, 0 FAIL (out of 14 tests)` near the end of `tmp\_wrap_out.txt`.

## Uninstall (idempotent)

```cmd
bin\install_AUDIT_scheduler.bat --uninstall
```

## How it differs from the nightly snapshot task

| Task                          | Schedule | Action                                       |
|-------------------------------|----------|----------------------------------------------|
| WarRoomDailyAuditPreFlight    | 06:00    | runs audit-runner only (and writes log)        |
| WarRoomNightlySnapshot        | 23:55    | runs `python war_room.py snapshot-doctor`     |
| WarRoomDailyTrendCompare      | 23:59    | runs `python war_room.py trend-compare`       |

The audit runs FIRST so a regression in the install surface is caught at the
start of the day, not at 23:55 when the snapshot writer would otherwise hit it.

## Distribution (cont.16-fup-6 -- PyInstaller --onefile)

The scheduled task action runs `bin\dist\run_audit_subprocess.exe` -- a **standalone
Windows .exe** produced by `bin\build_audit_exe.bat --rebuild` via PyInstaller
`--onefile`. This means:

- The box does NOT require Python installed at runtime for the 06:00 pre-flight
  to fire. The .exe is fully self-contained.
- Build steps for first-time install or after any edit to `bin\run_audit_subprocess.py`:

  ```cmd
  bin\build_audit_exe.bat --rebuild
  "%USERPROFILE%\bin\dist\run_audit_subprocess.exe" --help        :: smoke test
  bin\install_AUDIT_scheduler.bat --dry-run                       :: preview XML
  bin\install_AUDIT_scheduler.bat --uninstall                     :: clear cached XML
  bin\install_AUDIT_scheduler.bat                                 :: install (auto-elevates)
  ```

  `--uninstall` then bare-install ensures the cached temp XML in `%TEMP%` is
  fresh; the bare invocation re-creates the scheduled task bound to the new exe.

- The .exe is a per-machine release artifact (~6-10 MB). `bin/dist/`,
  `bin/build/`, and `*.spec` are `.gitignore`'d (Pass-15). Only the build
  script (`bin\build_audit_exe.bat`) is committed to the repo.
- Cold-start is ~0.5-2 s (PyInstaller self-extract to the user's TEMP dir) vs
  the 25-30 s wrapper measurement -- in the noise.

### Roll back to the legacy python invocation

If the rebuild is broken or the .exe is missing, edit `bin\audit_scheduler.xml`:

  - `<Command>bin\dist\run_audit_subprocess.exe</Command>` → `<Command>python</Command>`
  - `<Arguments>--cmd "bin\install_ALL_TASKS_AUDIT.bat" --log-timestamp --keep</Arguments>`
    → `<Arguments>bin\run_audit_subprocess.py --cmd "bin\install_ALL_TASKS_AUDIT.bat" --log-timestamp --keep</Arguments>`

Commit the revert, then `bin\install_AUDIT_scheduler.bat --uninstall` followed
by bare install.

## Cross-references

- `bin/install_BOTH_TASKS_DESIGN_NOTES.md` §7.2 — installer table + fup-5 row
- `bin/install_BOTH_TASKS_DESIGN_NOTES.md` §10 — deferred-bullet CLOSED
- `bin/install_ALL_TASKS_AUDIT_LOG.md` — Diagnostic footer: fup-3 wrapper as the winning approach
- `CHANGELOG.md` ## 2026-07-10 (cont.16-fup-5)
- `CHANGELOG.md` ## 2026-07-10 (cont.16-fup-6) -- PyInstaller --onefile migration
