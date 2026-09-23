# War-Room Both-Tasks Cascade -- Testable-Subset Verification Log

This log records the verification round for `bin\install_BOTH_TASKS.bat`'s flag
API (default + `--dry-run` + `--uninstall` + `--help`). The full cascade
(default install + real `schtasks /Create` + real `schtasks /Delete`) requires
**elevated cmd.exe** (Administrator) which the test harness does not have; the
non-elevated testable subset is run here, and the elevation-gated commands are
listed at the bottom with the expected outcome so the operator can re-run them.

## Test environment

- Host: `C:\Users\karma` (Windows, win32)
- Python: available on PATH (used for the `xml.etree.ElementTree` parse check)
- Shell: non-elevated cmd.exe (via bash subprocess)
- Date: 2026-07-10

## Test 0 -- parse-probe (no flags; verifies the bat LOADS without v26 parse-trip)

Without elevation, the default (no-flag) cascade call can't fully execute
(the sub-bats hit `schtasks /Create` which requires elevation). But if the
bat has a v26 `(...)` parse-trip bug, it FAILS TO LOAD before any label
executes -- the `cmd /c` host returns rc=1 with ": was unexpected at this
time.". To probe parse without elevation, this test stubs the sub-bat
calls via a sandbox copy and runs the real bat with no flags.

Probe (temp file in `tmp\probe_both.bat` is generated + cleaned up):

```cmd
copy bin\install_BOTH_TASKS.bat tmp\probe_both.bat
powershell -NoProfile -Command "(Get-Content -Path tmp\probe_both.bat -Raw) `
  -replace 'call bin\\install_daily_trend_compare\.bat', 'goto :after_daily_install' `
  -replace 'call bin\\install_nightly_snapshot\.bat', 'goto :after_nightly_install ^& exit /b 0' `
  | Set-Content -Path tmp\probe_both.bat -Encoding Unicode -NoNewline"
cmd /c "tmp\probe_both.bat"
```

Expected: rc=0; "Step 1/2: WarRoomDailyTrendCompare" + "Step 2/2:
WarRoomNightlySnapshot" + "[PASS] both tasks installed." printed (even
though no actual install happens because the sub-calls are stubbed).

If FAIL with rc=1 + ": was unexpected at this time.", the bat still
has a v26 `(...)` parse-trip that survived the v27 rewrite.

## Test 1 -- ET parse both task XMLs (safe; no scheduler changes)

```cmd
python -c "import xml.etree.ElementTree as ET; ET.parse(r'C:\Users\karma\bin\nightly_snapshot.xml'); ET.parse(r'C:\Users\karma\bin\daily_trend_compare.xml'); print('OK')"
```

Expected: `OK` printed, exit code 0.

If FAIL: there is a corruption in either `bin\nightly_snapshot.xml` or
`bin\daily_trend_compare.xml`. Re-run the fix from CHANGELOG ## 2026-07-09
(cont.14) which restores UTF-16-LE-BOM structure from the proven template.

## Test 2 -- sub-bat `--help` is safe (does not require elevation)

After this round the cascade accepts `--help`. Each sub-bat (`install_daily_trend_compare.bat`,
`install_nightly_snapshot.bat`) only enters its `:do_install` arm if no flag
matches, so calling them with `--help` is also safe.

## Test 3 -- `install_daily_trend_compare.bat --dry-run`

```cmd
bin\install_daily_trend_compare.bat --dry-run
```

Expected: prints WOULD-BE schtasks invocation, exit code 0, no scheduler changes.

## Test 4 -- `install_daily_trend_compare.bat --uninstall` (non-elevated)

```cmd
bin\install_daily_trend_compare.bat --uninstall
```

Expected: **exit code 0** with "[INFO] task was not installed or not
deletable; rc=1" printed INSIDE the bat's stdout. (The `:do_uninstall`
arm has UNCONDITIONAL `exit /b 0` -- this is the sibling bat's
documented symmetric idempotent UX; gaps don't bubble up as errors. The
rc=1 inside the message body is the underlying `schtasks /Delete` return
code, NOT the bat's own exit code.)

## Test 5 -- `install_BOTH_TASKS.bat --help`

```cmd
bin\install_BOTH_TASKS.bat --help
```

Expected: prints the flag inventory block, exit code 0.

## Test 6 -- `install_BOTH_TASKS.bat --dry-run`

```cmd
bin\install_BOTH_TASKS.bat --dry-run
```

Expected: prints Test 3 output (delegated to daily sub-bat) + synthetic nightly
preview + the 2-line PowerShell pre-flight hint (pasteable from elevated
cmd.exe), exit code 0.

## Test 7 -- `install_BOTH_TASKS.bat --uninstall` (non-elevated)

```cmd
bin\install_BOTH_TASKS.bat --uninstall
```

Expected: **exit code 0** with `[INFO] daily rc=...; nightly rc=...` message
(the `:do_uninstall` arm has UNCONDITIONAL `exit /b 0` -- "found but cannot
delete" is treated as idempotent-success). The underlying `schtasks /Delete`
return codes (rc=1 from either in non-elevated) are reported in stdout text
but do NOT cause a non-zero bat exit code.

## Elevation-gated (operator must run from elevated cmd.exe)

These are NOT run by the test harness; the operator runs them after the
non-elevated testable subset passes.

| Command                          | Requires elevated? | Expected outcome (elevated)                              |
|----------------------------------|--------------------|----------------------------------------------------------|
| `bin\install_BOTH_TASKS.bat`    | Yes                | Both tasks installed; `[PASS]` banner at end.            |
| `schtasks /Query /TN "WarRoomNightlySnapshot" /V /FO LIST` | No | Reads full task config; verify StartBoundary=23:55:00. |
| `schtasks /Run /TN "WarRoomNightlySnapshot"` | Yes   | Forces immediate fire; `snapshot-doctor` runs.           |
| `schtasks /Run /TN "WarRoomDailyTrendCompare"` | Yes | Forces immediate fire; report materializes in outbox/.   |
| `python war_room.py trend-doctor --window 7d` | No     | Verifies snapshots + reports pipeline end-to-end.        |
| `bin\install_BOTH_TASKS.bat --uninstall` (elevated) | Yes | Both tasks actually deleted; `[PASS] both tasks deleted.` |

## Notes on the PowerShell preview hint in `--dry-run`

The 2-line one-liner:

```
$xml = Join-Path $env:TEMP 'preview_nightly.xml'; Copy-Item bin
ightly_snapshot.xml $xml
$tn = 'PreviewNightly_' + [Guid]::NewGuid().ToString('N'); schtasks /Create /XML $xml /TN $tn /F; schtasks /Delete /TN $tn /F
```

deliberately uses `[Guid]::NewGuid().ToString('N')` rather than `.Guid` so the
GUID has NO hyphens (`N`-format = 32 hex chars, no dashes). `schtasks /TN`
rejects task names containing `-`, so a naively-formatted GUID would produce
"ERROR: The task name is invalid" -- this format avoids that trap.

The `$xml` variable is set on line 1 and consumed on line 2; no dead variables
and no redundant `Copy-Item`.

## Notes on the daily-fail and nightly-fail rollback wording

- **Daily-fail warning** (exit 1 from `install_daily_trend_compare.bat`):
  NO `schtasks /Delete` raw fallback printed -- daily install FAILED means no
  daily task exists, so a raw `/Delete` would return "Access is denied" on a
  non-existent task (misleading). Only points at the legitimate retry / bat
  uninstall.

- **Nightly-fail warning** (exit 1 from `install_nightly_snapshot.bat`):
  DOES include the raw `schtasks /Delete /TN "WarRoomDailyTrendCompare" /F`
  fallback -- daily WAS installed (so a rollback is legitimate) and if the
  bat's own `--uninstall` arm is broken for any reason, the raw fallback is a
  resilient cleanup route.

This asymmetric rollback wording matches the merge-fixup contract documented
by CHANGELOG ## 2026-07-09 (cont.14 v26) -- the file no longer accidentally
recommends deletion of a non-existent task.
