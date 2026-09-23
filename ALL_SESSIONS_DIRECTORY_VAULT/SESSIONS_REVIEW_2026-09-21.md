# All-Sessions Review — 2026-09-21 (final)

> Scope: full audit of every AI session store on this machine + the unified session index.
> The index was **patched and regenerated during this review**: 1,831 → **1,980 records across 19 tools**.

## 1. What was reviewed
- `MEMORY/agent_session_index/` unified index (all tool stores), `scan_all_sessions.py`,
  vault docs (`ALL_SESSIONS_UNIFIED_DIRECTORY.md`, Antigravity audit), and on-disk session dirs
  for grok-cli, cline, codex, claude-code, qoder, kilo, opencode, antigravity.

## 2. Bugs found & fixed in `scan_all_sessions.py` (this review)
1. **Timestamp normalization bug**: `ts_ms()` used a `1e15` threshold — ms-epochs (~1.78e12) were never
   converted, so kilo/opencode `created`/`updated` were raw ms floats in JSON/MD. Fixed to `1e11`; all
   timestamps now ISO-8601 and the monthly timeline is computable.
2. **opencode `bytes` bug**: every opencode record carried the whole-DB size (19,662,934,016 = the
   18.31 GB `opencode.db`) as its per-session size. Now NULL (per-session size isn't derivable from the DB).
3. **Coverage gaps closed** — new scanners added for:
   - `grok-cli` (~\.grok\sessions): 21 sessions w/ chat_history.jsonl + summary.json
   - `cline` (~\.cline\data\sessions): 102 sessions
   - `codex` (~\.codex\sessions): 5 rollouts
   - `claude-code` (~\.claude\projects): 5 transcripts
   - `qoder` (~\.qoder\logs\sessions): 15 segments

## 3. Final index snapshot (post-fix, 1,980 records)

| Tool | n | Activity span |
|---|---:|---|
| codingsesh | 1,453 | 2026-07-25 .. 2026-08-25 |
| opencode | 144 | 2026-01-21 .. 2026-09-20 |
| antigravity | 108 | 2026-07-17 .. 2026-09-21 |
| cline | 102 | 2026-08-21 .. 2026-09-21 |
| session_archive | 86 | 2026-07-12 .. 2026-09-06 |
| grok-cli | 21 | 2026-07-09 .. 2026-07-17 |
| kilo | 10 | 2026-08-23 .. 2026-09-20 |
| qoder | 15 | 2026-09-20 .. 2026-09-21 |
| claude-code / codex | 5 / 5 | 2026 |
| grok (archives) | 10 | 2026-07-12 .. 2026-07-16 |
| vscode-* / legacy | 17 | 2025-05 .. 2025-08 |

**Monthly activity**: 2026-07 is the all-time peak (1,603 records — the session-archive blitz),
then 2026-08 (129) and 2026-09 (174, month-to-date). Legacy VS Code agents effectively ended Aug 2025.

**Volume**: 12,040 opencode messages + 331 kilo messages indexed; largest single artifacts are three
~835 MB grok transcript dumps in `X:\SESSION_ARCHIVES` (2.5 GB from 3 days in July 2026).

## 4. Remaining issues (advisory)
1. **opencode.db is 18.31 GB** — back it up, archive/prune old sessions, then VACUUM.
2. **Three ~835 MB grok transcripts** (2.5 GB for 3 days) — gzip or split; they'll slow every RAG re-ingest.
3. **Churn pattern**: "reviewing opencode sessions and summaries" ×15, "opencode sessions dashboard
   not visible" ×3 — repeated retry loops; "greeting" ×3 are throwaway sessions.
4. **Vault doc drift**: `ALL_SESSIONS_UNIFIED_DIRECTORY.md` says 84 Antigravity sessions; index has 108.
   Regenerate it from the index.
5. **Path rot: 0** — all 1,980 indexed paths verified live.
6. **NO-timestamp stragglers**: `continue` (3) and `emptyWindowChat` (2) records still lack dates
   (their source JSON has none) — cosmetic only.


