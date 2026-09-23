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
