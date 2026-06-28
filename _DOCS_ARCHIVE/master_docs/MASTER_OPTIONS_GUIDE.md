# MASTER OPTIONS GUIDE — 2026-06-25

> **Every option available, with detailed explanations, step-by-step instructions, and Golden Rule compliance.**

---

## How to Use This Guide

1. **Read GOLDEN_RULES_REFERENCE.md first** — every option must obey the 7 rules
2. **Pick your path** based on your priority (revenue, cleanup, automation, strategic)
3. **Follow the step-by-step instructions** for each option
4. **Verify the result** before moving to the next option

---

## CATEGORY A: DELETE Operations

> **Golden Rule 2: No backwards compatibility. Deprecated code is removed immediately.**

### A1. Delete 5 Dead Repos from C:\Users\karma

**Why:** These repos overlap with Archon or are unused. They add noise to `git status` and confuse file watchers.

**What gets deleted:**

| Repo | Reason | Size | Risk |
|---|---|---|---|
| `agent-zero` | Superseded by jarvis (which is also superseded) | ~50 MB | None — no unique code |
| `aigf` | Unused, no activity | ~10 MB | None — empty |
| `tadpole-studio` | Third-party, zero activity | ~20 MB | None — not yours |
| `ai-music-video-studio` | Duplicates ComfyUI music_video_studio.py | ~30 MB | Low — unique scripts should be merged first |
| `ACTIVE_PROJECTS` | 21,566 dirty files, bloated | ~500 MB | Medium — check for unique work first |

**Step-by-step:**
```bash
# 1. Check for unique work in ai-music-video-studio
ls ai-music-video-studio/
# If any unique scripts exist, copy them to ComfyUI/tools/ first

# 2. Check ACTIVE_PROJECTS for unique work
find ACTIVE_PROJECTS -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20
# If unique code exists, copy to a safe location first

# 3. Delete each repo
cd C:/Users/karma
rm -rf agent-zero
rm -rf aigf
rm -rf tadpole-studio
rm -rf ai-music-video-studio
rm -rf ACTIVE_PROJECTS

# 4. Verify
git status --porcelain | wc -l
# Should show fewer untracked files
```

**Golden Rule compliance:**
- Rule 2 (No back-compat): ✅ Removing replaced/unused code
- Rule 4 (Simplicity): ✅ Reduces clutter
- Rule 6 (Quality): ✅ Cleans up mess

**Reversibility:** None — this is permanent. Use `git stash` first if unsure.

---

### A2. Delete 39 Orphan SQLite Databases from X:\GITHUBREPO

**Why:** These databases are from previous AI agent sessions. No code references them. They waste disk space and create confusion.

**What gets deleted:**

| Database | Source Session | Size | Reference Count |
|---|---|---|---|
| agent_registry.db | Unknown | ~10 MB | 0 |
| ai_collaboration_platform.db | Unknown | ~5 MB | 0 |
| ai_ecosystem_memory.db | Unknown | ~20 MB | 0 |
| ai_hub.db | Unknown | ~15 MB | 0 |
| apex_enterprise.db | Unknown | ~8 MB | 0 |
| audit_agent_registry.db | Unknown | ~5 MB | 0 |
| conversations.db | Unknown | ~50 MB | 0 |
| crypto_analysis.db | Unknown | ~10 MB | 0 |
| crypto_test_results.db | Unknown | ~5 MB | 0 |
| deep_security_audit.db | Unknown | ~8 MB | 0 |
| documentation_generation.db | Unknown | ~3 MB | 0 |
| enterprise_hub.db | Unknown | ~10 MB | 0 |
| enterprise_revenue.db | Unknown | ~8 MB | 0 |
| enhanced_security_monitoring.db | Unknown | ~5 MB | 0 |
| github_repo_manager.db | Unknown | ~15 MB | 0 |
| hackrf_platform.db | Unknown | ~10 MB | 0 |
| hackrf_ultimate_complete.db | Unknown | ~20 MB | 0 |
| hackrf_ultimate_sessions.db | Unknown | ~8 MB | 0 |
| integration_coordination.db | Unknown | ~5 MB | 0 |
| integration_system.db | Unknown | ~10 MB | 0 |
| market_domination_analytics.db | Unknown | ~8 MB | 0 |
| marketplace.db | Unknown | ~5 MB | 0 |
| master_audit.db | Unknown | ~15 MB | 0 |
| models.db | Unknown | ~10 MB | 0 |
| monitoring_data.db | Unknown | ~8 MB | 0 |
| openrouter.db | Unknown | ~20 MB | 0 |
| openrouter_analysis.db | Unknown | ~10 MB | 0 |
| openrouter_revenue.db | Unknown | ~8 MB | 0 |
| performance_optimization.db | Unknown | ~5 MB | 0 |
| project_management.db | Unknown | ~10 MB | 0 |
| quality_assurance.db | Unknown | ~5 MB | 0 |
| research_data.db | Unknown | ~8 MB | 0 |
| revenue_customers.db | Unknown | ~5 MB | 0 |
| revenue_marketplace.db | Unknown | ~5 MB | 0 |
| security_analysis.db | Unknown | ~10 MB | 0 |
| security_platform.db | Unknown | ~8 MB | 0 |
| search_index.db | Unknown | ~5 MB | 0 |
| ultimate_crypto_platform.db | Unknown | ~15 MB | 0 |
| ultimate_revenue_system.db | Unknown | ~10 MB | 0 |
| unified_crypto_platform.db | Unknown | ~8 MB | 0 |

**Step-by-step:**
```bash
# 1. Verify no code references these databases
cd X:/GITHUBREPO
grep -r "agent_registry.db" --include="*.py" --include="*.js" --include="*.ts" | head -5
# Should return nothing

# 2. Delete all orphan databases
find . -maxdepth 1 -name "*.db" -delete
find . -maxdepth 1 -name "*.db-journal" -delete
find . -maxdepth 1 -name "*.db-shm" -delete
find . -maxdepth 1 -name "*.db-wal" -delete

# 3. Verify
find . -maxdepth 1 -name "*.db" | wc -l
# Should return 0
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Removes dead data
- Rule 6 (Quality): ✅ Cleans up orphaned files

**Reversibility:** None — databases are deleted permanently. Back up first if unsure.

---

### A3. Delete 8 Stale Lock/State Files from X:\GITHUBREPO

**Why:** These files are from previous AI agent sessions. They're stale, misleading, and serve no purpose.

**What gets deleted:**

| File | Source | Risk |
|---|---|---|
| `CLAUDE_ACCESS_PERMANENTLY_BLOCKED.lock` | Unknown session | None |
| `CLAUDE_EMERGENCY_ACTIVE.txt` | Unknown session | None |
| `CLAUDE_PROTECTION_ACTIVE.lock` | Unknown session | None |
| `COST_PROTECTION_ACTIVE.lock` | Unknown session | None |
| `EMERGENCY_BACKUP/` | Unknown session | Low — verify contents first |
| `EMERGENCY_PROTECTION_MAXIMUM.lock` | Unknown session | None |
| `EMERGENCY_RESPONSE_ACTIVATED.txt` | Unknown session | None |
| `OPENROUTER_ONLY_MODE.lock` | Unknown session | None |

**Step-by-step:**
```bash
# 1. Check EMERGENCY_BACKUP/ contents
ls X:/GITHUBREPO/EMERGENCY_BACKUP/
# If it contains unique data, copy elsewhere first

# 2. Delete lock files
cd X:/GITHUBREPO
rm -f CLAUDE_ACCESS_PERMANENTLY_BLOCKED.lock
rm -f CLAUDE_EMERGENCY_ACTIVE.txt
rm -f CLAUDE_PROTECTION_ACTIVE.lock
rm -f COST_PROTECTION_ACTIVE.lock
rm -f EMERGENCY_PROTECTION_MAXIMUM.lock
rm -f EMERGENCY_RESPONSE_ACTIVATED.txt
rm -f OPENROUTER_ONLY_MODE.lock

# 3. Delete EMERGENCY_BACKUP if empty or stale
rm -rf EMERGENCY_BACKUP/

# 4. Verify
ls *.lock *.txt 2>/dev/null | grep -i "emergency\|protection\|blocked"
# Should return nothing
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Removes stale state
- Rule 6 (Quality): ✅ Cleans up confusion

---

### A4. Delete 4 Redundant OpenRouter Backups from X:\GITHUBREPO

**Why:** All 4 backups were created within 3 minutes of each other on Aug 11, 2025. They're duplicates.

**What gets deleted:**

| Directory | Timestamp | Size |
|---|---|---|
| `OPENROUTER_COMPLETE_BACKUP_20250811_170045/` | Aug 11 17:00 | ~50 MB |
| `OPENROUTER_COMPLETE_BACKUP_20250811_170207/` | Aug 11 17:02 | ~50 MB |
| `OPENROUTER_COMPLETE_BACKUP_20250811_170242/` | Aug 11 17:02 | ~50 MB |
| `OPENROUTER_COMPLETE_BACKUP_20250811_170310/` | Aug 11 17:03 | ~50 MB |

**Step-by-step:**
```bash
# 1. Keep the latest backup (170310), delete the rest
cd X:/GITHUBREPO
rm -rf OPENROUTER_COMPLETE_BACKUP_20250811_170045/
rm -rf OPENROUTER_COMPLETE_BACKUP_20250811_170207/
rm -rf OPENROUTER_COMPLETE_BACKUP_20250811_170242/

# 2. Verify only one remains
ls -d OPENROUTER_COMPLETE_BACKUP_*/
# Should show only OPENROUTER_COMPLETE_BACKUP_20250811_170310/
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Removes redundancy
- Rule 6 (Quality): ✅ Cleans up duplicates

---

### A5. Delete 200+ Dead Directories from X:\GITHUBREPO

**Why:** ~90% of X:\GITHUBREPO is dead weight — duplicate projects, abandoned experiments, and stale code.

**What gets deleted (categories):**

| Category | Count | Reason |
|---|---|---|
| Crypto/Trading projects | 30+ | Unused, duplicated |
| Dashboard variants | 15+ | Duplication |
| Claude clone army | 15+ | Duplication |
| Web app clones | 20+ | Mostly unused |
| AI agent systems | 10+ | Superseded |
| Backup directories | 5+ | Redundant |

**Step-by-step:**
```bash
# 1. Create a safe deletion list
cd X:/GITHUBREPO
cat > DELETE_LIST.txt << 'EOF'
crypto-ai-hivemind/
crypto-ai-nexus-dashboard/
crypto-automa-pilot/
crypto-beacon-fusion-hub/
crypto-beacon-trader-hub/
crypto-dream-trade-sim/
crypto-forge-master/
crypto-fusion-nexus-flow/
crypto-lovable-trader/
crypto-nexus-automator/
crypto-nexus-compass/
crypto-nexus-fusion/
crypto-vision-suite/
crypto-woods-alpha/
crypto-woods-ulitmate-26/
cryptoai-trade-commander/
cryptoai-trade-forge/
cryptoai-tradeflow-nexus/
cryptonaut-ai-terminal/
solana-trading-bot-v2/
freecrypto/
coin-alchemy-ai/
awesome-coins/
fusion-trading-vision/
trading-insight-sphere/
trading-strategy-nexus/
trading_platform/
ultimate-trading-platform/
bot-bloom-capital/
phantom-profit-platform/
spare-change-futures/
quant-alpha-nexus/
marvel-ai-trading-hub/
digital-trading-flow/
crypto-dream-voyage-sim/
GEMDASH/
GEMDASH2/
SOLODASH/
SOLOQA/
SOLOQA2/
TMPDASH/
DASHBOARDS_COMPLETE/
ALL_DASHBOARDS_COMPLETE/
AI-Dashboard-Suite/
DEV-DASHBOARD/
dashboard-deploy/
dashboard_deployment/
dashboards_and_links/
favorite-flow-dashboard/
project-heartbeat-dashboard/
project-pal-dashboard-hub/
CLAUCODER/
CLAUDASH/
CLAUDEOPEN/
SuperClaude/
claude-code-complete-backup/
claude-code-otel/
claude-code-router/
claude-code-subagents/
claude-conductor/
claude-ecosystem/
claude-flow*/
claude-task-master/
claudia/
awesome-claude-agents/
awesome-claude-code/
awesome-claude-code-agents/
bolt.diy/
bolt2/
boltcrypto/
boltnew/
perplexity-clone/
lovable-custom-gpt/
lovable-evolved-fusion-core/
lovable-idea-nexus/
love-bolt-clone-magic/
lovely-web-clone/
loving-bolt-vortex-clone/
mimic-youware-clone/
open-lovable/
open-webui/
remote-desktop-webui/
rest-express-replit/
pancake-frontend/
tell-me-that-clone/
ui-source-gatherer/
web-analyst-mirror/
web-quadrant-viewer/
enhanced_file_sharing_app/
file_sharing_app/
v0-untitled-project/
foot_clan/
footclan-ultimate-os/
FOOTCLAN_OS/
aiarmy/
aiarmy_backup_20260217/
aether-flow-orchestrator/
multi_agent_core/
modular_agents/
openrouter_multi_agent/
cybersecurity-platform/
ethical-pentesting-platform/
security-forensics-toolkit/
bug-bounty-toolkit/
hackrf-ultimate-platform/
hackrfv0/
musicmanager/
artspark-gallery-verse/
artspark-nft-haven/
comment-roulette-youtube/
youtube-intelligence-suite/
youtube_intelligence/
Youtube-playlist-to-formatted-text/
creativeforge-nexus-studio/
ENTERPRISE_SALES/
REVENUE_ACTIVATION/
revenue_systems/
saas_launch/
MARKETING_LAUNCH/
marketing/
consulting_services/
business_sale/
GUMROAD_PRODUCTS/
creator_brand/
InstantCoder/
TaskFlow_AI_Manager/
ai_portal/
ai-workspace-open-source/
ai/
ai_assistants/
ai_hub_env/
aiworkspace/
aigenius-toolkit/
aiittoolsbolt/
aiusemaxbolt/
local-ai-alchemy-lab/
smart-ai-buddy/
unified-ai-ecosystem/
zeroone-autonomy-forge/
zeroone-private-nexus/
zeroone-toolkit/
zeroonebolt/
extreme_ai/
UltimateAndroidToolkit_Portable/
UltimateAndroidToolkit_v3.0_Professional/
woods-android-recovery-kit/
woodsandroidv2/
EOF

# 2. Dry-run first
while read dir; do
  if [ -d "$dir" ]; then
    echo "WOULD DELETE: $dir ($(du -sh "$dir" 2>/dev/null | cut -f1))"
  fi
done < DELETE_LIST.txt

# 3. Execute (after verifying dry-run)
while read dir; do
  if [ -d "$dir" ]; then
    rm -rf "$dir"
    echo "DELETED: $dir"
  fi
done < DELETE_LIST.txt

# 4. Verify
ls -d */ | wc -l
# Should be significantly fewer
```

**Golden Rule compliance:**
- Rule 2 (No back-compat): ✅ Removing replaced/unused code
- Rule 4 (Simplicity): ✅ Massive clutter reduction
- Rule 6 (Quality): ✅ Cleans up 90% of dead weight

**Reversibility:** None — permanent deletion. Back up first if unsure.

---

## CATEGORY B: ARCHIVE Operations

> **Golden Rule 10: Don't archive deprecated work. Remove it. But the user explicitly chose archive for the 7 orchestrators — that's a user decision, not a code decision.**

### B1. Archive Status: 7 Orchestrators Already Archived

**Status:** ✅ COMPLETE — all 7 directories moved to `_archive_2026-06-25/`

**Archived directories:**
1. EmpireOS
2. SYSTEM_CORE
3. jarvis_orchestrator
4. REVENUE_GENERATORS
5. hermes-agent
6. pipedream
7. stable-diffusion-webui

**Reversibility:** Available via `07_archive_overlapping_orchestrators.bat /UNDO`

**Note:** Per Golden Rule 10, the default should have been DELETE. The user chose ARCHIVE because they wanted reversibility. That's acceptable — but the DEFAULT for future decisions is DELETE.

---

### B2. Future Archive Decision Framework

**When to ARCHIVE (rare):**
- User explicitly requests reversibility
- The work might be needed for reference (not code, but design docs)
- The work is large and deletion would be destructive

**When to DELETE (default):**
- Code is replaced by something better
- Code overlaps with another system
- Code is unused (no imports, no calls)
- Code is from a previous session and stale

**When to CONDENSE:**
- Multiple docs cover the same topic
- A doc is longer than 500 lines
- A doc has sections that contradict other docs

---

## CATEGORY C: CONDENSE Operations

> **Golden Rule 4: Simplicity & Minimalism. Merge redundant docs into single sources of truth.**

### C1. Condense 239 Orphan .md Files at C:\Users\karma Root

**Why:** 239 markdown files at the root represent a "planning graveyard." Most are redundant, stale, or contradictory.

**Step-by-step:**
```bash
# 1. Categorize all .md files
cd C:/Users/karma
ls *.md | while read f; do
  echo "$(head -1 "$f" 2>/dev/null) | $f"
done > md_inventory.txt

# 2. Identify duplicates (similar first lines)
sort md_inventory.txt | uniq -d -w 50

# 3. Identify stale files (older than 30 days)
find . -maxdepth 1 -name "*.md" -mtime +30 | head -50

# 4. Create consolidation plan
# Group by topic:
# - Revenue docs → keep REAL_MONEY_PLAN_2026-06-25.md, delete others
# - Architecture docs → keep CLAUDE.md, delete others
# - Audit docs → keep SESSION_DOCUMENTATION_2026-06-25.md, delete others
# - Planning docs → keep PRODUCTIVITY_AND_REVENUE_OPTIONS.md, delete others

# 5. Move survivors to docs/
mkdir -p docs/
mv REAL_MONEY_PLAN_2026-06-25.md docs/
mv COMPLETE_SYSTEM_INVENTORY_2026-06-25.md docs/
mv SESSION_FULL_HISTORY_2026-06-25.md docs/
mv SESSION_DOCUMENTATION_2026-06-25.md docs/
mv GOLDEN_RULES_REFERENCE.md docs/
mv MASTER_OPTIONS_GUIDE.md docs/
mv PRODUCTIVITY_AND_REVENUE_OPTIONS.md docs/
mv GIG_PICK_MATRIX.md docs/
mv LINKEDIN_DM_TEMPLATES.md docs/
mv LINKEDIN_SEARCH_RUNBOOK.md docs/

# 6. Delete the rest
ls *.md | grep -v "CLAUDE.md\|README.md" | while read f; do
  rm "$f"
done

# 7. Verify
ls *.md
# Should show only CLAUDE.md and README.md at root
ls docs/*.md
# Should show consolidated docs
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Reduces 239 files to ~10
- Rule 6 (Quality): ✅ Single source of truth

---

### C2. Condense X:\GITHUBREPO Root Files

**Why:** 100+ orphaned files at X:\GITHUBREPO root — audit logs, test reports, config files, lock files.

**Step-by-step:**
```bash
# 1. Create organized directories
cd X:/GITHUBREPO
mkdir -p _archive_logs/
mkdir -p _archive_configs/
mkdir -p _archive_reports/

# 2. Move audit logs
mv apex_audit_results_*.json _archive_logs/
mv comprehensive_testing_audit_*.json _archive_logs/
mv comprehensive_test_results_*.json _archive_logs/
mv health_report_*.json _archive_logs/
mv monitoring_report_*.json _archive_logs/
mv performance_report_*.json _archive_logs/

# 3. Move config files
mv *.config.json _archive_configs/
mv *_config.json _archive_configs/
mv claude_*_config.json _archive_configs/
mv openrouter_*_config.json _archive_configs/

# 4. Move reports
mv comprehensive_*.json _archive_reports/
mv strategic_plan_*.json _archive_reports/
mv validation_*.json _archive_reports/

# 5. Delete remaining orphan files
rm -f *.txt *.log *.db *.json *.lock 2>/dev/null

# 6. Verify
ls *.json *.txt *.log *.lock 2>/dev/null | wc -l
# Should be 0 or very few
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Organizes chaos
- Rule 6 (Quality): ✅ Reduces root clutter

---

### C3. Condense Duplicate AI Tool Configs

**Why:** Multiple config files for the same tools (claude_code_config.json, claude_router_config.json, claude_squad_config.json, etc.)

**Step-by-step:**
```bash
# 1. Identify all claude configs
cd X:/GITHUBREPO
ls *claude*config*.json 2>/dev/null

# 2. Identify all openrouter configs
ls *openrouter*config*.json 2>/dev/null

# 3. Identify all agent configs
ls *agent*config*.json 2>/dev/null

# 4. Keep only the active ones (used by running services)
# Delete the rest
rm -f claude_dns_blocking.json
rm -f claude_hub_config.json
rm -f claude_ide_hooks_config.json
rm -f claude_squad_config.json
rm -f openrouter_intelligence_config.json
rm -f openrouter_ultra_conservative_config.json
rm -f openrouter_working_config.json
rm -f multi_agent_config.json
rm -f master_agent_config.json

# 5. Verify
ls *config*.json | wc -l
# Should be significantly fewer
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Removes config bloat
- Rule 6 (Quality): ✅ Single config per tool

---

## CATEGORY D: SECURITY Operations

> **Golden Rule 3: Detailed errors over graceful failures. Security issues must be visible and halt operations.**

### D1. Secure Exposed Encryption Key

**Why:** `encryption.key` in X:\GITHUBREPO root is a critical security risk.

**Step-by-step:**
```bash
# 1. Move to a secure location
mkdir -p ~/.ssh/keys/
mv X:/GITHUBREPO/encryption.key ~/.ssh/keys/

# 2. Set restrictive permissions
chmod 600 ~/.ssh/keys/encryption.key

# 3. Verify
ls -la ~/.ssh/keys/encryption.key
# Should show -rw------- (600 permissions)
```

**Golden Rule compliance:**
- Rule 3 (Detailed errors): ✅ Security issue addressed
- Rule 6 (Quality): ✅ Proper key management

---

### D2. Secure Exposed .env Files

**Why:** `.env*` files in X:\GITHUBREPO may contain API keys.

**Step-by-step:**
```bash
# 1. Check contents
cat X:/GITHUBREPO/.env 2>/dev/null | head -5
cat X:/GITHUBREPO/.env.* 2>/dev/null | head -10

# 2. If they contain real keys, move to secure location
mkdir -p ~/.config/env/
mv X:/GITHUBREPO/.env* ~/.config/env/

# 3. Add to .gitignore
echo ".env*" >> X:/GITHUBREPO/.gitignore

# 4. Verify
ls X:/GITHUBREPO/.env* 2>/dev/null
# Should return nothing
```

**Golden Rule compliance:**
- Rule 3 (Detailed errors): ✅ Security issue addressed
- Rule 7 (No corrupted data): ✅ Keys not leaked

---

### D3. Secure Exposed api_keys.json

**Why:** `api_keys.json` in X:\GITHUBREPO root contains API keys.

**Step-by-step:**
```bash
# 1. Check contents
cat X:/GITHUBREPO/api_keys.json 2>/dev/null | head -10

# 2. Move to secure location
mv X:/GITHUBREPO/api_keys.json ~/.config/api_keys/

# 3. Add to .gitignore
echo "api_keys.json" >> X:/GITHUBREPO/.gitignore

# 4. Verify
ls X:/GITHUBREPO/api_keys.json 2>/dev/null
# Should return nothing
```

**Golden Rule compliance:**
- Rule 3 (Detailed errors): ✅ Security issue addressed
- Rule 7 (No corrupted data): ✅ Keys not leaked

---

## CATEGORY E: REVENUE Operations

> **Golden Rule: Completion > collection. First dollar in bank > projections.**

### E1. List 2 Fiverr Gigs (Fastest to First Dollar)

**Why:** Zero cost, existing assets, fastest path to revenue.

**Gig 1: AI Music Video Creation**
- **Price:** $150 AUD (penetration pricing)
- **Delivery:** 24-72 hours
- **Description:** "I'll create a professional AI-generated music video using ComfyUI, Wan 2.1, and ACE-Step. You provide the song, I deliver a stunning visual experience."
- **Packages:**
  - Basic ($150): 1-minute video, standard quality
  - Standard ($300): 2-minute video, custom style
  - Premium ($500): 3-minute video, character consistency, effects

**Gig 2: Custom ComfyUI Workflow**
- **Price:** $200 AUD (penetration pricing)
- **Delivery:** 24-48 hours
- **Description:** "I'll create a custom ComfyUI workflow tailored to your aesthetic. Perfect for AI artists, content creators, and studios."
- **Packages:**
  - Basic ($200): Simple workflow, 1 style
  - Standard ($400): Complex workflow, 3 styles
  - Premium ($600): Enterprise workflow, documentation, support

**Step-by-step:**
```bash
# 1. Create Fiverr account (if not exists)
# 2. Create gig listings with above details
# 3. Upload portfolio pieces (run ComfyUI workflows, save outputs)
# 4. Set delivery times
# 5. Enable instant delivery for basic packages
```

**Golden Rule compliance:**
- Rule 6 (Quality): ✅ Ships at "good enough"
- Rule 8 (Close #1 first): ✅ Focuses on fastest path

---

### E2. Send 25 LinkedIn DMs (Highest Value per Deal)

**Why:** Highest value per deal ($2,500-5,000 for security audit).

**Target profile:** AI tool founders with <10 employees.

**Step-by-step:**
```bash
# 1. Open LINKEDIN_DM_TEMPLATES.md
# 2. Open leads_2026-06-25.csv
# 3. For each target:
#    a. Visit their LinkedIn profile
#    b. Check recent posts for pain points
#    c. Personalize DM template
#    d. Send connection request + message
# 4. Track responses in leads_2026-06-25.csv
```

**Golden Rule compliance:**
- Rule 6 (Quality): ✅ Personalized outreach
- Rule 8 (Close #1 first): ✅ Focuses on highest value

---

### E3. Create Carrd Landing Page (Enables Professional Invoicing)

**Why:** Enables Stripe payments and Calendly booking.

**Step-by-step:**
```bash
# 1. Go to carrd.co
# 2. Create new site
# 3. Add:
#    - Hero section: "AI Automation Services"
#    - Services section: Music Video, ComfyUI, Security Audit
#    - Pricing section: Link to Stripe
#    - Booking section: Link to Calendly
#    - Contact section: Email form
# 4. Set up Stripe payment links for each service
# 5. Set up Calendly for consultations
# 6. Publish
```

**Golden Rule compliance:**
- Rule 4 (Simplicity): ✅ Carrd is simple, not WordPress
- Rule 9 (Ship now): ✅ "Good enough" landing page

---

## CATEGORY F: AUTOMATION Operations

> **Golden Rule: Local-only deployment. You run your own instance.**

### F1. Verify All 3 Scheduled Tasks Fire Correctly

**Why:** Ensures automation actually works.

**Step-by-step:**
```bash
# 1. Run morning briefing manually
python tools/01_morning_briefing.py --no-ai
# Check: morning_briefing.txt created?

# 2. Run YouTube harvest manually
python tools/02_youtube_to_archon.py --dry-run --channels config/youtube_channels.txt
# Check: transcripts-dryrun/ created?

# 3. Run Archon crawl manually
powershell -ExecutionPolicy Bypass -File tools/04_archon_daily_crawl.ps1 -WhatIf
# Check: should show "WhatIf: would POST to..." without actual network call

# 4. Verify scheduled tasks exist
schtasks /Query /TN AntigravityMorningBrief
schtasks /Query /TN ArchonYouTubeHarvest
schtasks /Query /TN ArchonDailyCrawl
```

**Golden Rule compliance:**
- Rule 3 (Detailed errors): ✅ Verifies automation works
- Rule 6 (Quality): ✅ Tests before relying on it

---

### F2. Wire YouTube Harvest → Archon KB

**Why:** Knowledge base grows daily with relevant content.

**Step-by-step:**
```bash
# 1. Run harvest in non-dry-run mode
python tools/02_youtube_to_archon.py --channels config/youtube_channels.txt

# 2. Check Archon KB
curl http://localhost:8181/api/knowledge/items | head -20

# 3. Verify transcripts were uploaded
# Check Supabase for new documents
```

**Golden Rule compliance:**
- Rule 1 (Local-only): ✅ Runs locally
- Rule 6 (Quality): ✅ Verifies upload worked

---

## CATEGORY G: STRATEGIC Operations

> **Golden Rule: Quality over speed. Understand the problem before solving it.**

### G1. Move Archon Off C:\Users\karma

**Why:** Stops dotdir bleed. The OS profile is acting as your workspace.

**Step-by-step:**
```bash
# 1. Create new location
mkdir -p C:/dev/archon

# 2. Clone Archon to new location
cd C:/dev/archon
git clone <archon-remote> .

# 3. Copy your custom files
cp C:/Users/karma/tools/* C:/dev/archon/tools/
cp C:/Users/karma/config/* C:/dev/archon/config/

# 4. Update .env files
cp C:/Users/karma/.env C:/dev/archon/.env

# 5. Verify
cd C:/dev/archon
git status
python -m py_compile tools/01_morning_briefing.py

# 6. Update scheduled tasks to new path
schtasks /Delete /TN AntigravityMorningBrief /F
schtasks /Create /SC DAILY /TN AntigravityMorningBrief /TR "python C:\dev\archon\tools\01_morning_briefing.py --tts" /ST 09:00 /F
```

**Golden Rule compliance:**
- Rule 1 (Local-only): ✅ Still local, just cleaner location
- Rule 4 (Simplicity): ✅ Stops the bleed
- Rule 6 (Quality): ✅ Proper workspace separation

---

### G2. Clean Up X:\GITHUBREPO (Delete 200+ Dead Dirs)

**Why:** 90% dead weight. Frees disk space, reduces confusion.

**Step-by-step:**
```bash
# 1. Run A5 (Delete 200+ Dead Directories)
# 2. Run A2 (Delete 39 Orphan Databases)
# 3. Run A3 (Delete 8 Stale Lock Files)
# 4. Run A4 (Delete 4 Redundant Backups)
# 5. Run C2 (Condense Root Files)
# 6. Run C3 (Condense Duplicate Configs)
# 7. Run D1-D3 (Secure Exposed Keys)
# 8. Verify
ls -d */ | wc -l
# Should be significantly fewer
du -sh X:/GITHUBREPO/
# Should be significantly smaller
```

**Golden Rule compliance:**
- Rule 2 (No back-compat): ✅ Removing replaced/unused code
- Rule 4 (Simplicity): ✅ Massive clutter reduction
- Rule 6 (Quality): ✅ Cleans up mess

---

## Quick Reference: All Options by Category

| Category | Options | Total | Fastest | Highest Impact |
|---|---|---|---|---|
| **DELETE** | A1-A5 | 5 | A3 (lock files, 10 min) | A5 (200+ dirs, 4 hrs) |
| **ARCHIVE** | B1-B2 | 2 | B1 (already done) | B2 (decision framework) |
| **CONDENSE** | C1-C3 | 3 | C3 (configs, 30 min) | C1 (239 .md files, 2 hrs) |
| **SECURITY** | D1-D3 | 3 | D1 (encryption.key, 5 min) | D2 (.env files, 15 min) |
| **REVENUE** | E1-E3 | 3 | E1 (Fiverr, 2 hrs) | E2 (LinkedIn, 2 hrs) |
| **AUTOMATION** | F1-F2 | 2 | F1 (verify tasks, 1 hr) | F2 (YouTube harvest, 2 hrs) |
| **STRATEGIC** | G1-G2 | 2 | G1 (move Archon, 4 hrs) | G2 (clean X:, 4 hrs) |
| **Total** | | **20** | | |

---

## Recommended Execution Order

### Day 1 (Today): Security + Quick Wins
1. D1 — Secure encryption.key (5 min)
2. D2 — Secure .env files (15 min)
3. D3 — Secure api_keys.json (15 min)
4. A3 — Delete 8 lock files (10 min)
5. A4 — Delete 4 backup duplicates (5 min)
6. A1 — Delete 5 dead repos (30 min)

### Day 2: Revenue Setup
7. E1 — List 2 Fiverr gigs (2 hrs)
8. E3 — Create Carrd landing page (2 hrs)

### Day 3: Outreach
9. E2 — Send 25 LinkedIn DMs (2 hrs)
10. F1 — Verify scheduled tasks (1 hr)

### Day 4-5: Condense
11. C1 — Condense 239 .md files (2 hrs)
12. C3 — Condense duplicate configs (30 min)

### Day 6-7: Major Cleanup
13. A2 — Delete 39 orphan databases (30 min)
14. A5 — Delete 200+ dead directories (4 hrs)
15. C2 — Condense X:\ root files (1 hr)

### Month 1: Strategic
16. G1 — Move Archon off C:\Users\karma (4 hrs)
17. G2 — Full X:\GITHUBREPO cleanup (4 hrs)

---

*Authoritative source for all options. Updated: 2026-06-25*
