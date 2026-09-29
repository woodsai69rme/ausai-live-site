# HANDOFF — Repo-wide EOL hygiene & enforcement program (COMPLETE)

> Status as of **2026-09-30**. Branch `mr-wilson-v3-release`, fully synced with `origin`.
> Arc: audit -> pins -> Stage 0 hook enforcement -> per-file settlement plan -> settlements -> log -> commit -> push.
> Every step followed Golden Rules v1.1 (`.claude/GOLDEN_RULES.md`): nothing deleted, all files permanent,
> additive-only, personal folders read-only, backup before every edit, document everything.
>
> **Nothing is pending.** This file is the map. The full reasoning lives in `MD_EOL_AUDIT_2026-09-29.md`.

## 1. What was achieved

| Metric | Before | After (verified 2026-09-30) |
|---|---|---|
| Tracked files with mixed index EOL (`i/mixed`) | 26 | **22**, every one accounted for by decision |
| Tracked markdown with mixed index EOL | 5 | **1** (`FULL_REPO_AUDIT.md`, mixed *by policy*, forever) |
| `.gitattributes` surgical pins | 0 | **58** (32 `text eol=lf`, 7 `text eol=crlf`, 19 `-text`) |
| EOL drift blocked at commit time | none (advisory only) | **Stage 0 guard, hard-block, no bypass** |

The remaining 22 `i/mixed` files are intentional, not neglect:
- **19 are `-text` freeze pins** — bytes deliberately untouched, no conversion in either direction.
- **3 are in-flight user work**, left alone on purpose: `CUAI/core/vision_fleet.py`,
  `monetize-ai-engine/database.py`, `monetize-ai-engine/server.py`.
- The single mixed markdown is `_DOCS_ARCHIVE/master_docs/FULL_REPO_AUDIT.md`, frozen by pin.

69 uniform-CRLF markdown files (including `CHANGELOG.md`, `TODO_TRACKER.md`, `README.md`, `MEMORY/*`)
were deliberately **left unpinned** so no future filter pass can damage the append-only session logs.

## 2. Where the artifacts live

### Tracked (in git — the durable record)

| Artifact | Path | What it holds |
|---|---|---|
| **Full audit report** | `MD_EOL_AUDIT_2026-09-29.md` | The canonical document. §1 method, §2 findings (511 files), §3 the 5 mixed files, §4 the 30 pins, §5 change record, §6 out-of-scope, §7 non-md extension, §8 enforcement, §9 settlement plan. LF, 13,078 B. |
| **EOL policy pins** | `.gitattributes` | 58 surgical rules. Header **forbids wildcard rules** — extend by exact paths only, or you will mass-flip 75 LF `.bat` files. |
| **Stage 0 guard** | `.githooks/golden_rules_guard.sh` | §1 deletion block, §2 personal-folder block, §3 EOL-integrity block. Fail-closed, no bypass env var. |
| **EOL classifier** | `.githooks/eol_classify.py` | Byte-exact classifier. Self-serves `git diff-index --cached --name-status --diff-filter=ACMRT <tree-ish>`; emits `__MIXED__` / `__FLIP__` / `__EOLERR__`. |
| **Hook entry point** | `.githooks/pre-commit` | Invokes Stage 0 first, plus the `MSYS2_ARG_CONV_EXCL` fix and paired-ack hatches. |
| **Hook documentation** | `.githooks/README.md` | v3.4 = Stage 0 guard; **v3.5** = EOL-integrity check + implementation note. |
| **Session logs** | `CHANGELOG.md`, `TODO_TRACKER.md` | Append-only, uniformly **CRLF**. Top-of-stack / end-of-file entries per repo convention. |

### Untracked by design (gitignored `BACKUPS/` — the evidence trail)

`pre_eolguard_*`, `pre_harmonize_{REVENUE_GENERATORS_README,CLAUDE,DASHBOARD,MONETIZE_DOC}_2026-09-29.*`,
`pre_fullrepofreeze_gitattributes_2026-09-29`, `pre_md_eol_pins_gitattributes_2026-09-29`,
`pre_nonmd_pins_gitattributes_2026-09-29`, `pre_regdel_GITHUB_TOKEN_20260930-044444.txt`,
`harmonize_*.py`, `log_*.py`, `test_eol_guard_bytes_2026-09-29.py`, `test_eol_guard_2026-09-29.sh`.
These stay uncommitted by convention. `BACKUPS/` and `TOOLS/` were already gitignored.

## 3. The settlements (4 files converted + 1 frozen)

Each ran the identical byte-safe procedure: precondition md5 match -> backup -> byte-only conversion
-> minimal diff verification -> solo commit -> guard suite -> log entries.

| # | File | Action | Commit | Byte delta |
|---|---|---|---|---|
| 1 | `REVENUE_GENERATORS/README.md` | mixed -> **LF** | `f12ea0b67` | 1 CR removed, 5110 -> 5109 |
| 3 | `CLAUDE.md` | mixed -> **CRLF** | `f6ed68031` | +26 B (26-line island at 431-456; lines 1-430 byte-identical) |
| 4 | `DASHBOARD_ARCHITECTURE.md` | mixed -> **CRLF** | `9a2b5f403` | +15 B (15-line island at 60-74) |
| 2 | `DOCUMENTATION_AUTOMONETIZE_AI.md` | mixed -> **LF** | `c6af20fbd` | 1 CR, 6234 -> 6233 |
| 5 | `_DOCS_ARCHIVE/master_docs/FULL_REPO_AUDIT.md` | **frozen `-text`**, no byte change | `029e863a5` | 0 (config only) |

Full commit chain, oldest first:
`acce0b902` -> `4d7553262` -> `5b55c6524` -> `d8741f35a` -> `029e863a5` -> `f12ea0b67` -> `f6ed68031`
-> `9a2b5f403` -> `8013a5ba6` -> `c6af20fbd` -> `df42dfc78` -> `177a01228` -> `ef2d76c09`.

## 4. CRITICAL PLATFORM TRAP — read before any future EOL work

**MSYS / Git Bash text-mode redirection strips `\r` from scratch-file writes.** A pure-shell CR count over
`git cat-file blob` output therefore *always returns 0*. A pure-shell `classify_blob` implementation
passed `sh -n` syntax checking but **failed every live block test** for exactly this reason. That is why
`.githooks/eol_classify.py` is a native Python helper using byte-capturing subprocess.

**Corollary rule, absolute for this repo: never use `sed` / `awk` / `tr` or MSYS text-mode redirects on
these files. Python byte operations only.**

## 5. How the guard behaves (`.githooks/golden_rules_guard.sh` §3)

Runs at the very top of `.githooks/pre-commit`, ahead of the Windows `.bat` shim and the paired-ack
hatches, so it executes on every shell path and cannot be skipped by `PRECOMMIT_BYPASS`.

| Case | Result |
|---|---|
| Staged change turns a uniform file into mixed | **HARD BLOCK** |
| Pure LF <-> CRLF flip on a uniform file | NOTE only (informational) |
| File already mixed, or new, or binary | Out of scope (no block) |
| Classifier itself fails | exit 2 -> commit blocked (fail-closed) |
| Python missing from `PATH` | Logged SKIP, not a silent pass |

Chain order: `.husky/pre-commit` -> `.githooks/pre-commit` -> **Stage 0 guard** -> Windows `.bat` shim
(harmless `'#REM' is not recognized` stderr line is expected) -> Stage A `node --check` -> Stage B smoke.
`PRECOMMIT_SKIP_SMOKE` requires a paired `_ACK=1`.
Test suites: `BACKUPS/test_eol_guard_bytes_2026-09-29.py` and `test_eol_guard_2026-09-29.sh` —
byte-exact, all passing, and live-verified through a real refused `git commit`.

## 6. Follow-on cleanup (2026-09-30, same thread)

A stale, **invalid** 95-char fine-grained `GITHUB_TOKEN` was removed from `HKEY_CURRENT_USER\Environment`
(it had been shadowing the valid keyring credential and forcing an `env -u GITHUB_TOKEN` workaround on
every push). Backed up first to `BACKUPS/pre_regdel_GITHUB_TOKEN_20260930-044444.txt`.
Verified afterwards in a simulated fresh terminal: `GITHUB_TOKEN` undefined, `gh auth status` exit 0 as
`woodsai69rme` (keyring), `gh api user` -> `woodsai69rme`, and `git push` -> *Everything up-to-date*
**with no `env -u` workaround**. Pushes from now on need no prefix.

Caveats: terminals opened *before* the deletion still export the old value (environment is inherited at
process start) — restart them. The PAT value was printed to a terminal during the original lookup, so
treat it as exposed and revoke it at github.com/settings/personal-access-tokens.

## 7. Do not touch

- `START_MR_WILSON_ALL_SYSTEMS.bat` — the operator's own uncommitted edit (line 30, `&` -> `^&`). Never stage it.
- `monetize-ai-engine/*`, `CUAI/core/vision_fleet.py` — in-flight user work, deliberately unpinned.
- `CHANGELOG.md` / `TODO_TRACKER.md` — append-only. All log splices must be **CRLF**; anchors match the
  text *without* the trailing `\n`, then find the following `\r\n`.

## 8. Gotchas that cost time (worth inheriting)

- `write_file` intermittently fails with *"Invalid parameters… instructions: undefined"* when `content`
  precedes `path`. **Field order `path` -> `instructions` -> `content` always works.**
- `str_replace` fails on paths that `write_file` accepts — do a full rewrite instead.
- `read_files` returns `[BLOCKED]` for anything under `BACKUPS/` — read those via shell/python.
- Heredocs risk backslash mangling — stage text with `write_file`, then convert inside a python script.
- Plain `git add <path>` can be refused by a `.gitignore` **directory** rule for an already-tracked file
  (e.g. `REVENUE_GENERATORS/README.md`, dir rule at line 1162). Use `git add -u <path>` — tracked-only
  update, no force needed.
- `git ls-files --eol` shows the **index** (`i/`) keeping the old blob until staging. A converted worktree
  reads `i/mixed w/lf` *pre-stage*; the clean state only appears **after** `git add`.
- Backups and transcripts live in `BACKUPS/` and `TOOLS/`, which are gitignored — that is the convention,
  not an oversight.

## 9. If you extend this program

1. Audit with `git ls-files --eol`; never guess.
2. Add **exact-path** rules to `.gitattributes`. No wildcards, ever.
3. Back up the target, then convert with **python byte ops** (see the trap in §4).
4. Verify the diff is *minimal* — only the intended lines should move.
5. `git add -u` your file only. **Never `git add -A`** in this repo; other agents and the operator have
   uncommitted work in flight.
6. Solo commit, run both guard suites, then append the CRLF log entries.
