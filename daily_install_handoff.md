# Operator UAC Handoff: Install `WarRoomDailyTrendCompare` scheduled task

**Status:** The `.bat` install pipeline is **READY** (commits up to `1702a64ac` cont.13 round XML Principal scrub + version=1.2 downgrade). Only the operator-side UAC handoff remains.

**Recent changes from CHANGELOG `## 2026-07-09 (cont.13)`:**
- `bin\daily_trend_compare.xml` -- Principal scrubbed to `<UserId>SYSTEM</UserId>` only (no LogonType / RunLevel / GroupId), `id="Author"` retained, `version="1.2"` (downgraded from `1.4` for `schtasks /Create /XML` legacy compatibility).
- `bin\install_daily_trend_compare.bat` -- pre-flight guard now creates a throwaway test task to validate the XML schema BEFORE attempting the real install; `:schema_fail` block emits fallback messages appropriate to each rejection category (value-format, elevation, node-order).
- `bin\nightly_snapshot.xml` flagged as **CORRUPTED** in the audit (fails ET parse + `schtasks` acceptance) -- separate followup, not silently fixed.

**Why this is operator-only:** `schtasks /Create /XML` requires Administrator privileges.
The bat auto-launches a UAC prompt (PowerShell `Start-Process -Verb RunAs`), but the
prompt windows cannot be programmatically accepted from a non-elevated shell.
The operator must run the bat *interactively* (no extra flags) in an elevated cmd.exe (or PowerShell).

---

## Pre-flight (sanity checks BEFORE UAC handoff)

```cmd
:: 1. Verify the XML template still parses (no encoding drift)
python -c "import xml.etree.ElementTree as ET; ET.parse('C:\Users\karma\bin\daily_trend_compare.xml')"

:: 1b. Verify the XML's top-level structure is in the v1.2 canonical order
::     (RegistrationInfo > Triggers > Principals > Settings > Actions) AND
::     the Principal element carries id="Author" (required by Actions Context="Author" IDREF).
python -c "import xml.etree.ElementTree as ET; r=ET.parse(r'C:\Users\karma\bin\daily_trend_compare.xml').getroot(); NS='{http://schemas.microsoft.com/windows/2004/02/mit/task}'; names=[c.tag.split('}')[-1] for c in r]; assert names==['RegistrationInfo','Triggers','Principals','Settings','Actions'], names; assert r.find('{%s}Principal' % NS[1:-1]).get('id')=='Author'"

:: 2. Verify the bat preview prints cleanly (no parser error)
cmd /c "C:\Users\karma\bin\install_daily_trend_compare.bat --dry-run"
::    Expected: [DRY-RUN] WarRoomDailyTrendCompare block + Schedule: 23:59 daily

:: 3. Verify the uninstall branch is idempotent
cmd /c "C:\Users\karma\bin\install_daily_trend_compare.bat --uninstall"
::    Expected: [INFO] task was not installed or not deletable; rc=1 (if not yet installed)

:: 4. Validate Task Scheduler v1.2 schema acceptance end-to-end (the new schema pre-flight).
::    Creates + immediately deletes a throwaway task from the same XML. If schtasks rejects,
::    the real install WILL fail the same way. The bat's pre-flight guard does this
::    automatically inside :do_install, but running it here catches the issue BEFORE
::    you spend UAC elevation on a bat that will fail.
powershell -NoProfile -Command "$tn='WarRoomDailyTrendCompare.PreFlight.'+(Get-Random); $tp=Join-Path $env:TEMP 'preflight_test.xml'; Copy-Item 'C:\Users\karma\bin\daily_trend_compare.xml' $tp -Force; try { schtasks /Create /XML $tp /TN $tn /F 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) { 'PASS: schema valid'; schtasks /Delete /TN $tn /F 2>&1 | Out-Null } else { 'FAIL: schtasks rejected the XML (rc='+$LASTEXITCODE+'). See :schema_fail fallback message in the bat for the GUI-import workaround.'; try { schtasks /Delete /TN $tn /F 2>&1 | Out-Null } catch {} } } finally { Remove-Item $tp -ErrorAction SilentlyContinue }"
```

All four steps must PASS before continuing to Step 1 (UAC install).

* If step 1b fails, the XML is in the wrong child order OR Principal lacks id="Author".
  Review the cont.23+ commit history; the fix procedure is documented in
  CHANGELOG.md `## 2026-07-09 (cont.13)` (or whichever cont.13+ section captured
  the wrap-in-Principals + id="Author" two-step).
* If step `--dry-run` exits non-zero or emits a `: was unexpected` parse error, do NOT
  proceed - the bat was modified past the v26-friendly goto :label rewrite.
* If step 4 fails with "value which is incorrectly formatted or out of range", the
  static-XML install path is blocked by schtasks' value-format check on
  `<UserId>S-1-5-4</UserId>` + `<LogonType>InteractiveToken</LogonType>`. The bat's
  :schema_fail block now prints a Task Scheduler GUI fallback (Import Task...,
  adjust Security Options). Use that to import manually, no console install possible.
* If step 4 returns "Access is denied", THE XML IS VALID -- this is the expected
  non-elevated response. Re-run the bat from an elevated cmd.exe (Administrator)
  in Step 1. The pre-flight schema guard correctly isolates XML-format errors from
  elevation errors by attempting the test-task creation.

---

## Step 1: Interactive install (UAC handoff)

Open `cmd.exe` (or PowerShell) **as Administrator**. Then:

```cmd
cd C:\Users\karma
bin\install_daily_trend_compare.bat
```

Expected output:

```
Installing scheduled task "WarRoomDailyTrendCompare":
  template:   C:\Users\karma\bin\daily_trend_compare.xml
  USERPROFILE: C:\Users\karma
  (substituting hardcoded C:\Users\karma with C:\Users\karma for portability)

[PASS] installed. Verify with:
  schtasks /Query /TN "WarRoomDailyTrendCompare" /V /FO LIST
  bin\validate_daily_trend_compare.bat

To test immediately (does NOT wait for 23:59 trigger):
  schtasks /Run /TN "WarRoomDailyTrendCompare"

To see the captured report afterwards:
  dir /od /b "%USERPROFILE%\SLEEP_TRIPLE\outbox\trend_reports\report__*.md"
```

If the install exits with `[FAIL] schtasks /Create returned errorlevel 1` — you're not in
an elevated shell. Right-click cmd.exe → "Run as administrator" → retry.

---

## Step 2: Verify install + capture a real snapshot

```cmd
:: Live verify the task is scheduled correctly
schtasks /Query /TN "WarRoomDailyTrendCompare" /V /FO LIST
::    Look for: Status = "Ready", Next Run Time = <tomorrow 23:59:00>, Last Run Result = ...

:: Or fire it immediately and watch the outbox materialize
schtasks /Run /TN "WarRoomDailyTrendCompare"

:: Wait 5-30 seconds for the python wrapper to finish, then check the most recent report
dir /od /b "%USERPROFILE%\SLEEP_TRIPLE\outbox\trend_reports\report__*.md"
::    Look for: a fresh report__<YYYY-MM-DD_HHMMSS>.md AND .json with matching timestamps
```

The `validate_daily_trend_compare.bat` script automates this dance — fires the task,
waits `WAIT_SECONDS` (default 30), counts reports before/after, prints PASS/FAIL.

---

## Strict-mode alert semantics (wired by default since 4df5a76d5)

The scheduled task runs in strict mode by default — `bin\daily_trend_compare.xml` `<Arguments>`
already includes `--strict-alert-rc`:

```
python war_room.py launch-trend-compare --emit-report --alert-on-degraded --strict-alert-rc --a 1d --b 7d
```

**What strict mode means:** when alert was REQUESTED (operator-set `--alert-on-degraded=True` AND
degraded_sections non-empty) but DELIVERY failed (subprocess nonzero OR `opt_d_alerts.py` missing),
the task exits `rc=1`. Task Scheduler's `Last Run Result` column will show `0x1` (= failed).

**Why this is the default:** the daily rate-comparison is the operator's primary SLA surface for
workspace degradation. Strict-mode rc=1 lets a future scheduled-task monitor catch delivery failures
without needing to parse `--json` output. Cost: noise on the schedule when `opt_d_alerts.py`
is misconfigured (no Discord webhook means delivery trivially fails).

**If you want default behavior (rc=0 on delivery failure; silent delivery failures):** remove
`--strict-alert-rc` from `<Arguments>`, then re-run the install (overwrites the task).

---

## Uninstall (if needed)

```cmd
:: Preferred: use the bat itself
bin\install_daily_trend_compare.bat --uninstall

:: Or directly:
schtasks /Delete /TN "WarRoomDailyTrendCompare" /F
```

Both are idempotent. The bat version reports `[INFO] task was not installed` if already gone.

---

## Outstanding side-effects (operator should know)

| # | Effect | Why it matters |
|---|---|---|
| 1 | Existing operators with OLD 23:57 install must re-run install to pick up new 23:59 schedule | The XML is the source of truth; the bat just wraps `schtasks /Create /XML` |
| 2 | `--strict-alert-rc` is now wired by default in the XML <Arguments> field (commit 4df5a76d5+) — strict-mode is the daily baseline. Override per operator in XML+re-install. | Wired by default per the reviewer's MAJOR flag in cont.22+ followups #4 |
| 3 | `WarRoomNightlySnapshot` is a separate task at 23:55; the daily trend-compare at 23:59 consumes the freshest snapshot set | 4-min buffer (was 2 min) covers slow-disk snapshots |

---

## Failure modes + fixes

| Symptom | Cause | Fix |
|---|---|---|
| `[FAIL] schtasks /Create returned errorlevel 1` | Not in elevated cmd.exe | Re-launch cmd.exe as Administrator |
| `[FAIL] %TEMPLATE% not found` | `daily_trend_compare.xml` not in same dir as the bat | Restore XML to `bin\` |
| `[FAIL] PowerShell substitution failed` | `_Replace()` error on the XML | Re-save XML as UTF-16-LE BOM (PowerShell default from `Get-Content ... -Encoding Unicode`) |
| `[FAIL] temp XML not written` | PowerShell silent failure | Inspect the bat's `%TMP_PS_OUT%` log for actual error |
| Reports materialized but FORMAT broken | Operator saved XML as UTF-8 instead of UTF-16 | Re-save XML with `-Encoding Unicode` |
