# Dashboard System v3.1.0 — Release Notes

## Summary

**Tag:** `dashboard-system-v3.1.0`
**Date:** 2026-07-13
**Branch:** `master`
**Commits since v2.5.0:** 7 (+ 2 docs commits)
**Major change:** ESM migration + URL deep-linking + WAI-ARIA tablist + global cross-tab Spotlight search (Ctrl+K).

## What's new in 3.1.0

| Feature | Where |
|---|---|
| Global cross-tab Spotlight search (Ctrl+K overlay) | `dashboards.mjs` — ~145 new lines + 2 patched listeners |
| Spotlight full reference | [`DASHBOARD_ARCHITECTURE.md`](DASHBOARD_ARCHITECTURE.md) → `## Spotlight overlay (v3.1.0)` (keyboard-handler-order + ARIA listbox pattern + card-index snapshot) |
| ES module migration (deferred via `type="module"`) | `dashboards.mjs` (was `dashboards.js`; same IIFE) |
| WAI-ARIA tablist + roving tabindex | `dashboards.mjs` — `global.syncTabARIA(activeName)` |
| URL hash deep-linking (`#tab=<name>` / legacy `#tab-X`) | `dashboards.mjs` — `global.parseTabHash` + `hashchange` listener + cold-load `initFromHash` |
| Modal background scroll-lock | `dashboards.mjs` — paired `body.style.overflow` set/revert |
| linkedom-based test migration | `tools/test_dashboards.js` — ~200 LOC removed; spec-compliant |
| 14 test categories / 61 individual OK lines | `tools/test_dashboards.js` (Cats 1–14) |
| 4-file `verify_dashboard.py` 4/4 VALID | pre-commit hook + GitHub Actions unchanged |
| 3 HTML dashboards remain on the same `dashboards.mjs` | `UNIFIED_MASTER_DASHBOARD.html`, `AI_TOOLS_DASHBOARD.html`, `AUSAI_OPS_DASHBOARD.html` |

## What's gone in 3.1.0

- **`dashboards.js` (IIFE format)** — entirely renamed and refactored as `dashboards.mjs` (strict deferred ES module). Same wire-format behavior.
- **Hand-rolled DOM stubs** — ~250 lines of custom test-mock code deleted; replaced by `linkedom ^0.18.13` for spec-compliant classList / dataset / event dispatch. 2 polyfills added inline (KeyboardEvent shim + activeElement override).
- **`<script src="dashboards.js">` loader pattern** — replaced by `<script type="module" src="dashboards.mjs">` in all 3 HTML files. `git mv` preserves the file history.

## Routing milestones

> **Note:** `dashboard-system-v3.1.0` is the only actual git tag in this lineage. Versions v3.0 and v3.1 are **conceptual milestones** used for narrative clarity in the routing milestones below. To retroactively tag a sub-milestone: `git tag -a dashboard-system-v3.0 <commit>`.

### v2.5 — Bundled docs release (2026-07-12)

The pre-v3.1.0 release. Three months of dashboards work summarized in `GITHUB_TAG_NOTES.md` v2.5 with 14 commits, 12 test categories, full modal system extracted.

### v3.0 (Architecture & a11y cycle, 2026-07-13)

Bundles **E02 + E01 + E04 + E05 + E03** (5 commits). The whole architecture + a11y cycle.

- **v3.0-beta** — modal background scroll-lock (E02, `8cb10cf28`). Mouse-wheel scroll bleed behind modal backdrop is fixed.
- **v3.0-rc1** — WAI-ARIA tablist + roving tabindex (E01, `f1d3db0a8`). `global.syncTabARIA` keeps screen-reader behavior in lockstep with mouse/keyboard activation.
- **v3.0-rc2** — `linkedom` migration for `tools/test_dashboards.js` (E04, `a94c64598`). 250-line hand-rolled DOM mock replaced by ~50-line real-DOM setup.
- **v3.0.0** — `dashboards.js` → `dashboards.mjs` deferred ES module rename (E05, `9a7a2696c`). 3 HTML loader swaps + 1 test loader swap + 4 doc-only patches. IIFE preserved (no `export` keywords added).
- **v3.0.1** — URL hash deep-linking (E03, `7d74c5e37`). `#tab=<name>` parses + dispatches on cold-load; `hashchange` listener for back/forward + fragment-link clicks; tab-nav writes hash via `replaceState`.

### v3.1 — Global Ctrl+K Spotlight overlay (2026-07-13)

Bundles **E06** (1 commit). The headline feature of this release.

- **v3.1.0** — global Ctrl/Cmd+K Spotlight overlay (E06, `a752f81b4`). Cross-tab search across every `.card` / `.tool-card` in the active dashboard. ArrowUp/Down nav with wrap; Enter selects → `global.switchTab` + `global.showCardDetail` + E03 hash lockstep. 7 new helpers; 14/14 test cats; 61 OK lines.

**(For per-commit audit + Validation tables + Files-in-this-round lists, see `CHANGELOG.md` post-cont.5-fup-4 through post-cont.5-fup-10.)**

### v3.2 — Spotlight UX polish (E07, 2026-07-13)

Bundles **E07** (1 commit). Three UX enhancements to the E06 Spotlight overlay:

- **Fuzzy substring ranking** — position-biased scoring across `(title, tabName, body)`:
  - `title.startsWith(q)` = 100; `title.includes(q)` = 40
  - `tabName.startsWith(q)` = 20; `tabName.includes(q)` = 10
  - `body.includes(q)` = 1
  - Results sort descending by score (stable tie-break by insertion position). Cap at 12.
- **Recency-sorted results** — selected cards persist to `localStorage` key
  `dashboards.spotlight.recent` (JSON array of `tabname::title` IDs, LRU cap 10).
  Cards present in the list receive a `+1000` score boost so they float to the
  absolute top. Silent no-op when localStorage is unavailable. Recent items also
  render with a small `↻` badge inside the result title span.
- **`:` colon-filter (tolerant)** — input starting with `:<tabprefix>`
  physically filters the candidate pool to tabs whose
  `tabName.toLowerCase().includes(prefix)`; the remainder after the colon
  runs through standard scoring. Example: `:rec adb` → Recovery tab + "adb"
  substring. A lone `:` falls back to the empty-query baseline (no crash).
  Bare `foo` (no colon) preserves the existing substring behaviour.

**(For per-commit audit + Validation tables + Files-in-this-round lists, see `CHANGELOG.md` post-cont.5-fup-11.)**

### v3.3 — Spotlight v3.3 enhancements (E08, 2026-07-13)

Bundles **E08** (1 commit). Three additive UX enhancements on top of the E07 (v3.2) Spotlight baseline:

- **Levenshtein fuzzy fallback** — when substring scoring yields 0 hits AND the query is short (≤12 chars), `updateSpotlightResults` invokes the new IIFE-private `levenshtein(a, b, 2)` helper (iterative Wagner-Fischer with rolling 2-row array, charCodeAt comparison, early-exit sentinel on length-diff or row-min overrun). Filters to distance ≤ 2, ranks ascending, tie-breaks by recency, caps 12. Cover the last 5% of fuzzy UX coverage for typos like "codng" → "coding", "modles" → "models".
- **History dropdown overlay** — separate `#spotlightHistory` div with `.spotlight-history` marker. Click-only, max 10 items, reads `localStorage['dashboards.spotlight.recent']` and resolves each ID against the currently-indexed card DOM. Silently filters detached cards. Empty-state placeholder "No recently viewed cards yet."
- **Ctrl/Cmd+H binding** — toggles the history dropdown; closes the main Spotlight first if both are open. Esc handler extended with a 3rd tier (modal > main spotlight > history).

**(For per-commit audit + Validation tables + Files-in-this-round lists, see `CHANGELOG.md` post-cont.5-fup-12.)**

### Roadmap updates (post-v3.3)

Likely next:

- ~~**Migration of dashboards to ESM-only `dashboards.mjs`** (drop IIFE)~~ Shipped in v3.1.0.
- ~~**Move smoke test from hand-rolled DOM mock to `linkedom`** (formalized lightweight DOM)~~ Shipped in v3.1.0.
- ~~**Spotlight UX polish** (fuzzy match via substring; recency sort with localStorage; multi-result keyboard shortcut)~~ Shipped in v3.2.0.
- ~~**Levenshtein fuzzy distance** (final 5% of fuzzy UX coverage)~~ Shipped in v3.3.0.
- ~~**Persistent spotlight history** (recent-viewed dropdown showing last 10 selections; Ctrl/Cmd+H binding)~~ Shipped in v3.3.0.
- **Wire `git push` to GitHub** — SSH publickey registration still blocks `git push origin`; once resolved, the `dashboard-system-v3.3.0` annotated tag rides in one wave.
- **Quantity-of-LRUs knob** — v3.3 hard-codes the recents cap at 10 (matches v3.2). Future v3.4 could expose `?` + the recents-cap query bypass (e.g. `:rec-cap=20`) for power users.

## Migration from v2.5.0 → v3.1.0

For users with custom dashboards on v2.5.0:

1. **Replace `<script src="dashboards.js">`** with `<script type="module" src="dashboards.mjs">`. The `.mjs` is implicitly deferred, so it runs after `DOMContentLoaded` and after any inline `<script>` blocks. Inline `onclick="openModal(...)"` handlers still work because they reference `window.openModal` at CLICK time (well after module evaluation).
2. **`npm i linkedom`** (or upgrade existing linkedom to `^0.18.13`) for the smoke test runner. The 2 polyfills (KeyboardEvent shim + activeElement override) are documented inline at the top of `tools/test_dashboards.js`.
3. **No API breakage** — all 7 window globals (`openModal`, `showModal`, `showCardDetail`, `closeModal`, `makeP`, `syncTabARIA`, `parseTabHash`) work unchanged. Inline `onclick="openModal('Title', '<html>')"` still works (with the canonical `console.warn` reminder to use `showModal` for user content).
4. **Tab navigation**: nothing to migrate for visual switching if you have inline `switchTab(name)` functions. **OPTIONAL ARIA**: if you want screen-reader behavior to stay in lockstep with mouse/keyboard, add `if (typeof window.syncTabARIA === 'function') window.syncTabARIA(name);` inside your inline `switchTab(name)`. The IIFE's keydown fallback calls `syncTabARIA` automatically only when `window.switchTab` is undefined (i.e., when you opt out of inline switchTab entirely); in that mode visual switching is replica'd by the IIFE, but in dashboards that define their own inline switchTab the IIFE delegates without calling syncTabARIA.
5. **Spotlight overlay**: zero-config — the new E06 overlay is automatic; press Ctrl+K to search across all tabs. If you want to disable it, monkey-patch `window.toggleSpotlight = function(){}` in an early `<script>` block.

The migration is **additive, not breaking**. Legacy `openModal` paths still work. The safe `showModal` path is preferred for new code.

## Roadmap to v3.3

Likely next:

- ~~**Migration of dashboards to ESM-only `dashboards.mjs`** (drop IIFE)~~ Shipped in v3.1.0.
- ~~**Move smoke test from hand-rolled DOM mock to `linkedom`** (formalized lightweight DOM)~~ Shipped in v3.1.0.
- ~~**Spotlight UX polish** (fuzzy match via substring; recency sort with localStorage; multi-result keyboard shortcut)~~ Shipped in v3.2.0 (Levenshtein deferred to v3.3).
- **Levenshtein fuzzy distance** (final 5% of fuzzy UX coverage; deferred from v3.2).
- **Persistent spotlight history** (recent-search dropdown showing last 10 queries; last-opened cards quick-access; keyboard `Cmd+H`).
- **Wire `git push` to GitHub** (SSH publickey registration currently blocks `git push origin`; once resolved, `git push origin master && git push origin dashboard-system-v3.2.0` ships everything in one wave).
- **DASHBOARD_ARCHITECTURE.md update** — Spotlight overlay (v3.1.0) + Spotlight v3.2 enhancements already propagated; future rounds can extend.

## Verification

Run after cloning this tag:

```bash
# 1. Smoke test
node tools/test_dashboards.js
# Expect: 14/14 categories passed, 61 "ok" lines, exit 0

# 2. Per-file verify_dashboard.py (4 files)
python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py dashboards.mjs
python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py UNIFIED_MASTER_DASHBOARD.html
python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py AI_TOOLS_DASHBOARD.html
python COMPLETED_PROJECTS/mobile_backup/verify_dashboard.py AUSAI_OPS_DASHBOARD.html
# Expect: 4 DASHBOARD VALID / JS FILE VALID lines

# 3. Open in browser + test each headline feature
start UNIFIED_MASTER_DASHBOARD.html
# a) Press Ctrl+K — Spotlight overlay opens (test on body, not in modal)
# b) Type "codebuff" — list filters to 1 result; press Enter — modal opens with Codebuff card
# c) Press Ctrl+K again — overlay closes
# d) Open with URL hash: open UNIFIED_MASTER_DASHBOARD.html#tab=unlock — opens directly on Carrier Unlock tab
# e) Press ArrowLeft / ArrowRight on body — tabs cycle with wrap (when modal closed)

# 4. Repeat for AI_TOOLS_DASHBOARD.html and AUSAI_OPS_DASHBOARD.html
start AI_TOOLS_DASHBOARD.html
start AUSAI_OPS_DASHBOARD.html
```

## Tag

`dashboard-system-v3.1.0`

To create after the docs commit:

```bash
git tag -a dashboard-system-v3.1.0 -m "Dashboard System v3.1.0: ESM migration, deep-linking, WAI-ARIA tabs, and Spotlight search"
git push origin dashboard-system-v3.1.0  # explicit push
```

## Outstanding (deferred)

- **SSH push blocked**: as of 2026-07-13, `git push origin master` and `git push origin dashboard-system-v3.2.0` both return `git@github.com: Permission denied (publickey)`. The 7 source commits + 2 docs commits + the `dashboard-system-v3.1.0` + `dashboard-system-v3.2.0` tags (both annotated) are **local-only** at this release. Public key for copy/paste is `~/.ssh/id_ed25519.pub` (SHA256 fingerprint `I+kzrWSavN3srLAdiC9ahIP6tJZdAo5OhKokItmCFo0`); register it on the GitHub account (canonical how-to: `tmp/SSH_PUSH_SETUP.md`). When ready, `git push origin master && git push origin dashboard-system-v3.2.0` ships everything in one wave.
- **Browser-level Ctrl+K hijack**: Firefox uses Ctrl+K for its "search sidebar"; Chrome in some configs intercepts it; the `preventDefault()` in our handler covers most cases. Users with Firefox extensions that override Ctrl+K should use the modal-based navigation instead.
- **DASHBOARD_ARCHITECTURE.md hasn't caught up**: the architecture doc still describes only the modal + tab system; Spotlight should be added in a future propagation commit (out of scope for this round by design — minimal commit scope).
- **CLAUDE.md hasn't been updated to mention Spotlight**: same propagation-marker rationale as above; future round.
