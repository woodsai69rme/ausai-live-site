# 🧠 PROJECT_BRAIN_2_0_SYSTEM_INDEX.md

> **Master index for Project Brain 2.0 — the knowledge ingestion and RAG memory system.** Covers 10+ design documents, the `ingest.py` runtime, and multi-phase extension architecture. Strictly additive — chunks, deletion logs, and drift reports are append-only.

**Generated:** 2026-06-28
**Parent systems:** Agent Registry, YouTube Tools, Archon V2

---

## 📁 FILE INVENTORY (10+ files)

### 🔷 Core Runtime

| File | Purpose |
|---|---|
| `PROJECT_BRAIN_2_0/ingest.py` | Idempotent ingestion engine — SHA256 hashing, chunking, RAG pipeline |

### 🔷 Design Documents (in PROJECT_BRAIN_2_0/)

| Document | Purpose |
|---|---|
| `API_DESIGN.md` | REST API specification for brain ingestion endpoints |
| `EMBEDDINGS_DESIGN.md` | Embedding pipeline: Sentence Transformers, ChromaDB integration |
| `HYBRID_SEARCH_DESIGN.md` | Hybrid search: vector + keyword retrieval strategies |
| `DATA_INGESTION_DESIGN.md` | Data ingestion architecture and chunking strategy |
| `PHASE_F_DESIGN.md` | Phase F: Continuous monitoring (`--watch`), drift scanning (`--since`) |
| `PHASE_G_DESIGN.md` | Phase G: Advanced operations and extensions |
| `PHASE_H_DESIGN.md` | Phase H: Production hardening and scale |
| `MULTI_PHASE_OPS.md` | Multi-phase operational procedures |
| `PROJECT_BRAIN_2_0_SPEC.md` | Top-level specification document |

---

## 🏗️ ARCHITECTURE

```
YouTube Transcripts ──┐
Archon Knowledge Base ─┤
Uploaded Documents ────┤
Crawled Websites ──────┤
                        │
                        ▼
              PROJECT_BRAIN_2_0/ingest.py
                        │
                        ├── SHA256 hash → idempotency check
                        ├── Text chunking (sentence boundaries)
                        ├── Embedding generation
                        │
                        ├──► chunks.jsonl (append-only)
                        ├──► DELETED_FILES.jsonl (soft-delete log)
                        ├──► DRIFT_REPORT.md (change tracking)
                        │
                        └──► ChromaDB / Supabase pgvector
                               │
                               ▼
                          RAG Search API
```

---

## 🔧 INGEST.PY CAPABILITIES

| Flag | Purpose |
|---|---|
| `--watch` | Continuous filesystem monitoring |
| `--since <timestamp>` | Drift scanning from timestamp |
| `--purge` | Soft-deletion logging (never hard delete) |
| `--exclude` | Explicit folder exclusions |

### Excluded folders (Rule #8):
Documents, Downloads, Desktop, Pictures, Videos, Music, OneDrive, Downloads\ARCHIVE_OLD

---

## 🔒 SECURITY BOUNDARIES

- **Strictly additive:** `chunks.jsonl`, `DELETED_FILES.jsonl`, `DRIFT_REPORT.md` — never overwritten, only appended
- **Soft-delete only:** `--purge` logs deletions, never removes data
- **Rule #8 fence:** Personal folders explicitly excluded from ingestion
- **Idempotent:** SHA256 hashing prevents duplicate ingestion

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| YouTube Tools | `YOUTUBE_TOOLS_SYSTEM_INDEX.md` |
| Archon V2 | `ARCHON_V2_SYSTEM_INDEX.md` |
| Agent Registry | `AGENT_REGISTRY_SYSTEM_INDEX.md` |
| Workspace Master | `WORKSPACE_INDEX.md` |

---

*Designed under Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite.*
