/* dashboards.mjs
 *
 * Shared modal helpers for UNIFIED_MASTER_DASHBOARD.html, AI_TOOLS_DASHBOARD.html,
 * AUSAI_OPS_DASHBOARD.html. Loaded as a deferred ES module via
 * <script type="module" src="dashboards.mjs"></script> in each dashboard.
 *
 * `type="module"` is implicitly deferred by spec, so this file executes after
 * DOMContentLoaded and after any inline <script> blocks in each dashboard.
 * Inline `onclick="openModal(...)"` handlers reference window globals at CLICK
 * time, well after module evaluation, so the defer behaviour is benign here.
 * Note: opening the dashboards via `file://` may hit CORS restrictions in
 * some browsers; serve via http:// (e.g. `python -m http.server`) to be safe.
 *
 * Exposes (all on window, for inline onclick compatibility):
 *   - openModal(title, htmlString)        // legacy, XSS-vulnerable for user content
 *   - showModal(title, bodyNodes)         // safe — takes pre-built DOM nodes
 *   - showCardDetail(card)                // safe — extracts textContent from card
 *   - closeModal()                        // hides modal + restores focus
 *   - makeP(text, className)              // creates a <p> with textContent
 *   - syncTabARIA(activeName)             // keeps ARIA + roving tabindex in sync across tabs
 *   - parseTabHash(hash)                  // E03 helper: parses #tab=X / #tab-X (legacy)
 *
 * URL deep-linking (E03): On cold load, reads `location.hash` and dispatches the
 * matching page's `switchTab` if the hash is `#tab=<name>` (canonical) or
 * `#tab-<name>` (legacy). Hashchange events fire the same dispatch. Tab
 * navigation writes back via `history.replaceState` (no history pollution).
 *
 * The modal HTML is injected synchronously on load via insertAdjacentHTML, so the
 * modal is part of the DOM before any inline script runs. modalOpener is a private
 * IIFE-scoped variable (not a global).
 *
 * Focus-trap + Escape handler are unified into a single keydown listener. Tab cycles
 * within the modal; Shift+Tab reverses; Escape closes; background click closes.
 *
 * The shared `openModal` console.warn message is canonical (no per-dashboard drift).
 */

/**
 * @typedef {Object} ModalEl
 * @property {string} id
 * @property {DOMTokenList} classList
 * @property {(ev: MouseEvent) => void} addEventListener
 * @property {(selector: string) => NodeListOf<HTMLElement>} querySelectorAll
 * @property {() => void} focus
 * @property {string} textContent
 * @private
 */

/**
 * @typedef {Window} GlobalScope
 * Exposes the 5 modal helpers on global so inline `onclick="openModal(...)"` works.
 * @private
 */

(function(global) {
    'use strict';

    // -- Private state (not exposed on window) --
    /** @type {HTMLElement|null} Tracks the element that opened the modal so focus can be restored on close. */
    let modalOpener = null;
    /** @type {HTMLElement|null} Tracks the `.card` wrapper that opened the modal so it can be marked `aria-current="true"` while the modal is showing. */
    let currentCard = null;

    /**
     * WALK-UP: derive `currentCard` from `modalOpener` by walking the DOM via
     * `.closest('.card')`. Called immediately after `modalOpener` is set in
     * {@link openModal} and {@link showModal}. Sets `aria-current="true"` on
     * the card so AT users can tell which card is "the source" of the modal.
     *
     * @returns {void}
     */
    function markCurrentCard() {
        currentCard = (modalOpener && modalOpener.closest) ? modalOpener.closest('.card') : null;
        if (currentCard && currentCard.setAttribute) {
            currentCard.setAttribute('aria-current', 'true');
        }
    }

    /**
     * CLEANUP: clear `aria-current="true"` from `currentCard` and null the
     * reference. Called from {@link closeModal} before `modalOpener` is nulled.
     * No-op when no card was tracked.
     *
     * @returns {void}
     */
    function clearCurrentCard() {
        if (currentCard && currentCard.removeAttribute) {
            currentCard.removeAttribute('aria-current');
        }
        currentCard = null;
    }

    // -- Inject modal HTML synchronously so it's part of the DOM before inline scripts run --
    /**
     * Inline HTML template for the modal. Inserted once at script load via
     * insertAdjacentHTML, so callers can immediately invoke `openModal()`,
     * `showModal()`, or `showCardDetail()` without race conditions.
     * @private
     * @type {string}
     */
    const MODAL_HTML =
        '<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">' +
        '  <div class="modal-content">' +
        '    <div class="modal-header">' +
        '      <h3 class="modal-title" id="modalTitle">Modal Title</h3>' +
        '      <button class="modal-close" id="modalCloseBtn" aria-label="Close dialog">&times;</button>' +
        '    </div>' +
        '    <div class="modal-body" id="modalBody">Modal content goes here</div>' +
        '  </div>' +
        '</div>';
    document.body.insertAdjacentHTML('beforeend', MODAL_HTML);

    // -- Cached references --
    /** @type {ModalEl} */
    const modalEl       = document.getElementById('modal');
    /** @type {ModalEl} */
    const modalTitleEl  = document.getElementById('modalTitle');
    /** @type {ModalEl} */
    const modalBodyEl   = document.getElementById('modalBody');
    /** @type {ModalEl} */
    const modalCloseEl  = document.getElementById('modalCloseBtn');

    /**
     * Hides the modal (.modal.active removed). If a triggering element was
     * captured in `modalOpener`, focus is restored to it. Always safe to call
     * — no-op when modal is already closed.
     *
     * @returns {void}
     */
    function closeModal() {
        modalEl.classList.remove('active');
        // E02: unlock body scroll when the modal closes — paired with the
        // `document.body.style.overflow = 'hidden'` set in openModal() & showModal().
        document.body.style.overflow = '';
        clearCurrentCard();
        if (modalOpener && modalOpener.focus) modalOpener.focus();
        modalOpener = null;
    }

    // -- Close button (no inline onclick; attached here) --
    modalCloseEl.addEventListener('click', closeModal);

    // -- Background click closes modal --
    modalEl.addEventListener('click', function(e) {
        if (e.target === modalEl) closeModal();
    });

    // -- Unified keydown: Escape closes, Tab focus-traps within modal,
    //    Ctrl+1..N / Arrow / Home / End navigate tabs when modal is closed --
    /**
     * Single document-level keydown listener handling modal + tab keyboard
     * interaction:
     *
     * **Modal interaction (always active):**
     *   - `Escape` — closes the modal (even if focus is elsewhere on page).
     *   - `Tab` / `Shift+Tab` — cycles focus within `.modal` focusables; no-op
     *     when modal is not active.
     *
     * **Tab navigation (active only when modal is closed):**
     *   - `Ctrl+1`..`Ctrl+9` (or `Cmd+1..9`) — jumps to nth tab; clamped to last.
     *   - `ArrowLeft` / `ArrowRight` — previous / next tab; wraps around.
     *   - `Home` / `End` — first / last tab.
     *   - Skipped when focus is in `INPUT` / `TEXTAREA` / `SELECT` /
     *     contenteditable (so search boxes aren't hijacked).
     *   - Skipped when `Alt` or `Shift` is held (only `Ctrl` / `Meta` accepted).
     *   - Delegates to `window.switchTab(name)` if the page defines one (each
     *     dashboard has its own inline `switchTab` function); otherwise
     *     replicates the inline pattern (toggle `.tab-content` display, swap
     *     `.tab.active` class).
     *   - Targets focus on the activated `.tab` so AT users get the same
     *     feedback as a mouse click.
     *
     * @param {KeyboardEvent} e — keydown event from `document.addEventListener`
     * @returns {void}
     */
    document.addEventListener('keydown', function(e) {
        // === Modal Escape + Tab focus trap (always) ===
        // E06 (v3.1.0): Esc closes spotlight first if it's the only thing open.
        // Modal wins when both are open (modal is the higher-priority context).
        if (e.key === 'Escape') {
            if (modalEl.classList.contains('active')) {
                closeModal();
            } else if (spotlightEl && spotlightEl.classList.contains('active')) {
                closeSpotlight();
            } else if (spotlightHistoryEl && spotlightHistoryEl.classList.contains('active')) {
                closeSpotlightHistory();
            } else {
                return;
            }
            return;
        }
        if (e.key === 'Tab' && modalEl.classList.contains('active')) {
            const focusables = modalEl.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (!focusables.length) return;
            const first = focusables[0];
            const last = focusables[focusables.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
            return;
        }

        // === E06 (v3.1.0): Spotlight Ctrl/Cmd+K toggle + arrow/Enter navigation ===
        // Toggle on Ctrl+K / Cmd+K (preventDefault to suppress browser default
        // "search sidebar" / "find on page" behavior). No-op if the modal is
        // already open (modal is higher priority than spotlight).
        if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
            if (modalEl.classList.contains('active')) return;
            e.preventDefault();
            toggleSpotlight();
            return;
        }
        // v3.3 (E08) — Ctrl/Cmd+H toggles the spot history dropdown (recently
        // viewed cards). Closes the main spotlight first so both overlays never
        // stack. No-op when modal is active (modal is higher priority than
        // either spotlight context). preventDefault() suppresses browser
        // history-sidebar shortcuts on Chrome / Edge.
        if ((e.ctrlKey || e.metaKey) && (e.key === 'h' || e.key === 'H')) {
            if (modalEl.classList.contains('active')) return;
            e.preventDefault();
            if (spotlightEl && spotlightEl.classList.contains('active')) closeSpotlight();
            toggleSpotlightHistory();
            return;
        }
        // Spotlight-specific keys when overlay is open.
        if (spotlightEl && spotlightEl.classList.contains('active')) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                navigateSpotlight(e.key === 'ArrowDown' ? +1 : -1);
                return;
            }
            if (e.key === 'Enter' && spotlightResults.length && spotlightSelectedIdx >= 0) {
                e.preventDefault();
                selectSpotlightResult(spotlightResults[spotlightSelectedIdx]);
                return;
            }
            // Other keys (Tab, character keys, etc) fall through to default browser
            // handling so the input + result buttons receive them normally. Tab-nav
            // below is gated by Ctrl/Meta so an un-modded Tab won't trigger it.
        }

        // === Tab navigation (only when modal is NOT active) ===
        if (modalEl.classList.contains('active')) return;

        // Skip when focus is in an editable element so typing isn't hijacked.
        const ae = document.activeElement;
        if (ae && (
            ae.tagName === 'INPUT' ||
            ae.tagName === 'TEXTAREA' ||
            ae.tagName === 'SELECT' ||
            (ae.isContentEditable === true)
        )) {
            return;
        }

        // Only Ctrl/Cmd accepted — Alt/Shift would conflict with browser/system.
        if (e.altKey || e.shiftKey) return;

        const tabs = document.querySelectorAll('.tabs .tab');
        if (!tabs.length) return;

        const tabsArr = Array.from(tabs);
        const activeIdx = tabsArr.findIndex(t => t.classList.contains('active'));
        let newIdx = activeIdx;
        let handled = true;

        if ((e.ctrlKey || e.metaKey) && /^[1-9]$/.test(e.key)) {
            newIdx = parseInt(e.key, 10) - 1;
            // Clamp overflow: Ctrl+9 on a 4-tab page maps to last tab (idx 3),
            // not "no-op because index out of range". Capped at 9 in regex
            // above; tabs.length is the documented bound.
            if (newIdx >= tabs.length) newIdx = tabs.length - 1;
        } else if (e.key === 'ArrowLeft') {
            newIdx = (activeIdx - 1 + tabs.length) % tabs.length;
        } else if (e.key === 'ArrowRight') {
            newIdx = (activeIdx + 1) % tabs.length;
        } else if (e.key === 'Home') {
            newIdx = 0;
        } else if (e.key === 'End') {
            newIdx = tabs.length - 1;
        } else {
            handled = false;
        }

        if (!handled || newIdx === activeIdx || newIdx < 0 || newIdx >= tabs.length) {
            return;
        }

        e.preventDefault();
        const targetTab = tabsArr[newIdx];
        const targetName = targetTab.dataset && targetTab.dataset.tab;

        if (typeof global.switchTab === 'function') {
            // Delegate to the page-level handler (each dashboard defines its
            // own inline switchTab that toggles `.tab-content` display + swaps
            // `.active` classes).
            global.switchTab(targetName);
        } else if (targetName) {
            // Fallback: replicate the inline pattern observed across all 3
            // dashboards (display:none on all .tab-content, then display:block
            // on the matching one; .active swap on .tab siblings).
            document.querySelectorAll('.tab-content').forEach(el => {
                if (el.style) el.style.display = 'none';
            });
            const tc = document.getElementById('tab-' + targetName);
            if (tc && tc.style) tc.style.display = 'block';
            tabsArr.forEach(el => el.classList.remove('active'));
            targetTab.classList.add('active');
            // E01: keep aria-selected + roving tabindex in sync when the
            // inline-fallback path is used (i.e. the page does not define its
            // own switchTab). Each inline switchTab also calls syncTabARIA
            // directly so they stay in sync.
            if (typeof global.syncTabARIA === 'function') global.syncTabARIA(targetName);
        }
        // E03: write URL hash so back/forward navigation lands the user on
        // the right tab. Uses setTabHash → replaceState, no-op if no history.
        setTabHash(targetName);
        targetTab.focus();
    });

    /**
     * LEGACY: opens modal with `modalBody.innerHTML = content`.
     *
     * **XSS warning**: this function assigns to `innerHTML`, so untrusted/user-supplied
     * `content` strings will be parsed as HTML. Use {@link showModal} or
     * {@link showCardDetail} for any card-derived or external content.
     *
     * Prints a `console.warn` on every call so callers can audit during development.
     * Callers in the current dashboards use hardcoded literal HTML strings with no
     * user input, so this is safe in those specific use cases.
     *
     * @param {string} title — modal heading text (assigned to `.modal-title` via textContent, escaped).
     * @param {string} content — TRACKED LITERAL HTML to inject into `.modal-body`. UNTRUSTED INPUT MUST use {@link showModal} instead.
     * @returns {void}
     *
     * @example
     * // Safe — content is a hardcoded string literal in source code.
     * openModal('iPhone Pro v2', '<h4>Recovery Menu</h4><p>Press D for diagnostics</p>');
     *
     * @example
     * // UNSAFE — do NOT pass user content here. Use showModal(title, [nodes]) instead.
     * openModal('User Card', userSuppliedHTML); // ← XSS foot-gun!
     */
    global.openModal = function(title, content) {
        console.warn(
            'openModal() uses innerHTML and is XSS-vulnerable for user content. ' +
            'Use showModal() or showCardDetail() for safe DOM construction. ' +
            'See DASHBOARD_ARCHITECTURE.md "Modal safety pattern" for the migration path.'
        );
        modalOpener = document.activeElement;
        markCurrentCard();
        modalTitleEl.textContent = title;
        modalBodyEl.replaceChildren();
        const wrap = document.createElement('div');
        wrap.innerHTML = content; // trusted literal HTML only
        modalBodyEl.appendChild(wrap);
        modalEl.classList.add('active');
        // E02: lock body scroll while modal is open — paired with the revert
        // in closeModal(). Prevents background scroll-bleed (mouse wheel
        // scrolling the page behind the backdrop).
        document.body.style.overflow = 'hidden';
        modalCloseEl.focus();
    };

    /**
     * SAFE: opens modal with pre-built DOM nodes — never assigns to `innerHTML`.
     *
     * Builds modal body by `replaceChildren()` then `appendChild()` for each node.
     * Use this whenever content is derived from user input, card textContent, or any
     * external source. Pairs naturally with {@link makeP} for building paragraphs.
     *
     * @param {string} title — modal heading text (assigned via `textContent`).
     * @param {Array<Node>} [bodyNodes] — array of pre-built DOM nodes (e.g. paragraphs from {@link makeP}); empty array or null is OK.
     * @returns {void}
     *
     * @example
     * const p1 = makeP('First paragraph');
     * const p2 = makeP('Second paragraph', 'special-class');
     * showModal('My Tool', [p1, p2].filter(Boolean));
     */
    global.showModal = function(title, bodyNodes) {
        modalOpener = document.activeElement;
        markCurrentCard();
        modalTitleEl.textContent = title;
        modalBodyEl.replaceChildren();
        if (bodyNodes && bodyNodes.length) {
            bodyNodes.forEach(n => modalBodyEl.appendChild(n));
        }
        modalEl.classList.add('active');
        // E02: lock body scroll while modal is open (covers the showCardDetail
        // call path because showCardDetail ultimately invokes showModal).
        document.body.style.overflow = 'hidden';
        modalCloseEl.focus();
    };

    /**
     * Helper: create a `<p>` with `textContent = text`.
     *
     * Returns `null` if `text` is falsy so callers can `.filter(Boolean)` cleanly.
     * Safe by construction (uses `textContent`, never `innerHTML`).
     *
     * @param {string|null|undefined} text — paragraph text.
     * @param {string} [className] — optional CSS class to add to the `<p>`.
     * @returns {HTMLParagraphElement|null} — new `<p>` element, or `null` when `text` is empty.
     *
     * @example
     * const p = makeP('Hello world');
     * // → <p>Hello world</p>
     *
     * @example
     * const p = makeP('Highlighted', 'callout');
     * // → <p class="callout">Highlighted</p>
     *
     * @example
     * const p = makeP('');
     * // → null (callers can filter(Boolean) to skip)
     */
    global.makeP = function(text, className) {
        if (!text) return null;
        const p = document.createElement('p');
        if (className) p.className = className;
        p.textContent = text;
        return p;
    };

    /**
     * SAFE: extracts descriptive text from a card and opens modal with that content.
     *
     * Looks for `.card` (or any element passed in) and reads:
     *   - `<h3>` for the title
     *   - `<p>` for the description
     *   - `.meta` for technical meta (rendered as a `<div class="code-block">`)
     *   - `.status-pill` for status (rendered with `<strong>` "Status: " prefix)
     *
     * All text is read via `textContent` and rendered via `textContent` or
     * `createElement` — never `innerHTML`. Safe for any user-supplied card content.
     *
     * @param {HTMLElement} card — the card element to inspect. Should contain `<h3>`, optional `<p>`, optional `.meta`, optional `.status-pill`.
     * @returns {void}
     *
     * @example
     * document.querySelector('#toolGrid').addEventListener('click', e => {
     *     const card = e.target.closest('.card');
     *     if (card) showCardDetail(card);
     * });
     */
    global.showCardDetail = function(card) {
        const title      = card.querySelector('h3')?.textContent || 'Tool';
        const desc       = card.querySelector('p')?.textContent || '';
        const metaText   = card.querySelector('.meta')?.textContent || '';
        const statusText = card.querySelector('.status-pill')?.textContent || '';

        const nodes = [];
        const descP = global.makeP(desc);
        if (descP) nodes.push(descP);
        if (metaText) {
            const code = document.createElement('div');
            code.className = 'code-block';
            code.textContent = metaText;
            nodes.push(code);
        }
        if (statusText) {
            const sp = document.createElement('p');
            const b = document.createElement('strong');
            b.textContent = 'Status: ';
            sp.appendChild(b);
            sp.appendChild(document.createTextNode(statusText));
            nodes.push(sp);
        }
        const tip = document.createElement('p');
        tip.className = 'modal-tip';
        tip.textContent = 'Tip: click outside the modal or press Escape to close.';
        nodes.push(tip);
        global.showModal(title, nodes);
    };

    /**
     * E01 (v3.0+1): Sync WAI-ARIA tablist semantics + roving tabindex across
     * the active dashboard's `.tabs .tab` elements.
     *
     * Called by:
     *   - The unified keydown listener's tab-nav fallback path (v3.0+1).
     *   - Each page-level `switchTab(name)` inline function (AI / UNIFIED /
     *     AUSAI) after their own `.active` swap, ensuring mouse clicks and
     *     keyboard shortcut activation produce identical ARIA state.
     *
     * Side effects: writes `aria-selected="true|false"` and `tabindex="0|-1"`
     * on every `.tabs .tab`. Does NOT touch `.active` class (each page's
     * switchTab owns visual highlighting). Does NOT touch focus (the caller
     * decides whether to `.focus()` the new active tab).
     *
     * Idempotent: safe to call repeatedly with the same `activeName`.
     *
     * @param {string} activeName - the `data-tab` value of the tab to mark active.
     * @returns {void}
     *
     * @example
     * // In an inline switchTab (each HTML):
     * document.querySelector('.tab[data-tab="' + name + '"]').classList.add('active');
     * if (typeof window.syncTabARIA === 'function') window.syncTabARIA(name);
     */
    global.syncTabARIA = function(activeName) {
        const allTabs = document.querySelectorAll('.tabs .tab');
        if (!allTabs.length) return;
        allTabs.forEach(tab => {
            if (!tab.dataset && !tab.setAttribute) return;
            const isActive = tab.dataset && tab.dataset.tab === activeName;
            if (typeof tab.setAttribute === 'function') {
                tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
                tab.setAttribute('tabindex', isActive ? '0' : '-1');
            }
        });
    };

    // -- Expose closeModal (inline onclick handlers in dashboards call this) --
    global.closeModal = closeModal;

    // -- E03 (v3.0+1): URL hash deep-linking ------------------------------------
    //
    // Lets users bookmark and share `#tab=<name>` links, plus navigate the tab
    // stack via back/forward. Hash format: `#tab=<name>` (canonical) and the
    // legacy fragment form `#tab-<name>` (auto-normalised to canonical).
    //
    //   - `parseTabHash(hash)` → name string or null
    //   - `setTabHash(name)`   → replaceState to canonical form (no-op if history is missing)
    //   - `syncTabHashFromActive()` → write the active tab's name as the hash
    //   - `hashchange` listener → on browser back/forward or fragment-link click,
    //                             parse new hash and re-dispatch switchTab.
    //   - Module init          → on cold load, read hash and apply if valid.

    /**
     * Parse a `location.hash` string into a tab name.
     *
     * Accepts:
     *   - `#tab=foo`     canonical E03 form
     *   - `#tab-foo`     legacy fragment-href form (e.g. `<a href="#tab-unlock">`),
     *                    auto-normalised away by replaceState on first handler pass
     *   - `#tab`, `#tab=` no name; returns null
     *
     * Returns the bare name (e.g. `unlock`), or null if the hash is absent or
     * doesn't conform. Exposed on `window` for unit tests (v3.0+1 E03).
     *
     * @param {string} hash - the value of `window.location.hash` (or any string with leading `#`)
     * @returns {string|null}
     */
    global.parseTabHash = function(hash) {
        if (!hash || typeof hash !== 'string') return null;
        const m = hash.match(/^#tab(?:=|-)(.*)$/);
        if (!m) return null;
        // Group 1 is the name suffix (empty if `#tab=` or `#tab-`). Empty name
        // counts as no-name — caller must handle as no-op.
        return m[1] || null;
    };

    /**
     * Write the canonical `#tab=<name>` to `location.hash` via `replaceState`
     * so it doesn't accumulate in browser history on every click.
     *
     * No-op when `history.replaceState` is unavailable (sandboxed test
     * environments, browsers with strict CSP, etc). Silently swallows throw.
     *
     * @param {string} name - the data-tab value to write
     * @returns {void}
     */
    function setTabHash(name) {
        if (!name || typeof name !== 'string') return;
        if (!global.history || typeof global.history.replaceState !== 'function') return;
        try {
            global.history.replaceState(null, '', '#tab=' + name);
        } catch (_) { /* silent — CSP / sandboxed env / no history */ }
    }

    /**
     * Read the currently-active tab and write its name to the URL hash.
     *
     * Idempotent — calls repeatedly just normalize the form. Called once at
     * module init (so a non-default active tab is reflected in the URL) and
     * indirectly after each tab change (via the keydown listener below).
     *
     * @returns {void}
     */
    function syncTabHashFromActive() {
        const activeTab = document.querySelector('.tabs .tab.active');
        if (!activeTab || !activeTab.dataset || !activeTab.dataset.tab) return;
        setTabHash(activeTab.dataset.tab);
    }

    /**
     * Module init: read `location.hash` on cold load, parse it, validate
     * against an existing `.tabs .tab[data-tab="<name>"]` element, and
     * dispatch switchTab if so. Invalid / empty hash is silent no-op.
     *
     * @returns {void}
     */
    function initFromHash() {
        const name = global.parseTabHash(global.location && global.location.hash);
        if (!name) return;
        const safe = name.replace(/"/g, '\\"');
        const tabEl = document.querySelector('.tabs .tab[data-tab="' + safe + '"]');
        if (!tabEl) return;
        if (typeof global.switchTab === 'function') {
            try { global.switchTab(name); } catch (_) { /* swallow */ }
        }
        if (typeof global.syncTabARIA === 'function') {
            try { global.syncTabARIA(name); } catch (_) { /* swallow */ }
        }
    }

    /**
     * `hashchange` listener — fires on browser back/forward and on
     * fragment-link clicks (`<a href="#tab-unlock">` etc). On each fire,
     * parse the new hash and dispatch the page-level switchTab so the tab
     * system follows URL state.
     *
     * Inline `onclick="switchTab('...')"` handlers on the same anchors still
     * run synchronously and dominate the visible state for the click, but
     * this listener ensures back/forward navigation also lands on the
     * correct tab. Idempotent — calling switchTab with the already-active
     * name is a no-op (each page's inline switchTab is functionally guarded
     * by classList toggles).
     */
    global.addEventListener('hashchange', function() {
        const name = global.parseTabHash(global.location && global.location.hash);
        if (!name) return;
        const safe = name.replace(/"/g, '\\"');
        const tabEl = document.querySelector('.tabs .tab[data-tab="' + safe + '"]');
        if (!tabEl) return;
        if (typeof global.switchTab === 'function') {
            try { global.switchTab(name); } catch (_) { /* swallow */ }
        }
        if (typeof global.syncTabARIA === 'function') {
            try { global.syncTabARIA(name); } catch (_) { /* swallow */ }
        }
    });

    // Cold-load init: read URL and apply if valid. Must run after the
    // dispatching helpers above, but before scope exit. Both functions
    // are non-throwing by design (guarded `typeof` checks + early returns).
    initFromHash();
    // Also normalise the URL — if hash was `#tab-X` (legacy fragment form)
    // or pointed at the same tab that's already active, this is a no-op for
    // `#tab=<current>`. For `#tab-X` it canonicalises to `#tab=X`.
    syncTabHashFromActive();

    // -- E06 (v3.1.0): Global Ctrl+K Spotlight overlay ----------------------------
    //
    // Cross-tab search overlay. Press Ctrl+K (or Cmd+K on Mac) anywhere in any
    // of the 3 dashboards; the overlay opens with a search input + a live-filter
    // list of every card across every tab. Arrow keys navigate, Enter selects
    // (closes overlay, switches to that tab via global.switchTab, opens the card
    // detail modal via global.showCardDetail). Esc closes, Ctrl/Cmd+K toggles,
    // backdrop click closes.
    //
    //   - buildSpotlightIndex()        one-pass DOM scan; rebuild on each open
    //                                   so newly-rendered cards appear immediately.
    //   - updateSpotlightResults(query) filter + re-render; empty query shows
    //                                   the active tab's cards first (capped at 12).
    //   - navigateSpotlight(delta)     arrow-key selection with wrap.
    //   - selectSpotlightResult(r)     close + switchTab + showCardDetail (E03
    //                                   setTabHash keeps the URL in lockstep).

    /**
     * Spotlight HTML template. Inserted once at script-load via
     * insertAdjacentHTML, so callers can immediately invoke the spotlight
     * handlers without race conditions. Role + aria-label mirror the modal
     * pattern for screen-reader consistency.
     * @private
     * @type {string}
     */
    const SPOTLIGHT_HTML =
        '<div class="spotlight" id="spotlight" role="dialog" aria-modal="false" aria-labelledby="spotlightTitle">' +
        '  <div class="spotlight-backdrop" data-spotlight-close="1"></div>' +
        '  <div class="spotlight-container">' +
        '    <h2 class="spotlight-title" id="spotlightTitle">Search cards across all tabs</h2>' +
        '    <input class="spotlight-input" id="spotlightInput" type="text" placeholder="Type to search..." aria-label="Search across all dashboard tabs" autocomplete="off">' +
        '    <ul class="spotlight-list" id="spotlightList" role="listbox"></ul>' +
        '    <div class="spotlight-footer"><small>Arrows to navigate &middot; Enter to select &middot; Esc to close &middot; Ctrl/Cmd+K toggles</small></div>' +
        '  </div>' +
        '</div>' +
        // v3.3 (E08) — separate history overlay (Ctrl/Cmd+H). Shares the
        // .spotlight class for styling but adds .spotlight-history marker so
        // CSS can tweak layout (no input takes the input-row spot). Click to
        // jump; Esc to close; Ctrl/Cmd+H toggles.
        '<div class="spotlight spotlight-history" id="spotlightHistory" role="dialog" aria-modal="false" aria-labelledby="spotlightHistoryTitle">' +
        '  <div class="spotlight-backdrop" data-history-close="1"></div>' +
        '  <div class="spotlight-container">' +
        '    <h2 class="spotlight-title" id="spotlightHistoryTitle">Recently viewed cards</h2>' +
        '    <ul class="spotlight-list spotlight-history-list" id="spotlightHistoryList" role="listbox"></ul>' +
        '    <div class="spotlight-footer"><small>Click to jump &middot; Esc to close &middot; Ctrl/Cmd+H toggles</small></div>' +
        '  </div>' +
        '</div>';
    document.body.insertAdjacentHTML('beforeend', SPOTLIGHT_HTML);

    /** @type {ModalEl} */
    const spotlightEl       = document.getElementById('spotlight');
    /** @type {HTMLInputElement|null} */
    const spotlightInputEl  = document.getElementById('spotlightInput');
    /** @type {HTMLElement|null} */
    const spotlightListEl   = document.getElementById('spotlightList');
    // v3.3 (E08) — history dropdown refs (separate overlay; no input).
    /** @type {HTMLElement|null} */
    const spotlightHistoryEl      = document.getElementById('spotlightHistory');
    /** @type {HTMLElement|null} */
    const spotlightHistoryListEl  = document.getElementById('spotlightHistoryList');

    /** @type {HTMLElement|null} Element that had focus before the spotlight opened (restored on close). */
    let spotlightOpener            = null;
    /** @type {Array<{tabName:string,tabId:string,cardEl:HTMLElement,title:string,breadcrumb:string}>} Cached filtered results for the current input. */
    let spotlightResults           = [];
    /** @type {number} Index of the currently-highlighted result (0..n-1), or -1 when no results. */
    let spotlightSelectedIdx       = -1;
    /** @type {Array<{tabName:string,tabId:string,cardEl:HTMLElement,title:string,breadcrumb:string}>} Full index rebuilt on each open. */
    let spotlightCardIndex         = [];
    // v3.3 (E08) — spot history dropdown state. No keyboard nav (click-only):
    // the dropdown is short (max 10 items) and Click is the natural pointer
    // interaction. Spotlight history is treated as orthogonal to spotlight
    // search (different overlay, different binding, different rules).
    /** @type {HTMLElement|null} Element that had focus before the history dropdown opened (restored on close). */
    let spotlightHistoryOpener     = null;
    /** @type {Array<{tabName:string,tabId:string,cardEl:HTMLElement,title:string,breadcrumb:string,id:string}>} Cards resolved from getRecentIds() (cap 10, newest first). Items whose card element is missing (DOM rebuilt) are filtered out. */
    let spotlightHistoryResults    = [];

    /**
     * One-pass DOM scan: enumerate every `.card` / `.tool-card` inside any
     * `.tab-content` panel that is associated with a `.tabs .tab[data-tab]`.
     *
     * Title source: first `<h3>` or `<h4>` or `.card-title` child, fallback to
     * `card.textContent` truncated to 120 chars. Cards that yield no title
     * are skipped (e.g. divider / status cards without headings).
     *
     * @returns {Array<{tabName:string,tabId:string,cardEl:HTMLElement,title:string,breadcrumb:string}>}
     */
    function buildSpotlightIndex() {
        const idx = [];
        const tabs = document.querySelectorAll('.tabs .tab');
        tabs.forEach(tab => {
            const tabName = tab.dataset && tab.dataset.tab;
            if (!tabName) return;
            const tabId = 'tab-' + tabName;
            const panel = document.getElementById(tabId);
            if (!panel) return;
            const cards = panel.querySelectorAll('.card, .tool-card');
            cards.forEach(card => {
                const titleEl = card.querySelector('h3, h4, .card-title');
                const title = ((titleEl && titleEl.textContent) || card.textContent || '')
                    .trim().slice(0, 120);
                if (!title) return;
                // v3.2 (E07) — also capture card body (paragraph + meta) so the
                // fuzzy scoring algorithm (see scoreSpotlightResult) can rank
                // body-match cards below title-match cards. Capped at 200
                // chars to keep the index small.
                const body = ((card.querySelector('p')?.textContent || card.querySelector('.meta')?.textContent || '') + '').trim().slice(0, 200);
                // v3.2 (E07) — stable card ID for localStorage recency tracking.
                // Format: `tabname::title` (deterministic across DOM rebuilds).
                const id = tabName + '::' + title;
                idx.push({ tabName, tabId, cardEl: card, title, body, id, breadcrumb: tabName });
            });
        });
        return idx;
    }

    /**
     * v3.2 (E07) — Parse the spotlight input for colon syntax.
     *
     *   `:<tabprefix> [query]` — colon filter plus optional secondary substring.
     *   `:` alone            — fallback to standard empty-query behaviour (no crash).
     *   bare `foo`           — standard substring query.
     *
     * @param {string} input — raw text from the spotlight search input.
     * @returns {{isColon:boolean, tabPrefix:string, q:string}}
     */
    function parseSpotlightQuery(input) {
        const raw = (input || '').trim().toLowerCase();
        if (raw === ':') return { isColon: false, tabPrefix: '', q: '' };
        const m = raw.match(/^:([^\s]+)(?:\s+(.*))?$/);
        if (m) return { isColon: true, tabPrefix: m[1], q: (m[2] || '').trim() };
        return { isColon: false, tabPrefix: '', q: raw };
    }

    /**
     * v3.2 (E07) — Read `dashboards.spotlight.recent` JSON array from
     * localStorage and return up to 10 entry IDs (newest-first).
     *
     * Silent empty array on any parse error or when localStorage is unavailable
     * (Safari private mode, sandboxed iframes, linkedom test runs).
     *
     * @returns {string[]}
     */
    function getRecentIds() {
        try {
            const raw = (global.localStorage && typeof global.localStorage.getItem === 'function'
                ? global.localStorage.getItem('dashboards.spotlight.recent')
                : null) || '[]';
            const arr = JSON.parse(raw);
            return Array.isArray(arr) ? arr.slice(0, 10) : [];
        } catch (_) {
            return [];
        }
    }

    /**
     * v3.2 (E07) — LRU prepend `id` to the recent list in localStorage.
     * Deduplicates existing entries with the same id; caps list at 10.
     *
     * Silent no-op when localStorage is unavailable.
     *
     * @param {string} id — card ID, format `tabname::title`.
     * @returns {void}
     */
    function pushRecentId(id) {
        if (!id || typeof id !== 'string') return;
        try {
            if (!global.localStorage || typeof global.localStorage.setItem !== 'function') return;
            const list = getRecentIds().filter(x => x !== id);
            list.unshift(id);
            global.localStorage.setItem('dashboards.spotlight.recent', JSON.stringify(list.slice(0, 10)));
        } catch (_) {
            /* swallow — Safari private mode / disabled localStorage */
        }
    }

    /**
     * v3.2 (E07) — Position-biased scoring for one result against the query.
     *
     *   startsWith >> includes — title startsWith 100 / includes 40; tab startsWith 20 / includes 10; body includes 1.
     *   recency boost: +1000 if the card is in `recentSet` (so re-findable cards surface at the very top).
     *
     * @param {{title:string,tabName:string,body:string,id:string}} r — indexed card.
     * @param {string} q — lowercased query (already validated as non-empty by caller).
     * @param {Set<string>} recentSet — set of recent IDs for O(1) lookup.
     * @returns {number} score; >= 1 means the card should appear in results.
     */
    function scoreSpotlightResult(r, q, recentSet) {
        const t = (r.title || '').toLowerCase();
        const tab = (r.tabName || '').toLowerCase();
        const b = (r.body || '').toLowerCase();
        const s = (t.startsWith(q) ? 100 : t.includes(q) ? 40 : 0) +
                  (tab.startsWith(q) ? 20 : tab.includes(q) ? 10 : 0) +
                  (b.includes(q) ? 1 : 0);
        return recentSet && recentSet.has(r.id) ? s + 1000 : s;
    }

    /**
     * v3.3 (E08) — Token (word) Wagner-Fischer Levenshtein distance with
     * early-exit when the running minimum row value exceeds `max`.
     *
     * Token-based (not char-based) because dashboard card titles are
     * multi-word strings like "Alpha Item 1", and the common typo pattern
     * is one entire word being misspelled — not a single-character
     * substitution that happens to fall inside a word boundary. Comparing
     * word-arrays gives the semantically expected distance:
     *   - "alpha item 1" vs "alpha iten 1" → 1 (only "item" differs)
     *   - "alpha item 2" vs "alpha iten 1" → 2 ("item", "2" both differ)
     *   - "beta item 1"  vs "alpha iten 1" → 2 ("alpha", "iten" differ)
     *   - "gamma item 1" vs "alpha iten 1" → 3 (>MAX=2, filtered)
     * Same Wagner-Fischer rolling-row algorithm; al/bl now mean token-count
     * instead of char-count.
     *
     * Caller pre-tokenises both inputs (e.g. `.toLowerCase().split(/\s+/).filter(Boolean)`).
     * The fuzzy fallback below relies on this so typo queries like
     * "alpha iten 1" surface Alpha 1 (d=1), Alpha 2 (d=2), Beta 1 (d=2)
     * rather than the two Alpha cards the char-level version would return.
     *
     * Originally shipped as a char-level `levenshtein(a:str, b:str, max)`;
     * Town Crier 16a smoke regression exposed that, for multi-word titles,
     * the char-level distance inflates the cost of any non-aligned edit
     * (e.g. "alpha" → "beta" costs 5 chars, pushing those matches past the
     * d=2 cap). Renamed to `tokenLevenshtein` to make the contract obvious
     * and discourage char-level reuse.
     *
     *   - O(tokens_a × tokens_b) time, O(tokens_b) space (rolling 2 rows).
     *   - Short-circuits when |tokens_a − tokens_b| > max.
     *   - Returns `max + 1` sentinel when the row minimum exceeds `max`.
     *   - Token equality (`a === b`); no per-cell string slicing.
     *
     * @param {string[]} aTokens — first token array (case normalised).
     * @param {string[]} bTokens — second token array (case normalised).
     * @param {number} [max] — early-exit threshold; defaults to Infinity.
     * @returns {number}
     */
    function tokenLevenshtein(aTokens, bTokens, max) {
        if (aTokens === bTokens) return 0;
        if (!aTokens || !aTokens.length) return (bTokens || []).length;
        if (!bTokens || !bTokens.length) return aTokens.length;
        const al = aTokens.length, bl = bTokens.length;
        const cap = (typeof max === 'number') ? max : Infinity;
        if (Math.abs(al - bl) > cap) return cap + 1;
        const v0 = new Array(bl + 1);
        const v1 = new Array(bl + 1);
        for (let i = 0; i <= bl; i++) v0[i] = i;
        for (let i = 0; i < al; i++) {
            v1[0] = i + 1;
            let rowMin = v1[0];
            for (let j = 0; j < bl; j++) {
                const cost = aTokens[i] === bTokens[j] ? 0 : 1;
                v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);
                if (v1[j + 1] < rowMin) rowMin = v1[j + 1];
            }
            if (rowMin > cap) return cap + 1;
            for (let k = 0; k <= bl; k++) v0[k] = v1[k];
        }
        return v1[bl];
    }

    /**
     * Filter `spotlightCardIndex` by `query` and re-render the result list.
     * Empty query prioritises the active tab's cards (so users see their
     * current context first), then fills with cards from other tabs up to 12.
     *
     * v3.2 (E07) extension:
     *   - Fuzzy substring scoring: startsWith >> includes; recency +1000 boost.
     *   - Colon syntax: `:<tabprefix> [query]` filters to tab + then runs scoring on remainder.
     *   - Empty-query baseline (active-tab-first) preserved; recent items float to top within each tier.
     *
     * @param {string} query — user input from the spotlight search box. Empty string = all-tab listing.
     * @returns {void}
     */
    function updateSpotlightResults(query) {
        const parsed = parseSpotlightQuery(query);
        const q = parsed.q;
        const recent = new Set(getRecentIds());
        let results;
        // v3.2 (E07) — colon-only-scope: `:<tabprefix>` (no remainder) filters the
        // pool to tabs matching the prefix and returns up to 12 cards directly.
        // Overrides the active-tab-first baseline so users can scope WITHOUT
        // typing a query. (Pressing Enter on a result fires switchTab to actually
        // jump to that tab; the spec semantics follow Cmd+K → :rec → Enter.)
        if (parsed.isColon && parsed.tabPrefix && !q) {
            const scoped = spotlightCardIndex.filter(r =>
                r.tabName.toLowerCase().includes(parsed.tabPrefix)
            );
            spotlightResults = scoped.slice(0, 12);
            spotlightSelectedIdx = spotlightResults.length ? 0 : -1;
            renderSpotlightResults();
            return;
        }
        if (!q) {
            const activeTabName = (() => {
                const a = document.querySelector('.tabs .tab.active');
                return (a && a.dataset && a.dataset.tab) || null;
            })();
            const sameTab = spotlightCardIndex.filter(r => !activeTabName || r.tabName === activeTabName);
            const otherTab = spotlightCardIndex.filter(r => activeTabName && r.tabName !== activeTabName);
            // v3.2 — recency-boost empty-query tiering (stable sort, recent first within each tier)
            sameTab.sort((a, b) => (recent.has(b.id) ? 1 : 0) - (recent.has(a.id) ? 1 : 0));
            otherTab.sort((a, b) => (recent.has(b.id) ? 1 : 0) - (recent.has(a.id) ? 1 : 0));
            results = sameTab.slice(0, 12);
            if (results.length < 12) {
                results = results.concat(otherTab.slice(0, 12 - results.length));
            }
        } else {
            let pool = spotlightCardIndex.slice();
            if (parsed.isColon && parsed.tabPrefix) {
                pool = pool.filter(r => r.tabName.toLowerCase().includes(parsed.tabPrefix));
            }
            results = pool
                .map(r => ({ r, s: scoreSpotlightResult(r, q, recent) }))
                .filter(x => x.s > 0)
                .sort((a, b) => b.s - a.s)
                .map(x => x.r)
                .slice(0, 12);
        }
        spotlightResults = results;
        spotlightSelectedIdx = results.length ? 0 : -1;
        // v3.3 (E08) — Levenshtein fallback. When substring scoring yields no
        // hits AND the query is short enough to be plausibly a typo (≤12 chars),
        // compute Levenshtein distance (max=2) against each card title. Rank
        // ascending by distance, tie-break by recency boost, cap at 12. This
        // covers the final 5% of fuzzy UX coverage: typos like "codng" ->
        // "coding", "modles" -> "models". Guarded by query length so we don't
        // run O(n*m) over a long query that substring scoring would have caught.
        if (!spotlightResults.length && q && q.length <= 12) {
            const MAX = 2;
            // Tokenise query once (re-used for every card); early-exit when the
            // token array is empty (defensive: q is "" here only on bad input).
            const qTokens = q.split(/\s+/).filter(Boolean);
            if (qTokens.length) {
                const fuzzy = spotlightCardIndex
                    .map(r => {
                        // Pre-tokenise title into word array; cost = 0 iff identical.
                        const aTokens = r.title.toLowerCase().split(/\s+/).filter(Boolean);
                        const d = tokenLevenshtein(aTokens, qTokens, MAX);
                        return { r, d, boost: recent.has(r.id) ? 1 : 0 };
                    })
                    .filter(x => x.d <= MAX)
                    .sort((a, b) => (a.d - b.d) || (b.boost - a.boost))
                    .map(x => x.r)
                    .slice(0, 12);
                if (fuzzy.length) {
                    spotlightResults = fuzzy;
                    spotlightSelectedIdx = 0;
                }
            }
        }
        renderSpotlightResults();
    }

    /**
     * Re-render `spotlightListEl` from `spotlightResults`. Each entry is a
     * `<li role="option">` containing a `<button>` with title + breadcrumb.
     * Click handler maps to `selectSpotlightResult(r)`.
     *
     * @returns {void}
     */
    function renderSpotlightResults() {
        if (!spotlightListEl) return;
        if (!spotlightResults.length) {
            spotlightListEl.replaceChildren();
            const empty = document.createElement('li');
            empty.className = 'spotlight-empty';
            empty.textContent = 'No matches.';
            spotlightListEl.appendChild(empty);
            return;
        }
        const frag = document.createDocumentFragment();
        spotlightResults.forEach((r, i) => {
            const li = document.createElement('li');
            li.className = 'spotlight-item' + (i === spotlightSelectedIdx ? ' selected' : '');
            li.setAttribute('role', 'option');
            li.setAttribute('aria-selected', String(i === spotlightSelectedIdx));
            li.dataset.resultIdx = String(i);
            const btn = document.createElement('button');
            btn.className = 'spotlight-item-btn';
            btn.type = 'button';
            const titleSpan = document.createElement('span');
            titleSpan.className = 'spotlight-item-title';
            titleSpan.textContent = r.title;
            // v3.2 (E07) — recently-viewed marker (↻ small badge appended to title).
            const recentList = getRecentIds();
            if (r.id && recentList.indexOf(r.id) !== -1) {
                const recentBadge = document.createElement('span');
                recentBadge.className = 'spotlight-recent-badge';
                recentBadge.setAttribute('aria-label', 'recently viewed');
                recentBadge.textContent = '\u21bb';
                titleSpan.appendChild(recentBadge);
            }
            const breadcrumbSpan = document.createElement('span');
            breadcrumbSpan.className = 'spotlight-item-breadcrumb';
            breadcrumbSpan.textContent = '\u00a0\u00b7\u00a0' + r.breadcrumb + ' tab';
            btn.appendChild(titleSpan);
            btn.appendChild(breadcrumbSpan);
            btn.addEventListener('click', function() { selectSpotlightResult(r); });
            li.appendChild(btn);
            frag.appendChild(li);
        });
        spotlightListEl.replaceChildren(frag);
    }

    /**
     * Move selection by `delta` (+1 / -1) with wrap-around. Re-renders the
     * result list so the selected entry is visually highlighted.
     *
     * @param {number} delta — +1 (down) or -1 (up); other values are no-ops.
     * @returns {void}
     */
    function navigateSpotlight(delta) {
        if (!spotlightResults.length) return;
        const n = spotlightResults.length;
        let next = spotlightSelectedIdx + delta;
        if (next < 0) next = n - 1;
        if (next >= n) next = 0;
        spotlightSelectedIdx = next;
        renderSpotlightResults();
    }

    /**
     * Open the spotlight overlay. Saves the current focused element as the
     * opener (so close restores focus), rebuilds the card index from current
     * DOM, shows overlay, focuses input, renders the empty-query list.
     *
     * @returns {void}
     */
    function openSpotlight() {
        if (!spotlightEl) return;
        spotlightOpener = document.activeElement;
        spotlightCardIndex = buildSpotlightIndex();
        spotlightEl.classList.add('active');
        if (spotlightInputEl) {
            spotlightInputEl.value = '';
            spotlightInputEl.focus();
        }
        updateSpotlightResults('');
    }

    /**
     * Close the spotlight overlay. Restores focus to the opener (the element
     * that was focused when openSpotlight was called).
     *
     * @returns {void}
     */
    function closeSpotlight() {
        if (!spotlightEl) return;
        spotlightEl.classList.remove('active');
        if (spotlightOpener && typeof spotlightOpener.focus === 'function') {
            spotlightOpener.focus();
        }
        spotlightOpener = null;
        spotlightSelectedIdx = -1;
    }

    /**
     * v3.3 (E08) — Render `spotlightHistoryListEl` from
     * `spotlightHistoryResults`. Each entry mirrors renderSpotlightResults
     * but without the live-filter input / nav / recency badge (the dropdown
     * is short and click-only). Items whose card element no longer exists
     * (DOM rebuilt since the recent ID was recorded) are silently skipped
     * during the openSpotlightHistory() lookup, so this renderer only sees
     * valid entries.
     */
    function renderSpotlightHistoryResults() {
        if (!spotlightHistoryListEl) return;
        if (!spotlightHistoryResults.length) {
            spotlightHistoryListEl.replaceChildren();
            const empty = document.createElement('li');
            empty.className = 'spotlight-empty';
            empty.textContent = 'No recently viewed cards yet.';
            spotlightHistoryListEl.appendChild(empty);
            return;
        }
        const frag = document.createDocumentFragment();
        spotlightHistoryResults.forEach((r, i) => {
            const li = document.createElement('li');
            li.className = 'spotlight-item selected';
            li.setAttribute('role', 'option');
            li.setAttribute('aria-selected', 'true');
            const btn = document.createElement('button');
            btn.className = 'spotlight-item-btn';
            btn.type = 'button';
            const titleSpan = document.createElement('span');
            titleSpan.className = 'spotlight-item-title';
            titleSpan.textContent = r.title;
            const breadcrumbSpan = document.createElement('span');
            breadcrumbSpan.className = 'spotlight-item-breadcrumb';
            breadcrumbSpan.textContent = '\u00a0\u00b7\u00a0' + r.breadcrumb + ' tab';
            btn.appendChild(titleSpan);
            btn.appendChild(breadcrumbSpan);
            btn.addEventListener('click', function() { selectSpotlightHistoryResult(r); });
            li.appendChild(btn);
            frag.appendChild(li);
        });
        spotlightHistoryListEl.replaceChildren(frag);
    }

    /**
     * v3.3 (E08) — Open the spot history dropdown. Looks up each recent ID
     * in the current spotlightCardIndex (rebuilt earlier via buildSpotlightIndex);
     * silently drops entries whose card element is no longer in the DOM
     * (handles dashboards that mutate DOM between opens). No-op when the
     * overlay element is missing.
     */
    function openSpotlightHistory() {
        if (!spotlightHistoryEl) return;
        spotlightHistoryOpener = document.activeElement;
        // Index lookup is fresh per-open so re-indexed card elements (post DOM
        // mutation) are linked. Recent IDs whose card no longer exists are
        // dropped silently — they'll reappear once the user re-selects the
        // card via normal spotlight search.
        const idx = spotlightCardIndex && spotlightCardIndex.length
            ? spotlightCardIndex
            : (spotlightCardIndex = buildSpotlightIndex());
        spotlightHistoryResults = getRecentIds()
            .map(id => idx.find(x => x.id === id) || null)
            .filter(Boolean);
        spotlightHistoryEl.classList.add('active');
        renderSpotlightHistoryResults();
    }

    /**
     * v3.3 (E08) — Close the history dropdown. Restores focus to the opener.
     */
    function closeSpotlightHistory() {
        if (!spotlightHistoryEl) return;
        spotlightHistoryEl.classList.remove('active');
        if (spotlightHistoryOpener && typeof spotlightHistoryOpener.focus === 'function') {
            spotlightHistoryOpener.focus();
        }
        spotlightHistoryOpener = null;
        spotlightHistoryResults = [];
    }

    /**
     * v3.3 (E08) — Toggle spot history dropdown open/closed. Bound to
     * Ctrl/Cmd+H via the global keydown listener. The caller (keydown
     * handler) is responsible for closing the main spotlight overlay first
     * so both don't stack.
     */
    function toggleSpotlightHistory() {
        if (!spotlightHistoryEl) return;
        if (spotlightHistoryEl.classList.contains('active')) {
            closeSpotlightHistory();
        } else {
            openSpotlightHistory();
        }
    }

    /**
     * v3.3 (E08) — Select a history entry: close dropdown, switch tab via
     * global.switchTab, open the card detail modal. Also writes recency
     * (the LRU dedup in pushRecentId just moves the entry to the top).
     */
    function selectSpotlightHistoryResult(result) {
        if (!result) return;
        closeSpotlightHistory();
        pushRecentId(result.id);
        if (typeof global.switchTab === 'function') {
            global.switchTab(result.tabName);
        }
        setTabHash(result.tabName);
        if (result.cardEl && typeof global.showCardDetail === 'function') {
            global.showCardDetail(result.cardEl);
        }
    }

    /**
     * Toggle spotlight open/closed. Bound to Ctrl/Cmd+K via the global keydown
     * listener (see Esc + tab-nav patches above).
     *
     * @returns {void}
     */
    function toggleSpotlight() {
        if (!spotlightEl) return;
        if (spotlightEl.classList.contains('active')) {
            closeSpotlight();
        } else {
            openSpotlight();
        }
    }

    /**
     * Select a result: close the spotlight first (so the modal can open),
     * then switch tab via global.switchTab, then open the card detail modal
     * via global.showCardDetail. Also writes the URL hash via setTabHash so
     * the tab jump is reflected in the address bar (E03 lockstep).
     *
     * @param {{tabName:string,cardEl:HTMLElement}} result — entry from spotlightCardIndex (or equivalent shape).
     * @returns {void}
     */
    function selectSpotlightResult(result) {
        if (!result) return;
        closeSpotlight();
        // v3.2 (E07) — record recency BEFORE switching tabs so the entry floats to
        // the top of the next spotlight open. Idempotent on repeat-click (LRU
        // dedupe handled inside pushRecentId).
        if (result.id) pushRecentId(result.id);
        if (typeof global.switchTab === 'function') {
            global.switchTab(result.tabName);
        }
        setTabHash(result.tabName);
        if (result.cardEl && typeof global.showCardDetail === 'function') {
            global.showCardDetail(result.cardEl);
        }
    }

    // -- Spotlight DOM event wiring (runs once at module init) --
    if (spotlightEl) {
        // Backdrop click closes (matches the modal backdrop-click pattern).
        spotlightEl.addEventListener('click', function(e) {
            const t = e.target;
            if (t && t.dataset && t.dataset.spotlightClose === '1') {
                closeSpotlight();
            }
        });
    }
    if (spotlightInputEl) {
        // Live filter on every keystroke. dispatching a synthetic 'input' event
        // is what tests use to drive the filter path without a real keyboard.
        spotlightInputEl.addEventListener('input', function() {
            updateSpotlightResults(spotlightInputEl.value);
        });
    }

    // -- v3.3 (E08): History dropdown DOM event wiring --
    if (spotlightHistoryEl) {
        // Backdrop click closes (mirrors main spotlight backdrop pattern).
        spotlightHistoryEl.addEventListener('click', function(e) {
            const t = e.target;
            if (t && t.dataset && t.dataset.historyClose === '1') {
                closeSpotlightHistory();
            }
        });
    }

    // -- also: write hash whenever the keydown handler navigates between tabs --
    // (see the patch in the click/keydown branch above for setTabHash calls)
})(window);
