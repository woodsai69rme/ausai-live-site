# AUDIT — Markdown EOL audit of all tracked `*.md` (2026-09-29)

**Scope:** all 511 tracked `*.md` files, enumerated via `git ls-files --eol -- '*.md'`.
**Trigger:** the 2026-09-26 CHANGELOG.md EOL incident (an awk pipeline stripped CRLF
repo-wide before byte-repair) — this audit checks whether any other tracked markdown
carries mixed or phantom-prone line endings, and pins what needs pinning.
**Companion change:** `.gitattributes` (+44/−0, surgical pin block, see §4).
**Golden Rules:** additive-only; `.gitattributes` edited by byte-pure append with a
verified backup; nothing deleted, nothing re-normalized, no file content touched.

---

## 1. Method

1. `git ls-files --eol -- '*.md'` — index (i/) vs worktree (w/) EOL state per file.
2. `git status --porcelain` cross-check — every flagged file confirmed clean before
   any pin was added (no hidden content changes were papered over).
3. Byte-level spot checks: `head -c … | od -c`, `git cat-file blob`, `git hash-object`
   vs `git rev-parse HEAD:<path>`, `git ls-files --debug` (cached stat), and a forced
   `git update-index --really-refresh` no-op test.
4. Attribute stack: root `.gitattributes`, nested `original_archon/.gitattributes`,
   `.git/info/attributes` (absent), `core.attributesfile` (unset), global
   `C:/Users/karma/.gitattributes` (bat/license pins only, no `.md` rules).
5. Conversion config: `core.autocrlf=false`, `core.eol` unset, `core.safecrlf` unset,
   `core.checkStat`/`core.trustctime` unset (defaults), `core.fileMode=false`.

## 2. Findings (511 files)

| Class | Count | Disposition |
|---|---|---|
| `i/crlf` (uniform CRLF in index) | 69 | **Left unpinned** — incl. `CHANGELOG.md`, `TODO_TRACKER.md`, `README.md`, `_DOCS_ARCHIVE/*`, `MEMORY/kilo_sessions/*`, `*/graphify-out/*`. A `text`/`eol` attribute would put every future commit through a filter pass; the append-only session logs must never be routed through one (direct lesson of the 2026-09-26 incident). Their index bytes are already what we want to keep. |
| `i/lf` + `w/crlf` (phantom-prone) | 30 | **Pinned `text eol=lf`** in `.gitattributes` (§4). All 30 verified clean pre-pin; all 30 still clean post-pin. |
| `i/mixed` (mixed EOL **in the index**) | 5 | **Left unpinned, documented** (§3) — pinning cannot make a mixed file consistent; it would only redirect future conversions. |
| `w/mixed` with clean index (2026-09-26 incident signature) | **0** | The repo-wide CRLF repair held; no other file was silently normalized. |
| `i/crlf` + `w/lf` | 0 | — |

## 3. The 5 mixed-in-index files (documented, not pinned)

| File | Lines | Note |
|---|---|---|
| `CLAUDE.md` | 458 | mixed index bytes; active agent-instructions file |
| `DASHBOARD_ARCHITECTURE.md` | 632 | mixed index bytes |
| `REVENUE_GENERATORS/README.md` | 156 | mixed index bytes |
| `_DOCS_ARCHIVE/master_docs/FULL_REPO_AUDIT.md` | 325 | mixed index bytes (archive) |
| `monetize-ai-engine/DOCUMENTATION_AUTOMONETIZE_AI.md` | 100 | mixed index bytes |

These are genuinely mixed **as committed** — an `eol=crlf` pin would silently rewrite
half of each file on the next commit, and no pin can make history consistent. Per the
Golden Rules they stay byte-untouched. **Rule going forward:** any content edit to one
of these files must be logged as a session entry; EOL harmonization, if ever wanted,
is a deliberate, documented conversion — never a side effect.

## 4. The 30 pinned files (`text eol=lf`, exact paths in `.gitattributes`)

`.claude/commands/archon/` ×5 · `.claude/commands/prp-commands/` ×4 ·
`CLAUDE-ARCHON.md` · `CONTRIBUTING.md` · `DEVELOPMENT_ENVIRONMENT_IMPROVEMENT_PLAN.md`
· `DOTDIR_CATALOG_RUN.md` · `PRODUCTION_DEPLOYMENT_CONFIG.md` ·
`PRPs/templates/prp-base.md` · `archon-ui-main/README.md` ·
`archon-ui-main/docs/socket-memoization-patterns.md` · `docs/README.md` ·
`docs/docs/README.md` · `docs/src/pages/markdown-page.md` ·
`original_archon/.github/ISSUE_TEMPLATE/bug_report.md` · `feature_request.md` ·
`original_archon/README.md` · `original_archon/iterations/*/README.md` ×6 ·
`python/src/server/testing/README.md`

**Why they were phantom bombs (the invisible mechanism):** each has LF bytes in the
index but CRLF bytes on disk, yet git reports them clean — because their **cached
index stat exactly matches disk** (e.g. `CONTRIBUTING.md`: cached mtime
`1771318950` = 2026-02-17, size 16317 = live stat). Git's racy-stat optimization
therefore never re-hashes them, so the CRLF state is invisible until anything bumps
the file's mtime — at which point a full-file EOL diff erupts (the exact CHANGELOG-
incident shape, one mtime away). Verified: `git ls-files --debug` (cached stat), forced
`--really-refresh` (still clean = stat-cache path), `git hash-object` ≠ HEAD blob
(CRLF really is on disk).

**Why `eol=lf` fixes it:** the attribute installs a clean filter (CRLF→LF on add) so
the CRLF worktree hashes equal to the LF index — the file stays clean forever, no
worktree byte is touched today, and any future edit commits as LF. Pins are exact
paths only (the file's own header rule: no wildcards).

**Nested attributes interplay:** `original_archon/.gitattributes` sets `text=auto`
on its tree. Attribute resolution is per-attribute last-match: the root `eol=lf`
line applies to all 9 nested paths (they set no `eol` of their own); for
`original_archon/README.md` the deeper `text=auto` overrides the root `text` but
`eol=lf` still controls conversion. Result verified via `git check-attr`:
`text: auto, eol: lf`. The nested file itself was **not modified**.

## 5. Change record

- `.gitattributes`: +44/−0 (14 comment/separator lines + 30 pin lines), byte-pure append,
  file stays LF (+2510 bytes → 3541).
- Backup: `BACKUPS/pre_md_eol_pins_gitattributes_2026-09-29` (1031 bytes,
  md5 `0c4d04c3f4ef28a5f531777f3aed2d95`).
- Tooling: `BACKUPS/append_md_eol_pins_2026-09-29.py` (generates pins from live
  `git ls-files --eol` data — never hand-typed — asserts count, byte-verifies the
  append; first run failed safe on a parse bug **before** any write).
- Post-pin verification: `git status --porcelain` over all 30 paths = clean;
  repo modified-file list unchanged vs pre-audit (no phantoms triggered);
  `CHANGELOG.md`/`TODO_TRACKER.md` remain attribute-free and byte-identical.

## 6. Out of scope (footnotes)

- 21 non-`.md` tracked files are also `i/mixed` (repo-wide count, not audited here).
- Untracked `*.md` files were not audited (no index bytes to protect).
- No content file was modified by this audit; only `.gitattributes` changed.

## 7. Extension — the 21 non-markdown `i/mixed` files (2026-09-29, same session)

The repo-wide `i/mixed` count is 26: the 5 markdown files of §3 plus **21
non-markdown** files (`.py`, `.html`, `.tsx`, `.sql`, `.toml`, `.gitignore`,
`.bat`). Method per file: `git status --porcelain` (clean vs modified) plus
byte comparison `git hash-object <worktree>` vs `git rev-parse HEAD:<path>`.

| Class | Count | Disposition |
|---|---|---|
| **Stable-masked** — clean, worktree bytes **byte-identical to HEAD** | 18 | **Frozen with `-text` pins**: 17 new (+25/−0 in `.gitattributes`) + `START_MONETIZE_AI.bat` already pinned in the 2026-09-24 block. `-text` = byte-freeze: no clean/smudge filter, bytes never converted. These files are honestly-clean committed-mixed files (git status tells the truth); the pin only stops future attribute/renormalization changes from silently re-branching their line endings. |
| **In-flight content edits** — `M`, worktree differs from HEAD | 3 | **Deliberately unpinned, documented.** `CUAI/core/vision_fleet.py` (now uniformly CRLF, 232/0), `monetize-ai-engine/database.py` (161 LF / 1 CRLF), `monetize-ai-engine/server.py` (624 LF / 1 CRLF) — active edits are already *harmonizing* these files toward uniform; a pin would fight the editors. Revisit after their changes land. |

**No phantom-prone file in this class:** unlike §4's 30 markdown files (LF index /
CRLF disk under a matching stat cache), every stable non-md file's worktree equals
its HEAD blob — git status is truthful, nothing is one-resave-from-erupting. The
§4 mechanism (stat-cache masking of a pure-EOL drift) is markdown-specific in this
repo as of today.

**Change record:** `.gitattributes` +25/−0 (8 comment/separator lines + 17 pins,
byte-pure append, LF preserved); backup
`BACKUPS/pre_nonmd_pins_gitattributes_2026-09-29` (3541 bytes, md5
`63daf48c92b8b110453d28ba574c32e8`); generator
`BACKUPS/extend_nonmd_pins_2026-09-29.py`.
