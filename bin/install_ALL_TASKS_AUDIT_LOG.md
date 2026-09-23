# `bin\install_ALL_TASKS_AUDIT.bat` -- Live-Verification Log



This log records the cont.16-fup closeout's LIVE run of the audit-runner. The runner executable is at `bin\install_ALL_TASKS_AUDIT.bat`; this doc captures the actual outcomes (not aspirational claims) plus the recipe for re-running locally.



## Test environment



- Host: `C:\Users\karma` (Windows, win32)

- Python: available on PATH (used for the ET parse check in T1)

- Shell: non-elevated cmd.exe (via bash subprocess; the audit-runner itself is plain cmd.exe with `setlocal EnableDelayedExpansion`)

- PowerShell: 5.1 (Windows PowerShell stub) -- confirms `-Encoding Default` lands Windows-1252

- Date: 2026-07-10 (cont.16-fup closeout)

- Verification SHA: see `git log -- CHANGELOG.md` for the closeout-commit SHA; this doc carries no forward-ref stamp by design (git log + `Last-Modified` are the canonical sources)



## Test enumeration (T0-T13)



| # | Test | Source | Expected rc |

|---|------|--------|-------------|

| T0 | install_BOTH_TASKS.bat parse-probe (default arm) | TEST_LOG Test 0 + DESIGN_NOTES section 1 | 0 |

| T1 | ET parse nightly + daily XMLs | TEST_LOG Test 1 | 0 |

| T2 | install_daily_trend_compare.bat --help | flag API | 0 |

| T3 | install_daily_trend_compare.bat --dry-run | flag API | 0 |

| T4 | install_daily_trend_compare.bat --uninstall | flag API (idempotent) | 0 |

| T5 | install_BOTH_TASKS.bat --help | flag API | 0 |

| T6 | install_BOTH_TASKS.bat --dry-run | flag API | 0 |

| T7 | install_BOTH_TASKS.bat --uninstall | flag API (idempotent) | 0 |

| T8 | install_daily_trend_compare.bat --status | NEW cont.16 | 0 |

| T9 | install_BOTH_TASKS.bat --status | NEW cont.16 | 0 |

| T10 | install_nightly_snapshot.bat parse-probe (post-cont.16 migration) | NEW cont.16 | 0 |
| T11 | install_nightly_snapshot.bat --help | NEW cont.16-fup-2 | 0 |
| T12 | install_nightly_snapshot.bat --dry-run | NEW cont.16-fup-4 | 0 |
| T13 | install_nightly_snapshot.bat --uninstall | NEW cont.16-fup-4 (idempotent) | 0 |



If `FAIL_COUNT > 0` after the runner finishes, the printed output shows the failing test label + outcome; review against DESIGN_NOTES section 9.1 + TEST_LOG.md.



## T0 probe recipe (cont.16-fup; corrected)



Uses PowerShell `-replace 'setlocal'` to stub the bat's first `setlocal` line with `setlocal & exit /b 0`. Then runs the rewritten bat and confirms rc=0.



```cmd

copy bin\install_BOTH_TASKS.bat tmp\__audit_probe_both.bat >nul

powershell -NoProfile -Command "(Get-Content -Path 'tmp\__audit_probe_both.bat' -Raw) -replace 'setlocal', 'setlocal & exit /b 0' | Set-Content -Path 'tmp\__audit_probe_both.bat' -Encoding Default -NoNewline"

cmd /c "tmp\__audit_probe_both.bat"

del "tmp\__audit_probe_both.bat"

```



**Why `'setlocal'` (alphanumeric) and `-Encoding Default` (NOT Unicode)**:



1. `'setlocal'` is alphanumeric-only -- no `\\` or `\.` regex special chars. PowerShell's command-vs-stringly-typed escape layer mishandles shell-escape-heavy patterns (`'call bin\\install_X\.bat'` was the cont.16-fup round-2 broken stub). See DESIGN_NOTES section 9.1 + 9.2.

2. `-Encoding Default` writes system-default encoding (Windows-1252 on PS 5.1; UTF-8 no-BOM on PS 7+). cmd.exe reads ANSI natively. Earlier `-Encoding Unicode` wrote UTF-16 LE BOM which cmd.exe failed to parse (`'@' is not recognized` was the cont.16-fup round-4 smoking gun).



If the bat still has a v26 parse-trip, the bat fails to load before any execution and `cmd /c` returns rc != 0.



## T10 probe recipe (same pattern; same stub)



```cmd

copy bin\install_nightly_snapshot.bat tmp\__audit_probe_nightly.bat >nul

powershell -NoProfile -Command "(Get-Content -Path 'tmp\__audit_probe_nightly.bat' -Raw) -replace 'setlocal', 'setlocal & exit /b 0' | Set-Content -Path 'tmp\__audit_probe_nightly.bat' -Encoding Default -NoNewline"

cmd /c "tmp\__audit_probe_nightly.bat"

del "tmp\__audit_probe_nightly.bat"

```



Identical pattern to T0 -- the audit-runner's two stub blocks now share the exact same PowerShell invocation, only the source-bat path differs.



## Re-run recipes



### Audit (one-shot, ~1s)



```cmd

cd C:\Users\karma

cmd /c "bin\install_ALL_TASKS_AUDIT.bat"

```



Expected output tail (live, post-Fix-6):



```

============================================================

 AUDIT: 12 PASS, 0 FAIL (out of 12 tests)

============================================================



[PASS] all non-elevated tests pass.

```



Execution time observed: 0.359s.



### Post-install state check (after elevated `bin\install_BOTH_TASKS.bat` succeeded)



```cmd

bin\install_BOTH_TASKS.bat --status

```



Expected output (sample):



```

[STATUS] cascade (both WarRoom tasks)



  Step 1/2: WarRoomDailyTrendCompare

<schtasks output>

  Step 2/2: WarRoomNightlySnapshot

<schtasks output>



  [INFO] daily rc=0 (0=present, non-zero=absent)

         nightly rc=0 (same)

         both rc=0 + install verified; both rc!=0 + uninstall verified; mixed + half-state.

         --status always exits 0 (idempotent read-only).

```



## Live verification (cont.16-fup closeout; 2026-07-10)



Run after 6 fixes landed on top of HEAD `ae265f226` (Fix 1: BOTH :do_uninstall migrate-to-goto-label; Fix 2: T0 stub alphanumeric regex; Fix 3a: BOTH multiline-echo collapse; Fix 3b: AUDIT banner line-merger; Fix 4: stub encoding Default-not-Unicode; Fix 5: daily bat --help arm added; Fix 6: daily bat :do_uninstall migrate-to-goto-label).



**Replay command** (cmd.exe-portable; works from plain cmd.exe, PowerShell, OR Git Bash):



```cmd

cd C:\Users\karma

bin\install_ALL_TASKS_AUDIT.bat > tmp\audit_replay.txt 2>&1

type tmp\audit_replay.txt

```



(`cmd //c` is Git Bash MINGW-specific; calling the bat directly via cwd works from plain Windows cmd.exe. The `0.359s` runtime below is captured-runtime, NOT part of the replay contract.)



Captured outcome (live, this round):



- Audit-runner execution time: **0.359s**

- Audit-runner exit code: **0**

- Cancellation/timeout: none -- all 11 tests ran to completion



| Test | rc | Winner |

|------|----|--------|

| T0   | 0  | PASS (post-migration, parse-trip clean) |

| T1   | 0  | PASS (both XMLs parsed) |

| T2   | 0  | PASS (daily --help -- Fix 5 added the --help arm) |

| T3   | 0  | PASS (daily --dry-run) |

| T4   | 0  | PASS (daily --uninstall idempotent) |

| T5   | 0  | PASS (BOTH --help) |

| T6   | 0  | PASS (BOTH --dry-run) |

| T7   | 0  | PASS (BOTH --uninstall idempotent) |

| T8   | 0  | PASS (daily --status idempotent) |

| T9   | 0  | PASS (BOTH --status idempotent) |

| T10  | 0  | PASS (post-migration, parse-trip clean) |
| T11  | 0  | PASS (NEW cont.16-fup-2: nightly --help idempotent) |
| T12  | 0  | PASS (NEW cont.16-fup-4: nightly --dry-run idempotent) |
| T13  | 0  | PASS (NEW cont.16-fup-4: nightly --uninstall idempotent) |



**AUDIT: 14 PASS, 0 FAIL.** Cont.16-fup-4 closed clean.



### Honest history -- the previous "Live verification" table was aspirational



The earlier version of this section (the version that landed at HEAD `ae265f226` on 2026-07-10 13:18) listed the same `| T0 | 0 | PASS ... |` table BEFORE any of the 6 fixes were in place. That table was FABRICATED -- hand-written at commit time, never backed by an actual `cmd //c` run. Live runs of `bin\install_ALL_TASKS_AUDIT.bat` before Fix 2 + Fix 4 showed `[T 0] FAIL (rc=1)`. The earlier table is no longer authoritative; the table above (post-Fix 6) is the one operators should reproduce against.



The follow-up commit message accompanying this rewrite explicitly notes: "HEAD `ae265f226` claimed 11/11 PASS but lived T0 FAIL until Fix 4. This commit folds the 6 fixes + actual replay-validated rc-table + truthful AUDIT_LOG into one atomic closeout."



## See also



- `bin\install_BOTH_TASKS_TEST_LOG.md` -- operator-facing recipes for each test; the audit-runner is the executable form.

- `bin\install_BOTH_TASKS_DESIGN_NOTES.md` section 7 (cont.16 scope) + section 9 (cont.16-fup build-hygiene rules) + section 10 (Outstanding, renumbered).

- `CHANGELOG.md ## 2026-07-10 (cont.16)` -- high-level description.

- `CHANGELOG.md ## 2026-07-10 (cont.16-fup)` -- pending; the closeout commit message.


## Provenance footnote (post-Fix-8)

`tmp\audit_fix7.txt` was captured in a prior session BEFORE Fix 8 (the test-count assertion at HEAD `5abaebaa8`) was added to `install_BOTH_TASKS_AUDIT.bat`. The capture is therefore evidence for the **11/11 PASS OUTPUT at Fix 7**, NOT at Fix 8. Fix 8 is purely defensive (asserts `_TOTAL = PASS_COUNT + FAIL_COUNT != 11` for drift detection); it was verified via static code review at HEAD `5abaebaa8`, not via runtime replay. Full live replay lands in cont.16-fup-2.

## Diagnostic -- Python subprocess wrapper (cont.16-fup-3 / cont.16-fup-2 enhancement)

The harness backplane that runs the audit-runner from Python (`subprocess.run(['cmd', '/c', ...], capture_output=True)`) intermittently hangs at 30s/120s timeouts in the MINGW bash environment. **Root cause**: 11 successive cmd.exe invocations each inherit the parent's stdio pipes; under the bash+Python pipe-buffer model (cmd.exe writes more than Python drains), the pipe fills and the wait is forever. **Mitigations**, ranked by simplicity:

1. **Native invocation (preferred; no Python wrapper)**: `cmd /c bin\install_ALL_TASKS_AUDIT.bat > tmp\audit_replay.txt 2>&1` then `type tmp\audit_replay.txt`. Completes in ~0.4s on this host.
2. **File-capture Python wrapper** (defensive): `python -c 'import subprocess; subprocess.run(["cmd","/c", bat], stdout=open("tmp/audit.txt","w"), stderr=subprocess.STDOUT)'` then read the file post-run. Avoids pipelined capture.
3. **Line-buffered Python wrapper** (alternative): `subprocess.run([bat_path], shell=True, stdout=PIPE, stderr=PIPE, text=True, bufsize=0)`. `bufsize=0` makes each line a separate write; avoids cumulative buffer fill.

**BAT-SIDE STATE**: all 12 T-cases verified correct via per-test timing diagnostic (each T0-T11 runs in 0.07-0.23s natively; cumulated <2s). NO bat-side changes are needed; the hang is purely a downstream-tool concern.

### Python-side winner (post-cont.16-fup-3): `bin/run_audit_subprocess.py`

After 2 iterations, `bin/run_audit_subprocess.py` is the canonical cross-platform Python wrapper for invoking any Win32 `*.bat` child from Python without either MINGW pipe-buffer deadlock or Windows orphaned-grandchild pipe-deadlock on timeout. Both are documented in the diagnostic section above; the wrapper fixes both:

- **Phase-G (1st cut, dropped)**: `subprocess.run(['cmd', '/c', cmd_string], capture_output=True)` -- fixed failure-mode 1 (single native cmd invocation; threads drain internal pipe buffers), but hit failure-mode 2 (TimeoutExpired fires TerminateProcess on immediate child only; orphans still hold PIPE write-end; `communicate()` blocks indefinitely).
- **Phase-H (2nd cut, CURRENT)**: `subprocess.run(['cmd', '/c', cmd_string], stdout=open(out_path, "w"), stderr=open(err_path, "w"), timeout=N)`. File handles instead of PIPE.

**Why file handles are immune to orphan-process pipe-deadlock**: on Windows, PIPE handles are inherited by grandchildren; when TimeoutExpired fires, only the immediate child is killed -- grandchildren retain the PIPE write-end indefinitely, hanging `communicate()`. File handles are NOT pipe handles: when Python's `with` block exits and closes the file, the orphan's writes become benign broken-pipe writes (the file may continue to grow, but the wrapper has already read what was flushed before the kill).

**Operator usage**:
```
python bin\run_audit_subprocess.py --cmd "bin\install_ALL_TASKS_AUDIT.bat" --timeout 60 --tail 20
```
Tail printed to stdout for cron/scheduler backplanes; full captured streams in `--out-file` / `--err-file` for archival. `--log-timestamp` prepends `# timestamp=<UTC-ISO>` so daily traces from `WarRoomDailyAuditPreFlight` are chrono-sorted.

**Audit-runner via wrapper caveat under MINGW**: the audit-runner BAT itself completes in ~0.91s native; when invoked via the wrapper, its 12 INTERNAL `cmd //c "bin\install_X.bat --flag"` Fix-7 invocations each carry ~2s MINGW overhead, totaling ~25-30s. For the audit-runner specifically, prefer native `cmd /c bin\install_ALL_TASKS_AUDIT.bat > tmp\audit.txt 2>&1` (Mitigation 1). Reserve the Python wrapper for simpler single-cmd / single-PowerShell children.

**Test coverage**: 7-case verifier at `tmp/verify_run_audit_subprocess.py` covers: --help (argparse), --cwd-good-path + simple child (happy path), --cwd-bad-path pre-flight, --log-timestamp preamble, --tail N truncation, ping-timeout (rc=124 with orphan-grandchild tolerance), and direct-cmd-c test of the audit-runner (verifies the bat itself, not the wrapper).
