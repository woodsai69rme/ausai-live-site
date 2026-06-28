# GOLDEN RULES REFERENCE — Authoritative Source

> **Every decision, every action, every option must obey these rules. If an option contradicts them, drop the option.**

---

## The 7 Golden Rules

### Rule 1: Local-Only Deployment
**You run your own instance.** No cloud-first thinking. No SaaS dependency. Everything works on your machine.

**What this means:**
- Archon runs locally, not on Vercel/Netlify/AWS
- Ollama runs locally, not via OpenAI API
- ComfyUI runs locally, not via cloud GPU
- n8n runs locally, not via n8n cloud
- Supabase can be local (Docker) or cloud — your choice, but you own the data

**What this DOESN'T mean:**
- You can't use OpenRouter for AI routing (that's an API, not deployment)
- You can't use Fiverr/Upwork for sales (that's a marketplace, not deployment)
- You can't use Stripe for payments (that's a payment processor, not deployment)

**Example:**
```
✅ GOOD: "I'll run Ollama locally and use OpenRouter for cloud AI"
❌ BAD: "I'll deploy Archon to Vercel and use OpenAI API directly"
```

---

### Rule 2: No Backwards Compatibility
**Deprecated code is removed immediately — not archived, not parked, deleted.** If something is replaced, the old version is gone.

**What this means:**
- If ComfyUI replaces stable-diffusion-webui → delete stable-diffusion-webui
- If Archon replaces jarvis_orchestrator → delete jarvis_orchestrator
- If a new script replaces an old one → delete the old one
- No "LEGACY" prefixes, no "DEPRECATED" comments, no "v1" folders

**What this DOESN'T mean:**
- You can't keep backups (backups are different from deprecated code)
- You can't version your own work (git history handles that)
- You can't keep reference material (docs are different from code)

**Example:**
```
✅ GOOD: "I fixed the bug in 03_voice_to_n8n.py — the old behavior is gone"
❌ BAD: "I added a new function but kept the old one 'just in case'"
❌ BAD: "I moved the old script to _archive/ in case we need it later"
```

**The archive exception:** You archived 7 orchestrators to `_archive_2026-06-25/`. This was a USER DECISION, not a code decision. The user explicitly chose archive over delete because they wanted reversibility. That's fine — but the DEFAULT is delete.

---

### Rule 3: Detailed Errors Over Graceful Failures
**Surface failures loud so you can fix them fast.** Fail hard on critical issues, log + continue on batch operations.

**When to Fail Fast (Let it Crash!):**
- Service startup failures (missing creds, broken DB)
- Missing configuration (no .env, invalid settings)
- Database connection failures
- Authentication/authorization failures
- Data corruption or validation errors
- Critical dependencies unavailable
- Invalid data that would corrupt state

**When to Complete + Log:**
- Batch processing (crawling, document processing)
- Background tasks (embedding generation, async jobs)
- WebSocket events (don't crash on single event failure)
- Optional features (projects/tasks disabled)
- External API calls (retry with backoff, then fail clear)

**The Critical Nuance: Never Accept Corrupted Data**
```python
# ❌ WRONG — Silent Corruption
try:
    embedding = create_embedding(text)
except Exception as e:
    embedding = [0.0] * 1536  # NEVER — corrupts database
    store_document(doc, embedding)

# ✅ CORRECT — Skip Failed Items
try:
    embedding = create_embedding(text)
    store_document(doc, embedding)  # Only store on success
except Exception as e:
    failed_items.append({'doc': doc, 'error': str(e)})
    logger.error(f"Skipping document {doc.id}: {e}")
    # Continue with next document, don't store anything
```

**Example from this session:**
```
✅ GOOD: 03_voice_to_n8n.py now raises SystemExit(1) on malformed JSON
❌ BAD: 03_voice_to_n8n.py previously returned {} — silently degraded
```

---

### Rule 4: Simplicity & Minimalism
**Make as few changes as possible.** Don't add dashboards, don't perfect landing pages, don't research more tools.

**What this means:**
- Fix the bug with the smallest possible change
- Don't add features nobody asked for
- Don't refactor "while you're in there"
- Don't add a 6th dashboard when 5 exist
- Don't research 12 AI tools when you have 122 dotdirs

**What this DOESN'T mean:**
- You can't add necessary features (the user asked for --dry-run)
- You can't improve error messages (that's detailed errors)
- You can't document things (documentation is minimalism)

**Example:**
```
✅ GOOD: "I added one line to persist morning_briefing.txt"
❌ BAD: "I refactored the entire morning briefing system while fixing the bug"
```

---

### Rule 5: Code Reuse Over Reinvention
**Helper functions, components, classes — always reuse.** Don't reimplement what already exists elsewhere in the codebase.

**What this means:**
- Check if a utility function already exists before writing a new one
- Use existing libraries (httpx, not raw requests)
- Use existing patterns (Pydantic models, not raw dicts)
- Use existing tools (ComfyUI workflows, not custom CUDA kernels)

**Example:**
```
✅ GOOD: "I used the existing speak() function in morning_briefing.py"
❌ BAD: "I wrote a new TTS function because I didn't see the old one"
```

---

### Rule 6: Quality Over Speed
**Fewer, well-informed actions beat many rushed ones.** Take time to understand the problem before solving it.

**What this means:**
- Read the file before editing it
- Understand the bug before fixing it
- Research the market before setting prices
- Test the change before shipping it

**What this DOESN'T mean:**
- You can't move fast when you have context
- You can't iterate quickly on known patterns
- You can't batch similar operations

**Example:**
```
✅ GOOD: "I read the PS1 file, understood the -WhatIf mechanism, then made the fix"
❌ BAD: "I guessed at the fix and hoped it worked"
```

---

### Rule 7: Never Accept Corrupted Data
**Skip failed items entirely. Do not silently fill with placeholders.** Zero-vectors, null foreign keys, and malformed JSON are NEVER acceptable.

**What this means:**
- If embedding generation fails → skip the document, don't store [0.0]*1536
- If JSON parsing fails → raise an error, don't return {}
- If a file is missing → fail loud, don't create a placeholder
- If a database insert fails → log and skip, don't retry forever

**Example:**
```
✅ GOOD: "03_voice_to_n8n.py raises SystemExit(1) on missing config"
❌ BAD: "03_voice_to_n8n.py returned {} on missing config — voice dispatch silently disabled"
```

---

## The 10 Anti-Patterns (Don't Do These)

Anchored to CLAUDE.md + audit findings + the rank-ordering principle "completion > collection."

### 1. Don't Park Overlapping Orchestrators
**Per alpha rule: just delete.**
- ❌ "I'll come back to EmpireOS later"
- ❌ "Let me archive jarvis_orchestrator for now"
- ✅ Delete them. Archon owns the surface.

### 2. Don't Add a Tracking Dashboard
**REVENUE_DASHBOARD.html exists.**
- ❌ "Let me build a new real-time dashboard"
- ❌ "I'll create a React dashboard for revenue tracking"
- ✅ Use the existing one, or update it.

### 3. Don't Bootstrap Another AI Tool
**122 dotdirs and 14 Ollama models already cover it.**
- ❌ "Let me install Cursor too"
- ❌ "I'll add Copilot to my setup"
- ✅ Use what you have. You have enough.

### 4. Don't Accept Contradictory Tasks from Old Docs
**PRODUCTIVITY_AND_REVENUE_OPTIONS.md is the working source.**
- ❌ "The MASTER_EXECUTION_PLAN says to do X"
- ❌ "The ULTIMATE_GUIDE recommends Y"
- ✅ This file is authoritative. Ignore the rest.

### 5. Don't Let Backups Live Inside Active Git
**Backups bloat the index and confuse file watchers.**
- ❌ "I'll keep SYSTEM_BACKUP_2026-03-04 in the repo"
- ❌ "The COMPLETED_PROJECTS folder is fine here"
- ✅ Move backups outside the git tree.

### 6. Don't Store Zero-Vectors on Embedding Failure
**Skip the item. Never corrupt the database.**
- ❌ `embedding = [0.0] * 1536`
- ❌ `embedding = None`
- ✅ Skip the document, log the error, continue.

### 7. Don't Route AI Through Direct Provider Keys
**OpenRouter only.**
- ❌ `OPENAI_API_KEY=sk-...`
- ❌ `ANTHROPIC_API_KEY=sk-ant-...`
- ✅ `OPENROUTER_API_KEY=sk-or-...` — one key, one billing line.

### 8. Don't Start a New Revenue Stream Before #1 Closes
**Completion > collection.**
- ❌ "I'll start a YouTube channel while also doing Fiverr"
- ❌ "Let me add n8n consulting before I land my first audit"
- ✅ Close one paying transaction first. Then expand.

### 9. Don't Perfect a Workflow Before First Paying Client
**Ship at "good enough."**
- ❌ "I need to perfect my ComfyUI workflow before listing on Fiverr"
- ❌ "My audit report template isn't ready yet"
- ✅ Ship now. Iterate after you get paid.

### 10. Don't Archive Deprecated Work
**Remove it. Pages can be re-typed in seconds.**
- ❌ "I'll move this to _archive/ just in case"
- ❌ "Let me keep this in a BACKUP/ folder"
- ✅ Delete it. If you need it again, you'll recreate it in minutes.

---

## The Revenue Rules

### Completion > Collection
Finish one path before starting another. Don't collect 5 revenue streams — master 1.

### First Dollar > Projections
Not projections. Not dashboards. Not valuations. First dollar in bank.

### Penetration → Market → Premium
- Week 1-2: Penetration pricing (low, get reviews)
- Week 3-4: Market rate (match competitors)
- Month 2+: Premium pricing (portfolio justifies it)

### Break-Even Math
- Fixed overhead: $45-85/mo (electricity, Carrd, domain)
- Break-even: ~3 small gigs or 1 audit
- Fiverr fees: 20% of revenue
- Stripe fees: 1.75% + $0.30 per transaction

---

## The Error Handling Decision Tree

```
Is this a critical system (service startup, auth, DB connection)?
  → YES → Fail Fast (crash with clear error)
  → NO ↓

Is this a batch operation (crawling, processing, embedding)?
  → YES → Continue + Log (skip failed items, report at end)
  → NO ↓

Is this an external API call?
  → YES → Retry with backoff (3 attempts), then fail clear
  → NO ↓

Is this a user-facing feature?
  → YES → Fail with user-friendly message
  → NO → Log and continue
```

---

## The Delete/Archive/Condense Decision Tree

```
Is this code that's been replaced by something better?
  → YES → DELETE (Rule 2: no backwards compatibility)
  → NO ↓

Is this code that overlaps with another system?
  → YES → DELETE (Rule 4: simplicity — pick one)
  → NO ↓

Is this code that's unused (no imports, no calls)?
  → YES → DELETE (Rule 4: simplicity — remove dead code)
  → NO ↓

Is this a backup of something that still exists?
  → YES → DELETE (Rule 10: don't archive deprecated work)
  → NO ↓

Is this documentation that's redundant with other docs?
  → YES → CONDENSE (merge into single doc, delete originals)
  → NO ↓

Is this a database that's orphaned (no code references it)?
  → YES → DELETE (Rule 6: quality — clean up mess)
  → NO ↓

Is this a lock/state file from a previous session?
  → YES → DELETE (stale state, not useful)
  → NO ↓

Keep it.
```

---

## The Condense Decision Tree (for Documentation)

```
Are there 2+ docs covering the same topic?
  → YES → CONDENSE into single doc
  → NO ↓

Is this doc longer than 500 lines?
  → YES → CONDENSE (split into focused sub-docs)
  → NO ↓

Does this doc have sections that contradict other docs?
  → YES → CONDENSE (pick one source of truth)
  → NO ↓

Is this doc older than 30 days with no updates?
  → YES → REVIEW (likely stale, condense or delete)
  → NO ↓

Keep it.
```

---

## Quick Reference Card

| Rule | One-Liner | When to Apply |
|---|---|---|
| 1. Local-only | You run your own instance | Architecture decisions |
| 2. No back-compat | Remove immediately | Code changes |
| 3. Detailed errors | Fail loud, fix fast | Error handling |
| 4. Simplicity | Fewer changes, fewer tools | All decisions |
| 5. Code reuse | Don't reinvent | Implementation |
| 6. Quality > speed | Understand before solving | All actions |
| 7. No corrupted data | Skip, don't placeholder | Data operations |

| Anti-Pattern | One-Liner | Fix |
|---|---|---|
| 1. Park orchestrators | "I'll come back" | Delete now |
| 2. Add dashboards | "Let me build a new one" | Use existing |
| 3. Bootstrap tools | "Let me install X" | Use what you have |
| 4. Old docs | "MASTER_PLAN says..." | Use this file |
| 5. Backups in git | "Keep it in the repo" | Move outside |
| 6. Zero-vectors | "[0.0] * 1536" | Skip the item |
| 7. Direct keys | "OPENAI_API_KEY" | OpenRouter only |
| 8. New streams | "Let me start Y" | Close #1 first |
| 9. Perfect workflow | "It's not ready yet" | Ship now |
| 10. Archive work | "Move to _archive/" | Delete it |

---

*Authoritative source. All other docs reference this.*
*Last updated: 2026-06-25*
