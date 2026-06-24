# DOTDIR_CATALOG_RUN

```text
✅ COMPLIANCE — ADDITIVE ONLY
✔ Adds: NEW `DOTDIR_CATALOG_RUN.py` (first concrete dotdir catalog tool) + NEW `DOTDIR_CATALOG_RUN.md` (this doc).
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
```

A bounded audit that catalogs every dot-directory living directly under the
project workspace root, classifies each against a closed list of well-known
per-user IDE / AI-tooling directories, and emits an append-only JSONL summary
the operator can use to decide what new entries to add to `.gitignore`.

This tool belongs to the **ENH-H15 audit family** (sister tool to
`INDEX_DELTA_SCANNER.py`, `REALITY_VS_CLAIM_AUDIT.py`, `MASTER_INDEX_RECONCILER.py`).
It produces a structured catalog and a verdict per dotdir. It is intentionally
**read-only** when invoked with the default `--dry-run`; only an explicit
`--run` invocation writes anything to disk.

---

## 1. Why this exists

On Windows workstations, IDE and AI-coding tools write their state under
`C:\Users\<user>\.` paths. When a project is cloned into `C:\Users\<user>\<project>`,
those tool state directories sit **immediately next to** source code and
show up as untracked entries under `git status -uall`. The operator's natural
response is to add blocks of `.gitignore` rules, but to know what to add you
first need a list of what's actually there.

`DOTDIR_CATALOG_RUN.py` produces that list, classifies each entry against a
closed list of well-known per-tool names (so common candidates are `well_known_noise`
and ready to add), and surfaces anything not on the closed list as
`unclassified_per_user` so the operator decides consciously.

---

## 2. Closed set architecture

| Constant | Type | Cardinality | Purpose |
|---|---|---|---|
| `WELL_KNOWN_NOISE_DIRS` | `frozenset[str]` | ~110 entries | Per-user IDE / AI-tooling state. Names we KNOW should NEVER be committed. |
| `CLOSED_POSSIBLY_LEGIT` | `frozenset[str]` | 9 entries | Dot-named project artefacts that MUST NOT be auto-ignored (`.git/`, `.github/`, `.vscode/`, …). |
| `RULE_8_DIRS` | `tuple[str, ...]` | 8 entries | Personal / user folders the walker refuses to descend into. |
| `DOTDIR_CATALOG_ENUM` | `tuple[str, ...]` | 6 entries | The only legal row verdicts: `well_known_noise` / `unclassified_per_user` / `possibly_legit` / `refused` / `skipped` / `unverifiable`. |
| `TRACKED_DOTDIR_LOGS` | `frozenset[str]` | 1 entry | Append-only log files this tool concludes can be emitted (currently only `DOTDIR_CATALOG.log`). |

**Closed-set sync caveat (manual):** this file's `WELL_KNOWN_NOISE_DIRS` and
`.gitignore`'s per-user IDE/tooling block share the same set by intent.
If you grow one, grow the other in the same turn. Run
`python DOTDIR_CATALOG_RUN.py --dry-run` after edits to confirm any new
candidate renders as `well_known_noise` rather than `unclassified_per_user`.

---

## 3. Verdict enum (closed)

| Value | When emitted |
|---|---|
| `well_known_noise` | name is in `WELL_KNOWN_NOISE_DIRS` |
| `unclassified_per_user` | name starts with `.`, is on disk, but is NOT in well-known or possibly-legit sets |
| `possibly_legit` | name is in `CLOSED_POSSIBLY_LEGIT` |
| `refused` | workspace resolution matched `RULE_8_DIRS` |
| `skipped` | workspace exists but cannot be listed (`PermissionError`/`OSError`) |
| `unverifiable` | defensive fallback (currently unreachable on the happy path) |

`refused` and `skipped` are exit-code signals — they are NOT emitted per-row.
The verdicts emitted per-row on the happy path are exactly the first three.

---

## 4. Implementation notes

These two design decisions are recorded here so a future maintainer can see
WHY the implementation deliberately deviates from the naive defaults.

### 4.1 The 6-name intentional over-match silence

After the initial 81-name sweep, **6 entries** were promoted into
`WELL_KNOWN_NOISE_DIRS` and housed in a dedicated `INTENTIONAL_OVERMATCH`
frozenset, deliberately kept OUT of `.gitignore`'s per-user IDE/tooling
block because they could (in principle) over-match nested project subdirs
of the same name at the root of a workspace whose project IS the root:

- `.venv`
- `.vs`
- `.crawl4ai`
- `.keras`
- `.matplotlib`
- `.profiles`

Specifically, `.gitignore` patterns declared at a project root match every
file at-or-below that root — so a `.venv/` pattern at `/c/Users/karma/.gitignore`
would silently hide any `/c/Users/karma/<some-project>/.venv/` directory for
**all** subprojects, including legitimate per-project virtualenvs and cloned
Python sources.

`sync_warning` subtracts `INTENTIONAL_OVERMATCH` from its `only_in_python`
diff so those six names do NOT look like drift; the set is then consumed by
`parse_gitignore_noise_block` purely through the `.gitignore` block's actual
contents. Each subproject can opt-back-in by adding the same pattern to its
OWN `.gitignore`; the catalog will then classify it as `well_known_noise` on
the next run.

### 4.2 Close-fence parser assumption

`parse_gitignore_noise_block` is bracketed by:

- **ENTER** on any `#` comment line containing `NOISE_BLOCK_HEADING` (currently
  `"Per-user IDE/AI-tooling"`).
- **EXIT** on a pure-divider line matching the regex `^#\s*=+\s*$` — i.e. ONLY
  `#`, whitespace, and one or more `=` runs. No embedded content allowed.

If the noise block is opened but the close fence is missing before end-of-file,
the parser would otherwise silently scan the entire rest of the file. To
prevent that, `parse_gitignore_noise_block` returns a 3-tuple
`(names, found_block, found_close_fence)` and `sync_warning` emits a WARN if
`found_block=True and found_close_fence=False`. The fix: add a closing fence
(e.g. `# ============================================================`)
immediately AFTER the last noise name. The drift is recoverable without
losing data: add the fence and re-run.

---

## 5. I/O contract

### `--dry-run` (default)

- Walks workspace root one level deep (no recursion).
- For every direct-child name that begins with `.` AND exists on disk as a directory,
  emits a verdict and item-count.
- Prints tabular summary to stdout.
- Touches no files.

### `--run`

- Walks workspace as in `--dry-run`.
- APPENDS one ISO-prefixed JSONL row to `DOTDIR_CATALOG.log` in the workspace
  for every direct-child dotdir classified `well_known_noise`,
  `unclassified_per_user`, or `possibly_legit`.
- File handle is opened with `open(path, "a", encoding="utf-8")` only;
  the source script itself never opens the log read.
- Refuses to write under Rule #8 workspaces at all (exit 2).

### Refusal matrix (exits)

| Exit | Reason |
|---|---|
| `0` | Happy path (including skipped workspace on a `PermissionError`) |
| `2` | Workspace or workspace ancestor matches `RULE_8_DIRS` |
| `4` | Workspace does not exist on disk |
| `5` | `--emit-summary` was passed without `--run` (set by `REFUSAL_EXIT_CODE_MATRIX["emit_summary_without_run"]`) |
| `6` | Workspace exists but is not a directory |

`--dry-run` paired with `--run` is rejected by argparse itself (mutually
exclusive group) and never reaches the closure. The argparse conflict produces
its own exit (2), not the matrix exit 5. The matrix exit 5 is reserved for
the `--emit-summary`-without-`--run` semantic conflict.

---

## 5. Output schema

Each JSONL row carries:

| Field | Type | Notes |
|---|---|---|
| `ts_iso` | UTC ISO-8601 second precision | second-precision on purpose (other audit logs use the same) |
| `workspace` | str | absolute path of the workspace root that was scanned |
| `dotdir_name` | str | the bare name only (e.g. `.claude`) |
| `abs_path` | str | absolute path of the dotdir on disk |
| `item_count` | int | direct-child count (`-1` means the directory contents were unreadable) |
| `verdict` | enum | one of the 6 closed enum values |
| `gitignore_match` | bool | `True` iff verdict is `well_known_noise` |
| `detail` | str | short human readability hint |

Sister logs in the audit family: `REALITY_VS_CLAIM_AUDIT.log`,
`INDEX_DELTA.log`, `INDEX_DELTA_RECURSIVE.log`, `MASTER_INDEX_RECONCILER.log`,
`GAL_INTEGRITY_VERIFY.log`, `MCP_QUERY_AUDIT.log`, `MCP_HOST_HEALTH.log`,
`BACKUP_AUDIT.log`, `ENV_AUDIT.log`, `CROSS_AUDIT_DIFF.log`,
`APPEND_ONLY_HYGIENE_RUNNER.log`. The first `--run` of this tool produces the
first authoritative JSONL evidence that `MASTER_STATUS_DASHBOARD.md` can
mechanically include in its "what lives at root" section.

---

## 6. Usage

```bash
# Dry-run: prints summary only, no log written
python DOTDIR_CATALOG_RUN.py --workspace "C:\Users\karma" --dry-run

# Real run: appends JSONL rows to DOTDIR_CATALOG.log in the workspace
python DOTDIR_CATALOG_RUN.py --workspace "C:\Users\karma" --run

# Default workspace is CWD -- useful inside CI from the project root
python DOTDIR_CATALOG_RUN.py --run
```

Combination `--dry-run --run` is not a real flag pair: argparse puts
`--run` first as a `--dry-run` toggle, so passing `--run` flips `dry_run` to
`False`. To explicitly enable the writer, pass only `--run`. To explicitly
disable the writer, pass only `--dry-run` (or nothing).

---

## 7. Compliance footer

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW `DOTDIR_CATALOG_RUN.py`. Adds: NEW `DOTDIR_CATALOG_RUN.md`.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
```
