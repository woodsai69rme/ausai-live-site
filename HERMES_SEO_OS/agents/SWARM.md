# Hermes SEO OS — 12-Agent Swarm

> Modelled on Julian Goldie–style multi-agent SEO OS (Hermes + OpenClaw + LLM brain).  
> Agents run as **sequential pipeline stages** (local) or can be dispatched as Hermes sub-agents.

| # | Agent ID | Role | Output |
|---|---|---|---|
| 1 | `keyword_scout` | Expand seed → long-tails + intent | `01_keywords.json` |
| 2 | `serp_strategist` | Outline SERP-winning structure | `02_outline.md` |
| 3 | `brand_memory` | Inject AusAI offers / CTAs / proof | context blob |
| 4 | `content_writer` | Full draft (1200+ words) | `03_article.md` |
| 5 | `seo_editor` | Titles, meta, H1–H3, FAQ, schema hints | `04_seo_pack.json` |
| 6 | `internal_linker` | Link map to site + related posts | `05_internal_links.md` |
| 7 | `social_clipper` | LinkedIn / Reddit / X / Shorts hooks | `06_social.md` |
| 8 | `youtube_scripter` | 60–90s Shorts + long-form outline | `07_youtube.md` |
| 9 | `backlink_scout` | Outreach targets + pitch angles | `08_outreach.md` |
| 10 | `publisher` | Stage draft for site / WP / Gumroad | `09_publish.md` |
| 11 | `indexer` | Indexing checklist (Search Console, sitemap) | `10_index.md` |
| 12 | `qa_auditor` | E-E-A-T + spam risk + Golden Rules | `11_qa.md` |

## Goldie-style loop (overnight)

```
keyword → research → write → SEO pack → social → draft publish → human approve → go live
```

## Local-first mapping

| Goldie stack | This machine |
|---|---|
| Hermes Agent | `hermes-agent/` + this pipeline |
| OpenClaw | `.openclaw` gateway :18789 |
| Claude brain | OpenRouter free + Ollama |
| Obsidian memory | `HERMES_SEO_OS/memory/` |
| Netlify / WP | `outbox/` drafts → manual or future WP API |
| Omega Indexer | `10_index.md` checklist + GSC manual |
