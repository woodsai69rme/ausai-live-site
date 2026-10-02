# .gitignore sweep, round 2 -- 2026-10-01

Companion to `MD_EOL_AUDIT_2026-09-29.md` (the EOL program) and to commit
`8983c0a7b` (round 1: 11 shadowed master/index docs re-admitted via exact-path
negations). Read-only investigation; **zero `.gitignore` edits made this round.**

## Method

1. Enumerated every non-negation wildcard pattern in `.gitignore` (1252 lines)
   that could match authored file types (`.md .py .js .ts .html .json .bat .sh
   .yaml .sql .txt`).
2. For each hit, asked: is the matched file (a) hand-authored source-of-truth,
   or (b) generated / runtime / credential / OS noise that the pattern exists
   to hide?
3. Cross-checked `git check-ignore -v` on every top-level entry to catch rules
   whose only repo-visible victims live at the root.

## Blanket patterns: verdicts

| Pattern | Repo-visible victims | Verdict |
|---|---|---|
| `*_INDEX.md` `*_MASTER.md` `*_SYSTEM_INDEX.md` `ALL_*.md` `*_INVENTORY.md` | only the 2 remaining generated ALL_ files | correct as-is |
| `/X*/` | `X:` (drive mount) | deliberate quarantine; keep |
| `tmp_v*.py` | `tmp_v14_amend_commits.py`, `tmp_v15_amend_commits.py` | one-shot git scripts; correctly ignored |
| `/bin/*.spec` | `bin/run_audit_subprocess.spec` | explicit pattern, single victim; keep |

Round 1 already re-admitted all 11 authored docs the five doc patterns were
hiding; the two `ALL_*.md` files still matched (`ALL_RECREATION_PROMPTS_MASTER_VAULT.md`,
`ALL_SESSIONS_UNIFIED_DIRECTORY.md`) are generated vault/directory dumps and
stay ignored. **No further negations warranted.**

## Annex: the explicit per-file ignore block (lines ~837-952)

Unlike round 1's collateral damage, these ~100 root files are each ignored by
name -- deliberate operator intent, not a blanket-pattern side effect. They
fall into three buckets:

- **Authored docs/scripts (~30)** -- e.g. `AGENCY_MISSION_CONTROL.md`,
  `OUTSTANDING_WORK_PLAN.md`, `SKILLS_MATRIX.md`, `FOOTCLAN_EXECUTOR.py`,
  `orchestrator.py`, `youtube_transcript_harvest.py`. Candidates for a future
  re-admission round IF the operator wants them versioned. Not done unilaterally.
- **Credentials / secrets (must stay ignored)** -- `api_key_vault.json`,
  `vault.key`, `MASTER_CONFIG.env`, `.env*`. Never re-admit; recommend
  `.githooks/golden_rules_guard.sh` gain a block-list check for these paths
  (future hardening).
- **Runtime state / OS noise** -- `*.log`, NTUSER.* registry hives, caches.
  Correctly ignored.

## Conclusion

- Blanket-pattern shadowing: **fully settled** after round 1; this round found
  no new authored victims.
- The per-file block is operator intent; logged here so the distinction is on
  record. If re-admission of the ~30 authored files is ever wanted, it must be
  an explicit, itemized decision -- same discipline as round 1 (exact-path
  negations, `git add -u`, byte-untouched entry).
