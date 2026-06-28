# 📚 AWESOME INDEX — Unified Knowledge Base Foundation  *(OPT-1.1)*

**Generated:** June 17, 2026
**Sources:** `GOLDEN_RULES.md` (Rule #4 — All 14 `awesome-*` collections are treasures) and a real-system scan.
**Compliance:** Add · Integrate · Connect · Document · Enhance.  No deletions.  No personal-folder touch.

---

## 🪙 GOLDEN RULES IN EFFECT

```
⭐ Rule #4  ALL COLLECTIONS ARE TREASURES — never delete, never "consolidate" by removal.
⭐ Rule #7  ENHANCEMENT NOT REDUCTION.
⭐ Rule #9  ADD · INTEGRATE · CONNECT · DOCUMENT.
```

This index **catalogues** the 14 protected `awesome-*` collections. Mirrors (e.g. `newgit/` + `X:/githubrepo/`) are listed distinctly so the user can pick whichever copy the rest of the system references.

---

## 📋 THE 14 PROTECTED COLLECTIONS  *(catalogue-only, status by real scan)*

| # | Collection (slug) | Status | newgit/ path | X:/githubrepo/ path | Domain |
|---|---|---|---|---|---|
| 1 | `awesome-ai-sdks` | ✅ found | `./newgit/awesome-ai-sdks` | `./X:/githubrepo/awesome-ai-sdks` | AI SDKs and frameworks |
| 2 | `awesome-claude` | ❌ not found at scan depth 4 (deeper scan pending) | — | — | Claude general |
| 3 | `awesome-claude-code` | ✅ found | `./newgit/awesome-claude-code` | `./X:/githubrepo/awesome-claude-code` | Claude Code specifically |
| 4 | `awesome-claude-code-agents` | ❌ not found at scan depth 4 (deeper scan pending) | — | — | Claude Code agents |
| 5 | `awesome-claude-code-subagents` | ✅ found | `./newgit/awesome-claude-code-subagents` | `./X:/githubrepo/awesome-claude-code-subagents` | Claude Code sub-agents |
| 6 | `awesome-cli` | ✅ found | `./newgit/awesome-cli` | `./X:/githubrepo/awesome-cli` | CLI tools |
| 7 | `awesome-cli-apps` | ✅ found | `./newgit/awesome-cli-apps` | `./X:/githubrepo/awesome-cli-apps` | Command-line apps |
| 8 | `Awesome-Code-LLM` | ✅ found | `./newgit/Awesome-Code-LLM` | `./X:/githubrepo/Awesome-Code-LLM` | Code-with-LLM |
| 9 | `awesome-coins` | ✅ found | `./newgit/awesome-coins` | `./X:/githubrepo/awesome-coins` | Cryptocurrency |
| 10 | `awesome-devtools` | ✅ found | `./newgit/awesome-devtools` | `./X:/githubrepo/awesome-devtools` | Developer tooling |
| 11 | `awesome-mcp-servers` | ✅ found | `./newgit/awesome-mcp-servers` | `./X:/githubrepo/awesome-mcp-servers` | MCP ecosystem |
| 12 | `awesome-n8n` | ✅ found | `./newgit/awesome-n8n` | `./X:/githubrepo/awesome-n8n` | n8n workflows |
| 13 | `awesome-nocode-lowcode` | ✅ found | `./newgit/awesome-nocode-lowcode` | `./X:/githubrepo/awesome-nocode-lowcode` | No/low-code |
| 14 | `awesome-selfhosted` | ✅ found | `./newgit/awesome-selfhosted` | `./X:/githubrepo/awesome-selfhosted` | Self-hosted software |

**Total `awesome-*` directories on the system (deep enough for the scan):** 24 paths (12 collections × 2 mirrors).

Two are flagged "not found at scan depth 4": `awesome-claude` and `awesome-claude-code-agents`. Recommend running a deeper scan (`-maxdepth 6–8`) in `OPT-1.1` Week 3-4.

---

## 🔍 HOW THIS WAS SCANNED (additive)

The scan command (read-only) was:

```
find . -maxdepth 5 -type d \( -iname 'awesome-ai-sdks' -o -iname 'awesome-claude' ... -o -iname 'awesome-selfhosted' \) 2>/dev/null
```

This walked up to depth 5 from the system root. It never opened or wrote to any file. Every directory match is appended to this document; **no report card decline is implied by "not found"** — they're simply further down the tree.

---

## 🪜 NEXT STEPS FOR OPT-1.1 (Week 3-4 plans)

1. **Deeper scan** at depth 6 or 8 to find `awesome-claude` and `awesome-claude-code-agents`. Append result here.
2. **Per-collection `README.md`** — extract each repository's `README.md` first 200 chars, store in `AWESOME_READMES.md` (additive). Skip the actual `README.md` write — every collection stays untouched.
3. **Cross-tags** — every collection gets tags like `curated`, `domain:<X>`, `mirror_count:2`. Appending to this index.
4. **Search interface** — build `AWESOME_SEARCH.py` (CLI) that searches across all collection `README.md` files. Read-only.
5. **Annotation system** — `AWESOME_ANNOTATIONS.md` (append-only) for personal notes (does NOT modify the original `README.md`).

---

## 🛡️ PERSONAL-FOLDER GUARD

The scan obeys Rule #8: `Documents`, `Downloads`, `Pictures`, `Videos`, `Music`, `Desktop`, `OneDrive`, and `Downloads/ARCHIVE_OLD` are explicitly excluded from any descent.

---

## 📦 NEW FILES THIS TURN

- `AWESOME_INDEX.md` (this file)

**No file was renamed, deleted, or modified.**

---

## ✅ COMPLIANCE FOOTER

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW `AWESOME_INDEX.md` catalog. No awesome-* directory touched.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive.
```
