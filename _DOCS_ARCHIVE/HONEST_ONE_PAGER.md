# ONE-PAGER — solo AI/automation builder

**For:** freelancer clients, early indie customers, grant funders, partnership outreach.
**Updated:** June 2026.

---

## Who

Solo developer focused on AI tooling, automation, and developer infrastructure. About 12 months of intensive building with local-first tools, free-tier dependencies, and zero contractors. Built Archon V2, Project Brain 2.0, and a 28-piece automation toolkit on disk that other solo builders don't usually have.

---

## What I've shipped (verified)

| Artifact | State | Evidence on disk |
|---|---|---|
| Local AI runtime | Working | 10 Ollama models downloaded (incl. Qwen 2.5 Coder); OpenClaw daemon running; smoke-tested by generating valid Python via local model |
| Archon V2 web UI | Builds + **37/37 tests pass** | React/Vite/TypeScript/Tailwind; ~30,000 LoC; port 3737 |
| Archon MCP server | Working + 5 passing tests | RAG/knowledge-base tools (knowledge, code-examples, sources) port 8051 |
| Project Brain 2.0 ingest pipeline | Working in 6 flag modes | `--watch`, `--since`, `--audit-offset`, `--deleted-out`, `--purge`, `--drift-out`; runs locally |
| 28 first-concrete automation runners | Working | Footclan (3-piece agent team), Voice PA + cross-system bridge, MCP query/host-health pair, federation merger, Backup/Env audit, append-only hygiene checker, revenue ledger |
| Documentation library | In place | 6 master guides; ~100 markdown files; append-only TODO tracker |

---

## Style of work (a buyer-defensible differentiator)

| Pattern | What it means for buyers |
|---|---|
| **Append-only discipline** | Every log writer adds rows, never deletes. Reversible by default. |
| **Refuses private folders** | All runners check against a closed 8-item personal-folder list. Customer data segregation is enforceable. |
| **Dry-run default** | Stateful actions require explicit `--run` opt-in. Safe to wire into staging. |
| **Closed enums** | Status codes are fixed sets, never coerced. Auditable interface contracts. |
| **Read-only on inputs, append-only on outputs** | No script overwrites a source file. Backup-and-rerun is the rollback story. |

These patterns make the work **auditable and reversible** — useful when introducing automation to teams that don't fully trust AI yet.

---

## What I'm currently building (not yet shipped)

- **Footclan Squad** — multi-agent code-review team (design + dispatcher + executor + cross-system bridge): the closest thing in my toolkit to a billable service.
- **Federated MCP** — Phase 1 query audit + Phase 2 chunk-row merger. Reads existing audit logs in real time.
- **Append-only daily hygiene checker** — 12 audit logs checked daily for size drift and timestamp regression.

---

## What is NOT in this portfolio (and why this is honest)

| Not yet | What this means |
|---|---|
| Paying customers | I haven't yet sold a service; I'm looking to. |
| A deployed SaaS with subscribers | Not at that stage. |
| A validated crypto-trading strategy | I have monitors and dashboards, not a tested strategy. |

This isn't a sales pitch about to fudge the gaps. The gaps are real.

---

## Pricing (if interested)

| Engagement | Price (AUD) | What you get |
|---|---|---|
| Audit-trail setup (one repo) | $300 | One Footclan dispatcher + executor + PROVENANCE.log; 30 PRs/month |
| Local-AI integration | $800 | OpenClaw + Ollama + custom skill bundle; tested for one workflow |
| Code-review pilot | $2,000 | 100 PRs/month across 3 repos; one monthly call |

First 3 engagements: 50% off. After that: full price.

---

## What I'm looking for (next 30 days)

1. **A first paid engagement** — code-review automation, audit-trail setup, or local-AI integration for one small team.
2. **Feedback** on offer-shaping before I commit to packaging as a full SaaS.
3. **One early-design partner** for a 30-day pilot at the discounted pilot rate.

---

## Contact

Reply to this conversation; we can iterate the offer together before money changes hands.

---

*This document intentionally drops the "500-700+ hours" and "$35-65K AUD" figures from earlier reports. They were upper-bound ceilings, not earned value. This card only describes what is verifiable on disk.*
