# bin/rescue/ — gitignore rescue scripts

Reusable surgical scripts for fixing .gitignore issues that blocked source
files from being tracked in vendored subtree (ComfyUI/) during the
**cont.17-fup-3 rescue on 2026-07-11**. These were originally
`tmp/_gitignore_*.py` fossil files; promoted to version-controlled
`bin/rescue/` so future operators have them on hand if similar
blanket-ignore collisions re-emerge (e.g. another vendored project with an
embedded `.git/`).

## Scripts

### `fix_comfyui_blanket_ignore.py`

**When to use:** a vendored project (e.g. ComfyUI) is blanket-ignored at
the repo root and you need to track a specific source file inside that
subtree.

**What it does:** strips the blanket rule and appends per-subdir ignores
for the heavy-weight dirs only (`models/`, `custom_nodes/`, `output/`,
`input/`, `.git/`). Leaves operator-useful source files (e.g. `tools/*.py`,
`config/*.txt`) trackable.

**Idempotent:** safe to re-run. Exits `GITIGNORE_NO_OP` if already in the
precise state.

**Run from repo root:**

```bash
cd /path/to/repo
python bin/rescue/fix_comfyui_blanket_ignore.py
```

### `unblock_comfyui_case_insensitive_ignores.py`

**When to use:** `git check-ignore -v <file>` reports the file as NOT
IGNORED, but `git add -v <file>` silently prints NOTHING (exit code 0 but
no effect).

**The smoking gun** is case-insensitive gitignore patterns elsewhere in
the rule set (Windows `core.ignorecase=true`) that blanket-match the file's
parent directory. On Cont.17-fup-3 the offenders were:
- Line 300: `[C-c]onfig/` (case-insensitive bracket expression matching any
  `config*` directory at any depth)
- Line 830: `TOOLS/` (no-leading-slash depth-matcher matching any `tools*`
  directory at any depth)

**Strategy:** append surgical negation rules for the specific subtree you
want to unblock (`!/ComfyUI/tools/`, `!/ComfyUI/config/`) rather than
blanket-removing the offender (which would unblock ALL "config/" or
"tools/" directories across the repo — potentially leaking secrets, build
artifacts, etc.).

**Idempotent:** safe to re-run. Exits `GITIGNORE_UNBLOCK_NOOP` if rules
already present.

**Run from repo root:**

```bash
cd /path/to/repo
python bin/rescue/unblock_comfyui_case_insensitive_ignores.py
```

## Diagnostic commands (run BEFORE applying any fix)

If `git add` silently fails for a vendored file, walk through these:

```bash
# 1. Is .gitignore actually blocking it? (rc=0 = blocked; rc=1 = OK)
git check-ignore -v path/to/file

# 2. Is there a nested .git inside the vendored subtree?
#    If yes, parent repo treats the subtree as a NESTED REPO and refuses
#    to enumerate its contents -- this is THE smoking gun from cont.17-fup-3.
ls -la vendored_project/.git/ 2>&1 | head -5
cat .gitmodules 2>&1 | head -10    # if non-empty: it's a registered submodule

# 3. Is sparse-checkout picking anything up? (rc=1 = not configured)
git config --get core.sparseCheckout
cat .git/info/sparse-checkout         # list of allowed paths

# 4. Are there nested .gitignore files inside the vendored subtree?
#    Nested gitignores TAKE PRECEDENCE over parent negation rules.
for f in vendored_project/.gitignore vendored_project/tools/.gitignore vendored_project/config/.gitignore ; do
  if [ -f "$f" ]; then echo "=== $f ==="; cat "$f" | head -20; fi
done
```

## "Nested repo" workaround

If `vendored_project/.git/` exists (because the clone was made directly
into the workspace rather than via `git submodule add`), this is the
**specific scenario from cont.17-fup-3 rescue**. The parent git refuses to
enumerate the subtree's contents — `git add -v` exits 0 with no output.

**Fix:** rename (NOT `rm -rf`) — preserves upstream git data so the
operator can restore if needed.

*(Requires a POSIX-style shell with `$(date +...)` subshell — MINGW bash,
Linux/macOS shell. On Windows cmd.exe / PowerShell, use a literal date
string like `_dot_git_bak_20260711` instead.)*

**MINGW bash / Linux / macOS:**

```bash
# Rename for archaeology
mv vendored_project/.git vendored_project/_dot_git_bak_$(date +%Y%m%d)

# Then add a gitignore carve-out so the backup doesn't surface as ?? in
# every git status output:
echo "/vendored_project/_dot_git_bak_*/" >> .gitignore
```

**Windows cmd.exe / PowerShell:**

```cmd
:: Rename with literal date (no $() subshell)
move vendored_project\.git vendored_project\_dot_git_bak_20260711
echo /vendored_project/_dot_git_bak_*/>>.gitignore
```

Both scripts and this workaround were promoted from `tmp/` precisely
because this scenario will recur with future vendored dependencies.

## Cross-references

- `tmp/_gitignore_fix.py` and `tmp/_gitignore_unblock.py` — original
  one-shot versions (kept for archaeology; same logic as `bin/rescue/`).
- `git log --grep cont.17-fup-3` — the commits that recovered the 16
  OpenRouter refresh changes.
