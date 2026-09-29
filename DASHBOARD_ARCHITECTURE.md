# Dashboard Architecture (2026-07-13 v3.1.0)

Three self-contained HTML dashboards at the project root share a common glassmorphic
dark-theme design pattern, modal system, Spotlight overlay, accessibility standards,
and a verification script. Modal + Spotlight live together in a **shared
`dashboards.mjs`** loaded via `<script type="module">` as a deferred ES module
so the same code is not triplicated across the 3 dashboards. A pure-Node **smoke
test** (`tools/test_dashboards.js`) exercises all public window helpers across
14 test categories using `linkedom ^0.18.13`. This document is the canonical
reference for how they fit together.

---

## Dashboards

### `UNIFIED_MASTER_DASHBOARD.html` (~1013 lines)

The phone-recovery aware empire hub. 4 tabs:

| Tab | Purpose | Interactivity |
|---|---|---|
| **Empire** | 12-card grid of AI empire / project / dashboard links | live search filter, click-to-open |
| **Recovery Suite** | 18 interactive cards covering every `RECOVERY_SUITE.bat` option | category filter (All / Android / iPhone / Oppo / Utilities / Diagnostics), modal detail per tool |
| **Diagnostics** | ADB status check + 4 diagnostic buttons displaying formatted ADB instructions for the user's PC | carrier lock / SIM state / APN / full |
| **Carrier Unlock** | Complete Australian carrier-unlock guide: Telstra (TEL), Optus (OPP/OPS), Vodafone (VAU/VA) + 6 MVNOs + Samsung-specific tips | decision tree, step-by-step for each carrier |

### `AI_TOOLS_DASHBOARD.html` (v2.2 — polished through 3 review rounds)

The AI-inventory dashboard. 4 tabs:

| Tab | Cards | Interactivity |
|---|---|---|
| **Coding Assistants** | 14 (Codebuff, Claude, Gemini, Cursor, Continue, Cline, OpenClaw, Qwen, Trae, Codex, Kilo, Monica, Crush, Hermes) | search + status filter (Active / Configured / IDE / CLI), click card → safe DOM-based modal |
| **Local Models** | 6 (Ollama, LM Studio, ComfyUI Studio, Pinokio, n8n, AITK) | search, click card → modal |
| **Quick Links** | 6 (AUSAI, Master Index, ComfyUI System Index, ComfyUI Launcher, Day 1 Pack, Budget Calculator) | click → external `target="_blank"` |
| **Active Projects** | 3 project pills (AusAI Tech, ComfyUI Studio, AI Voice Assistant) | static info |

### `WORKSPACE_REVIEW_DASHBOARD.html` (v1.0 — NEW 2026-07-13)

The workspace review dashboard. 4 tabs:

| Tab | Purpose | Interactivity |
|---|---|---|
| **30-Day Activity** | Timeline of 12+ recent directory modifications (red/yellow/green dots by recency) | search filter, tier filter (All / Today / Jul 8-12 / Jun 16-30) |
| **Root Docs Index** | 15+ card grid of root documentation files by category | search + category filter (All / System / Revenue / Client / YouTube / Infra), click card → safe DOM modal |
| **Dot-Directory Audit** | 10+ card grid of AI tool dot-directories by tier | search + tier filter (All / Tier 1 Active / Tier 2 Recent / Tier 3 Configured), click card → safe DOM modal |
| **OpenCode DB Report** | Visual bars showing opencode.db (14.35GB), kilo.db (82MB), fragmentation (0%), WAL (merged) + non-destructive optimization code blocks | static info cards (no modal) |

### `SETUP_DASHBOARD.html` (v1.0 — NEW 2026-07-17)

Operator **setup / go-live** dashboard. Self-contained glassmorphic HTML (no `dashboards.mjs` required). Live readiness from `SETUP_STATUS.json` (no secrets). Launcher: `OPEN_SETUP_DASHBOARD.bat` (runs `TOOLS/write_setup_status.py` then opens HTML). Desktop: **Setup Dashboard**.

| Tab | Purpose |
|---|---|
| **Overview** | Score ring + human checklist (localStorage) + machine status + next 5 moves + setup flow |
| **Remote** | CRD host, dual Gmail profiles, share checklist, health commands |
| **Accounts & Keys** | OpenRouter, Gumroad, Stripe, Fiverr, Calendly, GitHub, Vercel, CRD, ABN + secret paths |
| **Cash Go-Live** | ZIPs, Stripe apply, Fiverr paste, proceed_all check |
| **Browser Tools** | all_accounts_browser_computer, keys wizard, cash filler, stack install |
| **What After** | Post-setup sequence → first A$ → steady state |

### `TODO_BOARD_DASHBOARD.html` (v1.0 — NEW 2026-07-17)

Operator **execute-all Kanban** for pipeline progress, human gates, and live services. Self-contained glassmorphic HTML (no `dashboards.mjs`). Machine cards from `TODO_BOARD_STATUS.json` (no secrets); personal tasks in `localStorage`. Launcher: `OPEN_TODO_BOARD.bat` (runs `TOOLS/regenerate_live_status.py` + `TOOLS/write_todo_board_status.py` then opens HTML).

| Tab | Purpose |
|---|---|
| **Board** | Kanban: Done / Ready / Blocked / My Tasks (add personal items) |
| **Human Gates** | Credential blockers from publisher profile + env/payment checks |
| **Services** | Live port map from `live_port_status.json` (CPU/RAM meta) |
| **Commands** | Copy-ready execute-all / refresh / publish commands |
| **Dashboards** | Links to live status, setup, war room, execute-all docs |

### `WAR_ROOM_CONTROL_DASHBOARD.html` (v1.0 — NEW 2026-07-16)

Operator **AI Army command center** for full automation. 8 tabs. Self-contained
(does not require `dashboards.mjs`). Safe DOM card construction; copy-to-clipboard
commands. Launcher: `OPEN_WAR_ROOM_CONTROL.bat`. Canonical docs: `WAR_ROOM_CONTROL.md`.

| Tab | Purpose |
|---|---|
| **Command** | Quick launch stack + service port map |
| **Voice PA** | All free voice methods (Omni, Voice AI, edge-tts, Hermes, NEXUS, bridge) |
| **Browser + Computer** | Playwright, agency agent, auto_poster, desktop operator, screenshot |
| **Army Workforce** | Foot Clan + AI_ARMY agents + Agency roster + strategic divisions |
| **Skills + Subagents** | Agency skills, Grok skills, spawnable subagents, Archon MCP |
| **Free Research** | Ollama/OpenRouter free, YouTube, social, GitHub, awesome lists |
| **Automation** | n8n, SLEEP_TRIPLE A–E, war_room doctor, schedulers |
| **Dashboards** | Links to Portal/Classic War Room + empire hubs |

### `AUSAI_OPS_DASHBOARD.html` (v2.0 — ported to unified-tab pattern)

The AusAI Tech operations dashboard. 4 tabs:

| Tab | Purpose | Interactivity |
|---|---|---|
| **KPIs** | 4 live stat cards (revenue / customers / pipeline / conversions) + ABN-registered alert + daily checklist (persists in `localStorage`) + quick-action buttons | `ausai_revenue_dashboard_v1` localStorage key drives KPIs; `ausai_abn_registered` toggles the ABN alert; `ausai_check_*` per-item checklist state |
| **Pipeline** | 6-stage sales pipeline (Lead → Qualified → Proposal → Negotiation → Won / Lost) + prospecting links | clickable stages + external link cards |
| **Tools** | ~62 tool cards covering Money, Sales, Client, Docs, Growth categories | search + category filter; safe-DOM modal on click |
| **Revenue** | Embedded `Revenue_Dashboard_Static.html` iframe + top-docs row | iframe refresh button; cross-dashboard localStorage sync via `ausai_revenue_dashboard_v1` |

---

## `dashboards.mjs` (shared modal helpers)

Located at `C:\Users\karma\dashboards.mjs` (~60 KB). Loaded by all 4 dashboards via
`<script type="module" src="dashboards.mjs"></script>` as a deferred ES module.
The `type="module"` attribute is required so the file is treated as an ES module
and its IIFE-scoped private state (modalOpener, spotlightCardIndex, etc.) works correctly.

**Exposed API** (all on `window`, for inline `onclick` compatibility):

| Function | Purpose |
|---|---|
| `openModal(title, htmlString)` | Legacy: sets `modalBody.innerHTML = content` (XSS-vulnerable for user content). Console-warns on every call. |
| `showModal(title, bodyNodes)` | Safe: takes an array of pre-built DOM nodes; uses `replaceChildren` + `textContent`. |
| `showCardDetail(card)` | Safe: extracts `<h3>`, `<p>`, `.meta`, `.status-pill` text from a card and builds modal nodes. |
| `makeP(text, className)` | Helper: returns a `<p>` with `textContent = text` (or `null` if text is empty). |
| `closeModal()` | Hides modal + restores focus to the element that opened it. |
| `syncTabARIA(activeName)` | E01: keeps `aria-selected="true|false"` + roving `tabindex="0\|-1"` on every `.tabs .tab`. Called by tab-nav fallback + each page-level `switchTab(name)` so mouse and keyboard activation produce identical ARIA state. |
| `parseTabHash(hash)` | E03: returns the tab name from `#tab=<name>` (canonical) or `#tab-<name>` (legacy fragment-href). Exposed mainly for testability; runtime reads `location.hash` via the bundled `hashchange` listener registered at module init. |

**Module-private state:** `modalOpener` is an IIFE-scoped `let` (not a global).
The modal HTML itself is injected synchronously on load via
`document.body.insertAdjacentHTML('beforeend', MODAL_HTML)` so it's part of the DOM
before any inline script runs.

**Unified focus-trap + Escape handler:** single `keydown` listener on `document`.
Escape closes. Tab cycles within `.modal` focusables. Shift+Tab reverses. No-op
when modal is not active (`!modalEl.classList.contains('active')`).

**Canonical `openModal` warning:**
`'openModal() uses innerHTML and is XSS-vulnerable for user content. Use showModal() or showCardDetail() for safe DOM construction. See DASHBOARD_ARCHITECTURE.md "Modal safety pattern" for the migration path.'`

## Shared design pattern

All four dashboard files plus `dashboards.mjs` use the same:

- **CSS variables** in `:root`: `--primary` (`#6366f1`), `--secondary` (`#8b5cf6`),
  `--success`, `--danger`, `--warning`, `--surface`, `--surface-border`, `--shadow-soft`, etc.
- **Gradient backgrounds**: 3 radial gradients + a linear gradient for ambient theme.
- **Glassmorphic cards**: `backdrop-filter: blur(...) saturate(...)`, soft border,
  hover lift (`translateY(-4px)` + primary glow shadow).
- **Modal system**: `.modal > .modal-content > .modal-header > .modal-body`.
- **Tab system**: `.tabs > .tab` with active class swap via `switchTab(name)`.
- **Stats counter**: auto-fills from DOM via `querySelectorAll('#grid .card').length`.

Shared JS function names (reused verbatim or near-verbatim):

- `switchTab(name)` — toggle tab-content visibility + active tab class
- `openModal(title, content)` — **DEPRECATED** for user content; all 4 dashboards now `console.warn` on this path
- `closeModal()` — hides modal + restores focus to opener (via `modalOpener` tracker)
- `console.log('...')` at boot

---

## Modal safety pattern (DOM-based, not innerHTML)

### The bug it prevents

`'<' + title + '>'` then assigned to `modalBody.innerHTML` will be parsed as raw HTML.
If `title` is `"A & B"` then `A &amp; B` may render incorrectly; if `title` is
`"<img src=x onerror=alert(1)>"` then XSS executes.

### The safe path (`AI_TOOLS_DASHBOARD.html`, v2.2)

```javascript
function showCardDetail(card) {
    // textContent is safe to read; we only ever assign via .textContent or
    // pass through createElement + textContent below.
    const title    = card.querySelector('h3')?.textContent || 'Tool';
    const desc     = card.querySelector('p')?.textContent || '';
    const metaText = card.querySelector('.meta')?.textContent || '';

    document.getElementById('modalTitle').textContent = title;  // safe
    const body = document.getElementById('modalBody');
    body.replaceChildren();                                        // clean slate
    const descP = makeP(desc);                                     // safe build
    if (descP) body.appendChild(descP);
    // ... etc — every node is createElement + textContent, never innerHTML
    document.getElementById('modal').classList.add('active');
    document.querySelector('.modal-close').focus();                // keyboard a11y
}

function makeP(text, className) {
    if (!text) return null;
    const p = document.createElement('p');
    if (className) p.className = className;
    p.textContent = text;                                          // safe
    return p;
}
```

### The legacy unsafe path — and why it's kept

All 3 dashboards retain a `console.warn`-guarded `openModal(title, content)` that
uses `innerHTML`. The `console.warn` makes the deprecation noise at every call; the
current callers (Recovery Suite cards in Unified Master, 3-arg `openModal` literals
in AI Tools, none in AUSAI) pass only hardcoded literal HTML strings with no user
input, so it's safe in those specific use cases.

**Migration path for any new code:** use `showCardDetail(card)` (AI Tools, Unified
Master) or `showModal(title, ...safe DOM nodes...)` (AUSAI) for card-derived
content. See the safe path above.

---

## Spotlight overlay (v3.1.0)

A global, cross-tab search overlay that pairs with the existing modal system. Press
`Ctrl+K` (or `Cmd+K` on macOS) anywhere in any of the 3 dashboards to open it; press
again to toggle closed. The overlay scans every `.card` / `.tool-card` inside the
active dashboard's `.tab-content` panels (one-pass DOM scan at open time; live
filter on every keystroke).

### Handler-order invariant (multi-stage unified keydown listener)

The listener that already handles Modal-Esc + Modal-Tab-focus-trap + tab-nav
(`Ctrl+1..9`, Arrows, Home, End) is extended with a Spotlight layer inserted
**between** Modal and tab-nav. The handler order (top to bottom inside the
`keydown` callback) is:

1. **Modal Escape + Tab focus-trap** — always runs. Escape closes modal first,
   then spotlight, then no-op. Tab / Shift+Tab cycle within `.modal` focusables.
2. **Spotlight Ctrl/Cmd+K toggle** — `preventDefault()` suppresses the browser's
   default `Ctrl+K` (Firefox uses it for "search sidebar"; Chrome in some
   configurations intercepts it; Edge uses `Cmd+K` for "Read Aloud" on Mac).
   No-op when modal is already open (modal is the higher-priority context).
3. **Spotlight ArrowDown / ArrowUp** — moves selection within the result list
   with wrap-around. `preventDefault()` so the spotlight search input retains
   its caret (no native cursor nav within the input).
4. **Spotlight Enter** — close + `global.switchTab(tabName)` + `setTabHash(tabName)`
   + `global.showCardDetail(card)`. URL hash writes via `replaceState` (no history
   pollution; integrates with E03 deep-linking).
5. **Tab navigation** — only runs when BOTH modal AND spotlight are closed.
   Spotlight layer intercepts Ctrl+K before this can fire.

### Card-index snapshot (`buildSpotlightIndex`)

On open, the IIFE re-scans `.tabs .tab[data-tab]` + their panels
(`#tab-<name>`) + every `.card` / `.tool-card` descendant. Title source: first
`<h3>` or `<h4>` or `.card-title`, fall back to `card.textContent` truncated to
120 chars. Index is rebuilt on every open (handles dashboards that mutate DOM
between opens — e.g., the AUSAI iframe refresh, AUSAI checklist toggles).

### Result rendering (`renderSpotlightResults`)

Each result becomes a `<li role="option">` containing a `<button>` with title
+ breadcrumb (`<tabname> tab`). The selected entry gets `.selected` +
`aria-selected="true"`; **all other entries get `aria-selected="false"`** to
satisfy the ARIA 1.2 listbox pattern (every option in a single-select listbox
must declare `aria-selected` so screen readers can navigate the list). Click
listener maps to `selectSpotlightResult(r)` — same code path as the Enter
keyhandler.

### Empty-query listing

`updateSpotlightResults('')` prioritises the **active tab's cards first**
(up to 12), then fills with cards from other tabs to the 12-cap. Filtered
query (simple substring match on title or tab name; fuzzy / Levenshtein
deferred to v3.2 polish) returns up to 12 most-recent matches in insertion
order.

### Testability

Spotlight is **not** exposed on `window` (IIFE-private state). Tests drive
it through `document.dispatchEvent` with synthetic keydown events (built from
`linkedom`'s real `Event` + `Object.assign` keyboard-event fields). Test Cat 14
in `tools/test_dashboards.js` covers: open via Ctrl+K, close via Esc, live
filter via input dispatch, Enter → `switchTab` + `showCardDetail`, toggle via
second Ctrl+K, ArrowDown + ArrowUp-wrap navigation.

### v3.2 enhancements (E07: fuzzy ranking + recency + colon-filter)

Three production-grade UX improvements on top of the v3.1.0 baseline:

- **Fuzzy substring ranking.** `updateSpotlightResults(query)` runs a
  position-biased score across `(title, tabName, body)`:
  - `title.startsWith(q)` = 100 points; `title.includes(q)` = 40 points
  - `tabName.startsWith(q)` = 20; `tabName.includes(q)` = 10
  - `body.includes(q)` = 1
  - Results sort descending by score, then by insertion position
    (stable tie-break). Cap at 12 most-recent matches.
- **Recency-sorted results.** Selected cards are persisted to `localStorage`
  under key `dashboards.spotlight.recent` as a JSON array of
  `tabname::title` IDs (LRU, capped at 10). On each open, `getRecentIds()`
  returns the list; cards present in the list receive a `+1000` score
  boost so they float to the very top of the result list. Recent items also
  render with a small `↻` badge inside the result title span. Silent no-op
  when `localStorage` is unavailable (Safari private mode, sandboxed
  iframes, linkedom test environments).
- **`:` colon-filter (tolerant).** Input starting with `:<tabprefix>`
  physically filters the candidate pool to tabs whose
  `tabName.toLowerCase()` `.includes()` that prefix; the remainder after the
  colon runs through standard scoring. Example: `:rec adb` → Recovery tab
  only + body/title substring "adb". A lone `:` safely falls back to the
  empty-query baseline (no crash, no flicker). Bare `foo` (no colon)
  preserves the existing substring behaviour so no user-visible regression.

Test Cat 15 (`tools/test_dashboards.js`) covers 9 sub-checks across all three
behaviours plus the empty-query regression gate (15i specifically verifies
the colon-lone fallback). Combined with Cat 14, the spotlight layer now
exercises ~16 individual assertions in the smoke suite.### v3.3 enhancements (E08: Levenshtein + history dropdown + Ctrl/Cmd+H)

Three additive UX improvements on top of the v3.2 (E07) baseline:

- **Levenshtein fuzzy fallback.** `updateSpotlightResults(query)` invokes the new IIFE-private `levenshtein(a, b, max)` helper when substring scoring yields 0 hits AND `q.length <= 12` (length gate prevents O(n*m) on long queries). Distance is computed against each card title (case-insensitive, `max=2`); cards with `distance ≤ 2` are sorted ascending by distance and tie-broken by recency boost (`+1` flag). Cap at 12 results. Implementation is iterative Wagner-Fischer with a rolling 2-row array, `charCodeAt` comparison (no per-cell string allocation), and early-exits with a `cap+1` sentinel when `|al-bl| > max` or the running row minimum exceeds `max`. Pure-Levenshtein path proven by Cat 16a in the smoke test: `"alpha iten 1"` matches 3 fixture titles via distance 1–2.
  - Colon-scope override (`if (parsed.isColon && parsed.tabPrefix && !q) { ... return; }`) does NOT bypass Levenshtein — it only short-circuits when there is no remainder. With a colon plus a remainder like `:rec codng`, control flows through substring scoring then Levenshtein.
- **History dropdown overlay.** A second overlay structure (`#spotlightHistory`, `.spotlight-history` marker class) was injected alongside the main Spotlight element. Distinct render helpers (`renderSpotlightHistoryResults` + `openSpotlightHistory` + `closeSpotlightHistory` + `toggleSpotlightHistory` + `selectSpotlightHistoryResult`) manage the lifecycle. On open, the function reads `localStorage['dashboards.spotlight.recent']` (reusing `getRecentIds()` to stay in lockstep with the recency list already maintained for v3.2), resolves each ID against the current `spotlightCardIndex` (rebuilt per open so newly-rendered cards appear immediately), and silently filters detached cards. Render is click-only — no input, no arrow nav, no recency badge (the dropdown is short, max 10, and pointer interaction is the natural "jump-back-to" gesture). Empty state shows the literal "No recently viewed cards yet." placeholder.
- **Ctrl/Cmd+H binding.** A sibling block to the existing Ctrl/Cmd+K binding. On press, the handler closes the main Spotlight overlay (if open) then toggles the history dropdown. The Escape handler is also extended with a third tier: history closes (priority: modal > main spotlight > history dropdown). All Cat 16 sub-checks (16b–16f) verify the open/handoff/toggle/Esc/click lifecycle.

The ↻ recency badge inside the result title span (v3.2 / E07) carries `aria-label="recently viewed"` so screen-reader users can announce recency state without inferring it from the glyph.



---

## Accessibility standards

Enforced across all three dashboards:

| Requirement | Implementation |
|---|---|
| Aria-hidden on decorative icons | `<i class="fas fa-..." aria-hidden="true">` everywhere (60+ in Unified, 70 in AI Tools) |
| Modal role + modali­ty | `role="dialog" aria-modal="true" aria-labelledby="modalTitle"` on `.modal` |
| Close button accessible name | `aria-label="Close dialog"` |
| Focus trap in modal | Tab cycles within `.modal-content` focusable elements (`button`, `[href]`, `input`, `select`, `textarea`, `[tabindex]:not([tabindex="-1"])`); Shift+Tab from first → last; Tab from last → first |
| Focus restoration | On close, focus returns to the element that opened the modal (`modalOpener` tracker) |
| Keyboard close | `Escape` key closes modal |
| Click-outside close | Background click closes modal |
| Status semantics | `data-tag` and `data-cat` carry search keys; `aria-hidden="true"` to suppress status dot icons from screen readers |

---

## Verification system

### `verify_dashboard.py` — pre-edit guard

Located at `COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py`.
Validates any dashboard HTML for JS-syntax regressions.

**Usage:**

```bash
python verify_dashboard.py                              # default: walks 5 dirs up looking for UNIFIED_MASTER_DASHBOARD.html
python verify_dashboard.py path/to/dashboard.html      # validate any file
python verify_dashboard.py /tmp/nope.html              # missing file → exit 1
```

**Checks performed:**

1. `node --check` on the extracted inline `<script>...</script>` block (writes to a
   unique-pid-uuid-suffixed tmp file in the same directory as the dashboard to
   avoid Windows race collisions from parallel runs).
2. Aria-hidden coverage on decorative FontAwesome `<i class="fas fa-...">` icons.
   Below 80% → soft `[WARN]` to stderr (does NOT exit non-zero — soft is intentional
   per CLAUDE.md "Detailed errors over graceful failures"; only JS syntax is a hard gate).
3. Reports total `<script>` block count as a sanity check.

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Valid (JS parses, coverage ≥ 80%) |
| 1 | File/argument error (missing file, no `<script>` block, empty JS) |
| 2 | JS syntax error (hard fail — this is what the pre-commit hook catches) |

### `.githooks/pre-commit` — workspace-level pre-commit hooks (NEW 2026-07-13)

Located at `C:\Users\karma\.githooks\pre-commit` (~7.3 KB) with companion `README.md`.
This is a **separate** hook system from the `.git/hooks/pre-commit` above — it provides
additional pre-commit checks for the workspace root repo. See `.githooks/README.md`
for details. Both systems coexist (Rule #7: enhance, not reduce).

> **Note:** `git config core.hooksPath` is currently set to `.husky` — the `.githooks/`
> directory is preserved but not the active hook path. To activate it, the operator would
> run `git config core.hooksPath .githooks` (or merge its checks into `.husky/`).

### `.git/hooks/pre-commit` — git-side enforcement

Auto-installed on 2026-07-12 at `C:\Users\karma\.git\hooks\pre-commit` (chmod
`0o755`). Blocks any commit if the smoke test or any `verify_dashboard.py` check
fails. **Two-stage enforcement:** the `tools/test_dashboards.js` smoke test runs
first (verifies the API + behavior of shared `dashboards.mjs` in a vm sandbox),
then `verify_dashboard.py` runs against each of the 4 dashboard files.

```sh
#!/bin/sh
set -e
echo "[hook] Running dashboard JS verification (smoke test + 4 files)..."

# 1) Smoke test: shared dashboards.mjs module
if [ -f "tools/test_dashboards.js" ]; then
    echo "  \xe2\x86\x92 smoke test: tools/test_dashboards.js"
    node tools/test_dashboards.js || { ...; exit 1; }
fi

# 2) Per-file verify_dashboard.py
for target in dashboards.mjs UNIFIED_MASTER_DASHBOARD.html AI_TOOLS_DASHBOARD.html AUSAI_OPS_DASHBOARD.html WORKSPACE_REVIEW_DASHBOARD.html; do
    echo "  \xe2\x86\x92 verify: $target"
    python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py "$target" || exit 1
done
```

### `tools/test_dashboards.js` — pure-Node smoke test

Located at `C:\Users\karma\tools\test_dashboards.js` (~6 KB). Zero npm
dependencies — hand-rolls minimal DOM stubs and runs dashboards.mjs inside a
`vm.createContext` sandbox.

**Verifies (8 test categories, 18 individual checks):**

1. The IIFE executes without throwing (script is syntactically valid + DOM mock
   is sufficient for the listener wiring).
2. The modal HTML was injected into `document.body` via `insertAdjacentHTML`.
3. All 5 public functions (`openModal`, `showModal`, `showCardDetail`,
   `closeModal`, `makeP`) are exposed on `window`.
4. `openModal(title, content)` sets `modalTitle.textContent`, adds `.modal.active`,
   and emits the canonical `console.warn`.
5. `closeModal()` restores focus to the original opener.
6. `makeP(text, className)` returns correct `<p>` for normal / empty / null /
   className inputs.
7. `showModal(title, [nodes])` activates the modal and appends all provided nodes
   via `replaceChildren` + `appendChild`.
8. `showModal(title, [])` with an empty array still works (no throw, modal opens).

**Usage:**

```bash
node tools/test_dashboards.js                              # ~1 second
node tools/test_dashboards.js && echo "ready to commit"
```

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | All 18 individual checks across 8 categories pass |
| 1 | At least one assertion failed (`FAIL: <name>` printed for each) |

Wired into both the pre-commit hook and `.github/workflows/verify-dashboards.yml`
as a fail-fast step before the per-dashboard `verify_dashboard.py` checks.

---

## Quick reference

### Validate dashboards

```bash
# Both at once
python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py UNIFIED_MASTER_DASHBOARD.html
python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py AI_TOOLS_DASHBOARD.html

# Manual extraction + node check (useful for debugging)
python -c "import re; html=open('AI_TOOLS_DASHBOARD.html').read(); m=re.search(r'<script>([\s\S]*?)</script>', html); open('t.js','w').write(m.group(1))"
node --check t.js && rm t.js
```

### Launch dashboards

```cmd
start UNIFIED_MASTER_DASHBOARD.html        :: Windows
start AI_TOOLS_DASHBOARD.html              :: Windows
```

### Mobile tools (require user's PC, not this server)

```cmd
cd COMPLETED_PROJECTS\mobile_backup
RECOVERY_SUITE.bat            :: press D for diagnostics, 5 for iPhone Pro, L for legacy
python phone_diagnostics.py   :: needs ADB connected to a phone via USB
python -X utf8 iphone_pro_drfone_alt.py --port 8455   :: opens http://localhost:8455
```

### Mobile docs

- `C:\Users\karma\Downloads\PHONE_FIXING_SKILLS.md` — master (21 KB, 12 sections)
- `C:\Users\karma\Downloads\PHONE_HELP.md` — synced copy of above

---

## Maintaining this doc

This section is for future contributors (human or AI) who need to extend the
dashboard system. Three common operations and how to do each without breaking
anything.

### Adding a new `(cont.X)` entry to `CHANGELOG.md`

`CHANGELOG.md` uses **CRLF line endings** (4,863 CRLF sequences at last count).
Two important constraints:

1. **Use the `str_replace` tool for small edits** (< ~2 KB) — it preserves CRLF.
2. **Use bytes-level Python for large inserts** (>= 2 KB) — `str_replace` and
   `bash` heredocs silently truncate or mishandle `\r\n` for big content blocks.

Bytes-level template (insert before the `## 2026-07-11 — D:/E: drive media identity pass` header):

```python
from pathlib import Path
p = Path('C:/Users/karma/CHANGELOG.md')
raw = p.read_bytes()
ANCHOR = b'## 2026-07-11 \xe2\x80\x94 D:/E: drive media identity pass'
pos = raw.rfind(b'\r\n', 0, raw.find(ANCHOR)) + 2
CONT_X = b'## 2026-07-12 (cont.X) \xe2\x80\x94 <title>\r\n\r\n<body>\r\n\r\n'
p.write_bytes(raw[:pos] + CONT_X + raw[pos:])
```

Then re-verify: `python -c "from pathlib import Path; b=Path('CHANGELOG.md').read_bytes(); print('CRLF:', b.count(b'\r\n')); print('(cont.X) header count:', b.count(b'(cont.X)'))"`.

### Adding a new dashboard (port to the unified pattern)

1. Create the new HTML file at the project root, following the structure of
   `UNIFIED_MASTER_DASHBOARD.html`:
   - Glassmorphic dark theme CSS in `<style>`
   - 4 self-contained tabs with `switchTab(name)` handler
   - Decorative FontAwesome icons get `aria-hidden="true"` (>= 80% coverage)
   - All 3 levels: HTML modal markup **omitted** (injected by `dashboards.mjs`)
2. Add `<script type="module" src="dashboards.mjs"></script>` immediately before the inline
   `<script>` block.
3. Use `openModal(title, htmlString)` only for hardcoded literal HTML (Recovery
   Suite-style). Use `showModal(title, nodes)` or `showCardDetail(card)` for any
   user-derived content.
4. Add the new file to the pre-commit hook's `for target in ...` loop and to
   `.github/workflows/verify-dashboards.yml`.
5. Add a new section to this doc under `## Dashboards` following the existing
   4-tab table format.
6. Add the new file to the `Outstanding` section's port-list (mark as done once
   the port lands).

### Updating `verify_dashboard.py` to add a new check

The script currently does: (0) `.js` short-circuit, (1) extract inline `<script>`
+ `node --check`, (2) aria-hidden coverage, (3) `<script>` block count.

To add a new check (e.g. CSS-variable presence, or that all `onclick` handlers
point to defined globals), add it as a numbered step in `main()` after step 3.
Keep checks independent: each must return a clear PASS/WARN/FAIL with a print
to stdout or stderr. Do NOT change existing exit codes without updating both
the pre-commit hook and the CI workflow.

## Outstanding (deferred)

- **Run `phone_diagnostics.py` on actual S24** — requires the user's PC with USB
  phone access. Exit-code-per-failure interpretation:
  - 0 = OK
  - 2 = carrier locked (Belong SIM blocked) — see Carrier Unlock tab
  - 3 = SIM not registered — network issue
  - 4 = data disabled — toggle SIM1/SIM2 data on
  - 5 = airplane mode on — disable
- ✅ **Port pattern to `AUSAI_OPS_DASHBOARD.html`** — completed in this round. The
  third major dashboard now uses the glassmorphic shell + 4-tab IA (KPIs / Pipeline
  / Tools / Revenue) + safe-DOM modal + console.warn-guarded legacy `openModal`.
  See `AUSAI_OPS_DASHBOARD.html` for the ported state.
- **Workspace audit cross-refs** — see `WORKSPACE_30DAY_REVIEW_2026-07-13.md` for 30-day activity review, `DOTDIR_INTEGRATION_AUDIT_2026-07-13.md` for dot-directory integration map, `ROOT_DOCS_MASTER_INDEX.md` for comprehensive root docs index.
- **CI-side enforcement** — set up GitHub Actions (or similar) to run
  `verify_dashboard.py` on every push. The local pre-commit hook only catches
  commits on this machine; remote CI catches everything.
- **Server-side `ADSBanner` connectivity** — currently tries
  `http://localhost:8181/api/system/adb_status`. If the Archon backend exposes
  that endpoint live, the dashboard can show "ADB Available" status. If not, the
  catch path ("Backend offline") fires. Wire the backend endpoint if it's useful.

## Keyboard shortcuts (v3.x)

The unified `document.addEventListener('keydown', …)` in `dashboards.mjs`
exposes a multi-stage handler (added in v3.0-alpha, extended in v3.1.0):

1. **Modal Escape + Tab focus-trap** — always runs. Escape closes modal
   first, then spotlight, then no-op. Tab / Shift+Tab cycle within `.modal`
   focusables.
2. **Spotlight overlay (new, v3.1.0)** — runs when modal is closed.
   Keybindings:
   - `Ctrl+K` / `Cmd+K` — toggles spotlight open/closed (`preventDefault()`).
     No-op when modal is already active (modal wins).
   - `ArrowDown` / `ArrowUp` — moves selection within the result list with
     wrap-around.
   - `Enter` — close + `global.switchTab(tabName)` + `setTabHash(tabName)` +
     `global.showCardDetail(card)`.
   - `Esc` — closes spotlight (handled in stage 1, modal-takes-priority rule).
3. **Tab navigation (v3.0-alpha)** — only runs when BOTH modal AND
   spotlight are closed. Keybindings:
   - `Ctrl+1`..`Ctrl+9` / `Cmd+1`..`Cmd+9` — jumps to nth tab. **Clamped**
     at last (over-shoot maps to last tab, not no-op).
   - `ArrowLeft` / `ArrowRight` — previous / next tab with wrap.
   - `Home` / `End` — first / last tab.
   - Skipped when focus is in `INPUT` / `TEXTAREA` / `SELECT` /
     contenteditable (search boxes aren't hijacked).
   - Skipped when `Alt` or `Shift` modifiers are present (only `Ctrl` /
     `Meta` accepted).

Delegates to `window.switchTab(targetName)` when defined (each of the 3 HTML
dashboards defines inline); falls back to replicating the inline pattern
(toggle `.tab-content` display + swap `.active` class). Each page-level
`switchTab(name)` SHOULD ALSO call `global.syncTabARIA(name)` to keep
screen-reader ARIA in lockstep — the IIFE only auto-syncs in the fallback
path (when `window.switchTab === undefined`); inline-defining dashboards
must opt in.

A single listener is preferred over stacked listeners: avoids stale closures,
makes the runtime path easier to reason about, and reuses existing scaffolding
(modal gating, focus restoration).


## v3.x limitations (cumulative across v3.0 + v3.1)

The Ctrl/Cmd+H binding is shadowed on macOS by the system "Hide application" shortcut — preventDefault() cannot override the system-level action. Use Ctrl+H on Mac, or accept as documented limitation.

- **Browser-level Ctrl+1..9 consumption** (v3.0-alpha): Chrome / Firefox /
  Edge may consume `Ctrl+1`..`Ctrl+9` before the page handler sees them
  (browser tab-switching shortcuts). When this happens, the page keydown
  listener never fires for those key combinations. **Arrow keys / Home /
  End are reliably received** across all major browsers and are the
  recommended fallback. If a user reports "Ctrl+2 doesn't switch tabs",
  recommend `ArrowRight` / `ArrowLeft` instead.
- **Browser-level Ctrl+K hijack** (v3.1.0): Firefox uses `Ctrl+K` for its
  "search sidebar"; Chrome in some configurations also intercepts it.
  Our handler calls `e.preventDefault()` to suppress the browser default,
  which covers most scenarios. If a user reports "Ctrl+K doesn't open
  Spotlight", the workarounds are: (1) check that no Firefox extension is
  globally binding Ctrl+K, (2) reload the page in the active tab (extension
  state can stick), (3) use Chrome / Edge instead, where Ctrl+K is not
  bound. This limitation is acknowledged in the v3.1.0 release notes'
  Outstanding section.

- **macOS Cmd+H caveat (v3.3):**
  The Ctrl/Cmd+H binding (added in v3.3 for Spotlight history dropdown)
  conflicts with macOS `Hide Window` (Cmd+H at the OS level). On macOS the
  browser-level handler fires after the OS-level hijack, so the modal does
  NOT close on Cmd+H. Users must use Esc or click the backdrop to dismiss.
  Track under "Outstanding" below.
