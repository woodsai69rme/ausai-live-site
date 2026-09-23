# MEMORY — AI Session Archives (2026)

Index of every recoverable AI coding-chat session on this machine, plus a full
export of the 10 native Kilo sessions.

## Quick links

| Artifact | Location | Size | Notes |
|----------|----------|------|-------|
| Unified index (JSON) | `MEMORY\agent_session_index\unified_ai_sessions_index.json` | ~960 KB | 1987 records, 18 tools |
| Unified index (Markdown) | `MEMORY\agent_session_index\unified_ai_sessions_index.md` | ~360 KB | human-readable report |
| Per-tool JSON splits | `MEMORY\agent_session_index\unified_<tool>.json` | — | e.g. kilo, opencode, antigravity |
| Kilo full export (JSON) | `MEMORY\kilo_sessions\kilo_sessions_full.json` | ~8.0 MB | all messages, parts, todos, metadata |
| Kilo consolidated index | `MEMORY\kilo_sessions\KILO_SESSIONS_INDEX.md` | 7.8 KB | table of 10 sessions |
| Kilo per-session | `MEMORY\kilo_sessions\ses_<id>__<title>\` | — | session.json + session.md each |

## Tools discovered

| Tool | Sessions found | Storage |
|------|----------------|---------|
| kilo (desktop) | 10 | `.local/share/kilo/kilo.db` SQLite + `session_diff/` |
| opencode | 145 | `.local/share/opencode/opencode.db` SQLite (~18 GB) |
| antigravity | 108 | `.gemini/antigravity/brain/{uuid}/` jsonl transcripts |
| cline | 102 | `.cline/data/sessions/` |
| codex | 5 | `~/.codex/sessions/` |
| claude-code | 5 | `~/.claude/projects/` + conversations |
| qoder | 30 | qoder sessions |
| grok-cli | 21 | grok transcripts |
| grok | 10 | `grok_transcript_*.jsonl` in SESSION_ARCHIVES |
| codingsesh | 1453 | `X:\codingsesh/session_*.{txt,md,html,json}` |
| session_archive | 87 | `X:\SESSION_ARCHIVES/SESSION_*_{DOCUMENTATION,FULL HISTORY}.md` |
| vscode-claude-dev | 6 | VS Code globalStorage tasks (Cline) |
| vscode-kilocode | 6 | VS Code globalStorage tasks (Kilo Code) |
| vscode-debug-cline | 1 | VS Code globalStorage tasks (Debug Cline) |
| continue | 3 | `.continue/sessions/*.json` |
| cursor | 1 | `.cursor/ai-tracking/ai-code-tracking.db` |
| emptyWindowChat | 2 | VS Code `emptyWindowChatSessions/` |
| cherrystudio | 1 | app data dir |
| lmstudio | 1 | LM Studio app data |

## Regenerate

```
python MEMORY\agent_session_index\scan_all_sessions.py   # rebuild unified index
python MEMORY\agent_session_index\verify.py               # quick integrity check
```

The Kilo export script lives at the kilo_sessions export step (reads
`.local/share/kilo/kilo.db` -> MEMORY\kilo_sessions).
