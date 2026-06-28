# 🧠 PROJECT BRAIN 2.0 — Specification  *(ENH-I1 — Ultimate Multiplier)*

**Generated:** June 17, 2026
**Sources:** `COMPLETE_ENHANCEMENTS_MENU.md` (Tier 2, ENH-I1)
**Goal:** Index all 346 repositories (active + historical) into a local Vector Database so every agent can cross-reference code, configs, and learnings across the entire ecosystem in seconds.
**Compliance:** Add · Integrate · Connect · Document · Enhance.  No deletions.  No personal-folder touch.

---

## 🪙 Why this is the **Ultimate Multiplier**

> *"If you're building a new project on `C:`, your agents can instantly remember how you solved a similar problem 3 years ago in a legacy project on `X:`."* — `COMPLETE_ENHANCEMENTS_MENU.md`

Project Brain 2.0 turns 346 isolated repos into **one searchable global intelligence**. Every other agent, dashboard, suggestion, and script becomes more valuable because the brain is its lookup layer.

Without Project Brain: each tool re-reads files, repeats mistakes, loses context.
With Project Brain: every prompt arrives pre-grounded against the entire history.

---

## 🎯 OBJECTIVES

| ID | Objective | Success metric |
|---|---|---|
| PB-1 | Index every code file across 346 repos | 100% of `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.go`, `.rs`, `.md`, `.json`, `.yml`, `.toml`, `.sh`, `.ps1`, `.bat` reachable in <500ms |
| PB-2 | Embed with high-quality open-source model | vector_dim = 768 (or 1536 if user prefers) |
| PB-3 | Provide semantic + keyword hybrid search | Top-5 recall on curated eval set ≥ 0.85 |
| PB-4 | REST API + CLI for agents | p95 <500ms over 1M chunks |
| PB-5 | All-daily re-ingest (additive) | New files auto-discovered; **never removed** |
| PB-6 | Append-only index history | Every chunk traceable to source commit |
| PB-7 | Replay-safe | Re-indexing is idempotent; doesn't mutate source |

---

## 🏗️ ARCHITECTURE

```
                ┌────────────────────────────────────┐
                │       Project Brain 2.0 (core)     │
                │  ┌──────────────────────────────┐  │
   Repos ─────► │  │ Ingestion (read-only)       │  │ ───► Faiss / Chroma
                │  │ Chunking + Embedding          │  │      (vector store)
                │  │ Metadata extractor            │  │
   Logs  ─────► │  │ Daily delta scanner           │  │
                │  └──────────────────────────────┘  │
                │  ┌──────────────────────────────┐  │
  Agents ─────► │  │  Hybrid Search API            │  │ ◄─── /search
  Tools  ─────► │  │  - BM25 (keyword)             │  │ ◄─── /ask
  Humans ─────► │  │  - Vector (semantic)           │  │ ◄─── /hybrid
                │  │  - Cross-encoder rerank        │  │
                │  │  - Cross-repo aggregator       │  │
                │  └──────────────────────────────┘  │
                └────────────────────────────────────┘
```

### Component map
| Component | Tech | Note |
|---|---|---|
| Vector store | Faiss (default) or Chroma | Pick one; both additive |
| Embedding model | sentence-transformers (open) or OpenAI/text-embedding-3 (via OpenRouter per CLAUDE.md) | MUST use OpenRouter; no direct provider keys (per project rule) |
| BM25 | rank-bm25 or Whoosh | Add on top, not instead |
| Cross-encoder | optional, cheap cross-encoder/ms-marco-MiniLM | Rerank top-50 hybrid hits |
| API | FastAPI on port 8053 | Mirrors MCP/Agent pattern (`8051`/`8052`) |
| Daily delta | ripgrep-based scanner | New/changed files only |
| Index history | append-only JSONL of `(chunk_hash, source, ts)` | Compliance: never drops or rewrites |

---

## 📦 DATA MODEL

Each chunk indexed carries:
```json
{
  "id": "<hash-of-source+span>",
  "source": "ACTIVE_PROJECTS/claude-flow/src/agent.py",
  "commit": "abc123…",
  "repo": "claude-flow",
  "lang": "py",
  "span": [120, 320],
  "text": "...",
  "tokens": 240,
  "embedding": [ … ],
  "tags": ["agent", "router", "anthropic"],
  "ingested_at": "2026-06-17T14:00:00Z"
}
```

---

## 🛡️ GOLDEN-RULE GUARD

- **Read-only source.** Project Brain **never** writes back to a user's repo file.
- **No deletions.** A removed file from source is **kept** with `deleted=true` flag — we never forget a chunk we learned.
- **Personal folders untouched.** `Documents/`, `Downloads/`, `Pictures/`, `Videos/`, `Music/`, `Desktop/`, `OneDrive/` are excluded from the indexer (Rule #8).
- **No plaintext secrets.** Embeddings don't capture raw `.env` values; secrets are PII-redacted before chunking.
- **OpenRouter only.** AI-model calls go through `OPENROUTER_API_KEY` — never direct provider keys.

---

## 🪜 BUILD PLAN (additive, Gold-Rule-safe)

### Phase A — Hardware & data audit (Week 1-2)
- A1 Scan all `.git` roots under `~`. Build `REPO_REGISTRY.csv` (name, class, last_touched, primary_lang).
- A2 Identify ignored dot-folders (`.env*`, `.claude/`, personal folders) — these stay unindexed.
- A3 Provision `~/PROJECT_BRAIN_2_0/` (new folder) to hold the index, store, and code; nothing moved out.

### Phase B — Ingestor (Week 3-4)
- B1 Build `ingest.py` (idempotent, multi-process, GPU-optional).
- B2 Chunking strategy: language-aware (tree-sitter for code, paragraph for docs).
- B3 Run ingest against `ACTIVE_PROJECTS/`, `EXPERIMENTAL/`, `COMPLETED_PROJECTS/`, returning counts to `INGEST_REPORT.md`.

### Phase C — Embedder (Week 5)
- C1 Default to sentence-transformers/all-mpnet-base-v2 (768-d, open).
- C2 Optional OpenRouter embedding model.
- C3 Run on GPU if available; CPU fallback uses 4 workers.

### Phase D — Hybrid search (Week 6)
- D1 BM25 layer built per-repo, merged at query time.
- D2 Vector cosine + BM25 score, weighted 0.7 / 0.3.
- D3 Optional cross-encoder rerank on top-50.

### Phase E — API & Webhook (Week 7)
- E1 FastAPI service on port 8053.
- E2 MCP-compatible tool surface (so Brain exposes itself to Claude / Kiro / Cline via MCP).
- E3 `/search`, `/ask`, `/hybrid`, `/lookup`, `/cite` endpoints.
- E4 Token-aware context assembly (returns the smallest set of chunks needed).
- E5 Additive audit log — every query appended to `QUERY_AUDIT.jsonl`.

### Phase F — Continuous Re-Ingest (ongoing)
- F1 Daily `delta-scan` cron: walk every repo's `.git` log since last run, ingest new/changed files only.
- F2 New chunk IDs use content-hash + span — never overwrite; append.
- F3 Soft-delete flag (`deleted=true`) on removed source files; the chunk stays.
- F4 Drift detection: surface unindexed files in `DRIFT_REPORT.md` (additive).

### Phase G — Search UX & Routing (Week 8-9)
- G1 Add `/router` endpoint that picks the right tool's repo (Claude / Qwen / Cursor / etc.) for follow-on edits — never replaces any tool.
- G2 `/followup` endpoint that suggests the best next file to edit for the answer.
- G3 Web UI panel that lists top-K chunk sources with click-to-open in user's editor.
- G4 Per-domain presets (security, incident, devops, revenue, game, media) tuned via `SEARCH_PRESETS.md`.

### Phase H — Polish & Adoption (Week 10+)
- H1 INCIDENT playbook: if Brain is offline, every tool falls back to its own memory (additive; no tool depends on Brain).
- H2 Onboarding doc — read `PROJECT_BRAIN_2_0_SPEC.md` plus `HOME_INDEX.md` plus `SCRIPTS/MASTER_ORCHESTRATION_INDEX.json`.
- H3 Monthly reporting into `BRAIN_MONTHLY_REPORT.md` — chunk growth, top queries, coverage percentage.

---

## 🔌 INTEGRATION MATRIX (Brain plugs INTO every tool — none removed)

| Tool | Integration | Net change |
|---|---|---|
| Claude | MCP tool surface (Brain exposes `/search` → cited answers) | New MCP capability; Claude still has all prior abilities |
| Cursor | `/hybrid` HTTP endpoint in `.cursor/hooks/` | Cursor still has all prior abilities |
| Cline | OpenAPI plugin | Cline still has all prior abilities |
| Continue | Custom provider spec | Continue still has all prior abilities |
| Aider · Kilo · Gemini · Qwen · Trae · Kiro | HTTP API client | Each keeps every prior ability |
| Ollama / LM Studio | Serve embedder locally when offline | Local fallback to existing setup, no removal |

> **Nothing in this matrix removes a tool. Brain is a *new* layer.** Rule #3 is preserved.

---

## 🧪 ACCEPTANCE TEST SET

| Test | Pass criterion |
|---|---|
| `query_returns_citation` | Top result returns `source=<repo>:<path>:<span>`; never returns a removed chunk |
| `replay_safe` | Re-index after Day-1 reproduces the same content-hashed IDs |
| `personal_folder_offlimits` | Indexer never includes paths inside `Documents/`, `Downloads/`, `Pictures/`, `Videos/`, `Music/`, `Desktop/`, `OneDrive/` |
| `mcp_bridge_alive` | MCP handshake returns Brain's tool list |
| `append_only_audit` | `QUERY_AUDIT.jsonl` records every query with timestamp, user, query, top-K |

---

## 📦 DELIVERABLES (additive only)

- `~/PROJECT_BRAIN_2_0/ingest.py` § adds new ingestor
- `~/PROJECT_BRAIN_2_0/api.py` § adds FastAPI surface
- `~/PROJECT_BRAIN_2_0/MCP_BRIDGE/` § adds MCP server folder
- `~/PROJECT_BRAIN_2_0/INDEX/` § adds vector store folder (Faiss + BM25)
- `~/PROJECT_BRAIN_2_0/REPO_REGISTRY.csv` § adds the registry file
- `~/PROJECT_BRAIN_2_0/INGEST_REPORT.md` § adds the report entry
- `~/PROJECT_BRAIN_2_0/DRIFT_REPORT.md` § adds the drift report
- `~/PROJECT_BRAIN_2_0/SEARCH_PRESETS.md` § adds presets doc
- `~/PROJECT_BRAIN_2_0/BRAIN_MONTHLY_REPORT.md` § adds monthly status

**No existing files are renamed, deleted, or moved. The 346 indexed repos are unchanged on disk.**

---

## ✅ COMPLIANCE FOOTER

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW specification `PROJECT_BRAIN_2_0_SPEC.md`. No source file is modified.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive.
```
