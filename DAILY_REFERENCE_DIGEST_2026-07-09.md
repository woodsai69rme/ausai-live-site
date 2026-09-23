# Daily Reference-Docs Digest &mdash; 2026-07-09 (cont.)

> If you only have time to read one new doc today, read this one. Each
> row links to the full artefact; bullets give you the one-sentence gist.

## 5 new top-level reference docs (at repo root)

| Path | One-line summary | Lines |
|---|---|---|
| `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` | 2026 YouTube transcript + AI content-factory + ComfyUI-video + voice-cloning GitHub ecosystem, anchored to the workspace's existing 12 YouTube files. 7 sections: transcript layer (jdepoix &rarr; yt-dlp &rarr; faster-whisper fallback), agentic shift, Wan2GP/LTX 2.3 ComfyUI nodes, voice-clone comparison, prioritised actions in 3 ROI tiers, NOT-TO-DO list. | ~400 |
| `HARDWARE_SHOPPING_LIST_2026.md` | Every laptop &rarr; display + peripheral connection method &mdash; 14 categories (cable / USB-C / hub / TB dock / MST / adapter / wireless / app-RDP / game-streaming / USB-tunneling / software-KVM / phone-as-display / cloud-desktop / hardware-KVM), plus Tier 1 ($30-60) / Tier 2 ($90-200, **recommended**) / Tier 3 ($200-450) hardware tables, virtual connections (Sunshine+Moonlight), cables, and a mega-decision-tree. | ~600 |
| `SUNSHINE_MOONLIGHT_STUP_SETUP.md` | _(placeholder &mdash; actual file is `SUNSHINE_MOONLIGHT_SETUP.md`)_ GPU-accelerated remote-desktop install guide: Step 0 PowerShell diag &rarr; host (Sunshine) install &rarr; client (Moonlight) install &rarr; pairing &rarr; firewall exception &rarr; uninstall. RTX 4060 NVENC means very low latency. Documented, NOT auto-installed &mdash; interactive decisions left with the user. | ~250 |
| `AWESOME_YOUTUBE_REPOS_2026.md` | Curated-list-of-curated-lists companion to the YouTube research. Big Three front-ends (FreeTube / Invidious / Piped), yt-dlp status, 15-niche catalog (FFmpeg / video-editing / AI agents / self-hosted / etc.), champion picks (`sitkevij/awesome-video` + `tankvn/awesome-ai-tools` + `avinash201199/awesome-youtube-playlists`), maintenance warning + heuristic for picking alive repos. | ~250 |
| `REFERENCE_DOCS_INDEX.md` | Single-page index + cross-link hub for the 4 docs above. The `START_HERE` entry point when looking for shipping hardware setups, deep-dive reports, or env setup guides. | ~60 |

## 3 cross-link / index updates

| Path | Change |
|---|---|
| `GRAND_SUMMARY.md` | +2 START-HERE rows (laptop &rarr; display + peripherals; cable-free remote-desktop via Sunshine + Moonlight). System-count unchanged (reference docs are workspace-level). |
| `WORKSPACE_INDEX.md` | +Reference-docs line in the header pointing at `REFERENCE_DOCS_INDEX.md`. No row-count delta. |
| `CHANGELOG.md` | New `## 2026-07-09 (cont.)` entry documenting the reference-docs workstream; disambiguated from the morning `## 2026-07-09` Mobile-Recovery entry on the same date. |

## Portable offline copies (`_DOCS_ARCHIVE/`)

| File | Size | Format | Use case |
|---|---|---|---|
| `HARDWARE_SHOPPING_LIST_2026.html` | ~28 KB | Standalone HTML w/ embedded CSS + `@media print` | Open in Edge/Chrome for screen reading |
| `HARDWARE_SHOPPING_LIST_2026.pdf` | ~800 KB | Binary PDF (Chrome headless `--print-to-pdf`) | True portable; email, print, archive |
| `SUNSHINE_MOONLIGHT_SETUP.html` | ~12 KB | Standalone HTML w/ embedded CSS + `@media print` | Open in Edge/Chrome for screen reading |
| `SUNSHINE_MOONLIGHT_SETUP.pdf` | ~240 KB | Binary PDF (Chrome headless `--print-to-pdf`) | True portable; email, print, archive |

Generation recipe: Python `markdown` lib (`extra` + `fenced_code` + `tables`) renders HTML; `chrome --headless --disable-gpu --no-sandbox --print-to-pdf --no-pdf-header-footer` renders the PDF. Re-runnable any time.

## Reading paths

- **Just want hardware?** &rarr; `HARDWARE_SHOPPING_LIST_2026.md` (start at the Tier 2 / "RECOMMENDED" row).
- **Just want remote desktop?** &rarr; `SUNSHINE_MOONLIGHT_SETUP.md` (start at Step 0).
- **Need to find a YouTube repo that already exists?** &rarr; `AWESOME_YOUTUBE_REPOS_2026.md`.
- **Want to build something new on top of YouTube?** &rarr; `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` &sect;3 + &sect;6.
- **Want to know what works today / what's deprecated?** &rarr; `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` &sect;7 (NOT-TO-DO).
- **Want a single anchor for ALL of the above?** &rarr; `REFERENCE_DOCS_INDEX.md`.

## Commits this workstream

| SHA | Subject |
|---|---|
| `db2e51b36` | `docs(reference): add 5 top-level reference docs at repo root` |
| `4eccfdfe8` | `docs(index): cross-link reference docs from 3 index docs` |
| _(next)_ | `docs(reference): add daily-digest + binary PDFs` &mdash; this digest + the 2 PDFs |

## Outstanding (after this round)

- **PDF generation is reproducible**: re-render any time via `chrome --headless --print-to-pdf=<name>.pdf file:///.../<name>.html` (no admin / no install required). If you want true `wkhtmltopdf` binary PDFs (higher fidelity for nested tables), install wkhtmltopdf into `C:\Program Files\wkhtmltopdf\bin\` yourself (admin needed) and re-point the render command.
- **HTML files in `_DOCS_ARCHIVE/` are generated artefacts**, deliberately NOT in git (they get stale on every source change &mdash; regenerate from the `.md` source).
- **Push to remote pending** &mdash; all 2 commits are still local-only. Run `git push origin master` when ready (already wired to `origin` per repo config).
