# `.githooks/` — tracked git hooks (v3.3.1+)

Operator-installable hooks that bypass the **Windows + git-bash hook-subprocess
PATH-strip** problem by delegating to `pre-commit.bat` via `cmd.exe`.

The `.bat` runs in a fresh `cmd.exe` process that inherits the **full
Windows PATH**, so `where node` reliably finds the canonical Node install at
`C:\Program Files\nodejs\node.EXE`. This is the fix for the 3 pure-bash hook
rewrite attempts that failed empirically in the v3.3.0 closeout (see
`CHANGELOG.md` → `## 2026-07-13 (post-cont.5-fup-13)`).

---

## Install (Windows)

```cmd
bin\install_precommit_hook.bat
```

The installer prints the current `core.hooksPath` before doing anything.
**Heads up**: if your repo already has `core.hooksPath = .husky` (husky
workflow), the installer will warn and pause before overriding — press
Ctrl+C to keep husky, any key to override.

## Install (Unix / Linux / macOS)

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

(Unix path runs Stage A + Stage B directly in bash without `.bat`
delegation. Pure POSIX `command -v` + native `node` binary.)

## Uninstall

```bash
git config --unset core.hooksPath
```

Reverts to git's default `.git/hooks/` lookup.

---

## What the hook does

| Stage | Command | Catches |
|---|---|---|
| **A** | `node --check` syntax on staged `dashboards.mjs` + 3 HTML files | parse errors that would have `node` reject the file at load time |
| **B** | `node tools/test_dashboards.js` (16 cats, ~75 linkedom assertions) | functional regressions that `--check` cannot see: Cat 16 (v3.3 Spotlight Levenshtein fallback + history dropdown + Ctrl+H binding), Cat 10 (tab navigation Ctrl+1..9), Cat 11 (modal scroll-lock), Cat 14 (Ctrl+K Spotlight), etc. |

Both stages run ALWAYS — not gated on `git diff --cached`. Functional
regressions can leak through any refactor regardless of what was directly
touched.

---

## Why `.bat` delegation?

Pure-bash hook runs in **MSYS bash**, which strips PATH such that
`C:\Program Files\nodejs\node.EXE` is invisible to `[ -f ]` /
`command -v` / `which` / `type -p`. Three rewrite iterations empirically
failed with this exact root cause.

Delegating to `cmd.exe` via `cmd.exe /c .githooks\pre-commit.bat` runs
the hook in a **fresh process** inheriting the **full Windows PATH**, so
`where node` works correctly.

---

## Operator-side manual check (no git wiring)

If you don't want to install the git hook, you can still get the same
verification:

```cmd
bin\precommit_check.bat
```

This runs Stage A + Stage B directly via `cmd.exe`'s full PATH — useful
for pre-PR checks, batch CI, or one-off verification without modifying
git config.

---

## Files in this directory

| File | Role |
|---|---|
| `pre-commit` | cross-platform bash dispatcher (delegates to `.bat` on Windows) |
| `pre-commit.bat` | Windows `cmd.exe` thin wrapper → `bin\precommit_check.bat` |
| `README.md` | this file |

## Files in `bin/` (companion)

| File | Role |
|---|---|
| `bin/precommit_check.bat` | **canonical** Stage A + Stage B Windows runner (single source of truth) |
| `bin/install_precommit_hook.bat` | one-shot installer with husky-conflict warning |

---

## Cross-references

- `CHANGELOG.md` → `## 2026-07-13 (post-cont.5-fup-13)` — the 3 prior
  bash rewrite attempts + the trade-off consensus that motivated this.
- `bin/install_precommit_check.bat` (above).
- `TODO_TRACKER.md` — `## 🎯 FOLLOWUPS` (Outstanding pre-commit hook items).

---

## v3.3.2 paired-ack policy (BREAKING from v3.3.1)

The hatch env vars now require **paired opt-in** to defend against accidental
CI bleed-through / parent-shell env inheritance:

| Hatch | Required env vars |
|---|---|
| Bypass entire hook (Stage A + B) | `PRECOMMIT_BYPASS=1` **+** `PRECOMMIT_BYPASS_ACK=1` |
| Skip Stage B smoke only | `PRECOMMIT_SKIP_SMOKE=1` **+** `PRECOMMIT_SKIP_SMOKE_ACK=1` |

Setting just one env var returns **rc=2** with a clear FAIL message
instructing the operator to set the matching `_ACK=1` env var. Operators
upgrading from v3.3.1 (used single-var hatches) MUST add the _ACK env
var to their workflow. See `bin\install_precommit_hook.bat` DONE block
for copy-paste-able `set` commands.

Full rationale lives in `CHANGELOG.md` → `## 2026-07-13 (post-cont.5-fup-13)`.

---

## v3.4 (2026-09-24) -- Golden Rules Stage 0 guard (additive)

New file: `golden_rules_guard.sh` -- called at the TOP of `pre-commit`,
**before** the Windows `.bat` shim and **before** the paired-ack bypass
hatches, so it runs on every shell path and cannot be skipped by
`PRECOMMIT_BYPASS`. Implements .claude/GOLDEN_RULES.md as hard git law:

1. **Deletion block (Rules #1/#2/#5, NO bypass):** any staged change that
   removes a file from the working tree is refused. Detection is by disk
   presence: staged `D` + file absent on disk = commit deletes it = block.
   Index-only untracks (`git rm --cached`) are ALLOWED and logged --
   nothing is deleted from disk, so they are Rule-compliant.
2. **Personal-folder block (Rule #8, NO bypass):** any staged change under
   `Documents/`, `Downloads/` (incl. `ARCHIVE_OLD`), `Pictures/`,
   `Videos/`, `Music/`, `Desktop/`, `OneDrive/` is refused. Read/review
   only, per the permanent operator directive of 2026-07-13.
3. **Fail closed:** unexpected guard errors exit 2 and refuse the commit.

Exit codes: 0 pass / 1 hard block / 2 guard failure. Both blocks are
intentionally bypass-free; the only remedy is to not stage the change.

---

## v3.5 (2026-09-29) -- EOL-integrity check (additive)

Section 3 of `golden_rules_guard.sh` now also enforces the line-ending
policy documented in `MD_EOL_AUDIT_2026-09-29.md`:

1. **Mixed-EOL block (NO bypass):** any staged A/C/M/R/T file that is
   uniform in HEAD (pure LF, pure CRLF, or zero line endings) is refused
   if its staged blob is MIXED (contains both LF and CRLF endings).
2. **Pure conversions pass with a note:** whole-file LF<->CRLF flips are
   logged via `[golden-rules] NOTE:` but not blocked.
3. **Out of scope:** files already mixed in HEAD, brand-new files, and
   binary files (NUL sniff on the first 8 KB).
4. **Fail closed:** classification runs through `.githooks/eol_classify.py`
   (byte-capturing python subprocess -- MSYS text-mode redirection strips
   \r from scratch files, so pure-sh CR counting is unreliable here).
   A missing python degrades to a logged SKIP; classifier failure exits 2.

Exit codes unchanged: 0 pass / 1 hard block / 2 guard failure.

**Implementation note (2026-09-29, same day):** the first pure-sh classifier
passed syntax but failed every live block test: MSYS text-mode redirection
silently strips `\r` bytes from blob contents written to scratch files, so
the shell CR count was always 0. Classification now runs through
`.githooks/eol_classify.py`, which captures `git cat-file blob` output as
exact bytes via python subprocess (no text translation). The guard calls it
in batch and applies verdicts: `__MIXED__` = block, `__FLIP__` = note,
`__EOLERR__` = fail closed. Byte-exact evidence:
`BACKUPS/test_eol_guard_bytes_2026-09-29.py` (all cases pass, including a
real `git commit` refusal through the full hook chain).

## v3.6 (2026-09-30) -- read-only repo-wide EOL audit (`eol_audit.py`, additive)

`.githooks/eol_audit.py` is a **read-only census tool**. It is not part of the
commit path and is never invoked by the guard; run it by hand whenever you want
to know the current line-ending state of the repository.

It exists because the v3.5 guard is commit-time and staged-only: it can only see
files someone is about to commit. EOL drift that accumulates in the working tree
between commits is invisible until it is staged. This tool closes that gap.

It **never writes**, never stages, never touches the index or the working tree,
and creates no lock file. Safe to run at any time, including mid-edit.

### Usage

```
python .githooks/eol_audit.py              # census of the INDEX (default)
python .githooks/eol_audit.py --worktree   # census of WORKING-TREE bytes
python .githooks/eol_audit.py --mixed      # only the mixed files, with pin status
python .githooks/eol_audit.py --unpinned   # only mixed files with NO .gitattributes pin
python .githooks/eol_audit.py --md         # restrict to *.md
python .githooks/eol_audit.py --json       # machine-readable
python .githooks/eol_audit.py --check      # exit 2 if any mixed file exists
```

Exit codes: `0` = census produced, `1` = usage error, `2` = git failure or
`--check` found mixed files (fail closed).

### Interpreting the output

Each mixed file is annotated with its `.gitattributes` pin. A mixed file **with**
a pin is frozen by decision and is expected -- that is the settled state. The
files listed under "no pin" are the ones still awaiting a decision, and are the
short list to work through.

Categories: `lf`, `crlf`, `mixed`, `none` (empty), `binary` (NUL in first 8 KB),
and `gitlink` (submodule, mode 160000 -- no blob to read; not a defect).

### Performance note

The first implementation shelled out to `git cat-file` once per file, which cost
~3000 process spawns and took **over 48 seconds for a 524-file `--md` scan**.
It now reads every blob through a single `git cat-file --batch` pipe, and a full
3073-file census completes in **about one second**.

The revs must be written to that pipe *concurrently* with reading. Writing all
revs before reading any deadlocks, because this repo holds blobs of hundreds of
KB and the 64 KB pipe buffer fills before git can drain its output. The tool
uses a writer thread for exactly this reason -- do not "simplify" it back into a
sequential write-then-read loop.

### Current census (2026-09-30, verified)

| Source | mixed |
|---|---|
| index | 22 -- 19 pinned and frozen, 3 unpinned (in-flight user work) |
| worktree | 28 -- the extra 7 are unstaged in-progress edits, invisible to the commit-time guard |

Markdown-only: 1 mixed, `_DOCS_ARCHIVE/master_docs/FULL_REPO_AUDIT.md`, frozen
by an explicit `-text` pin. This matches `MD_EOL_AUDIT_2026-09-29.md` §9.
