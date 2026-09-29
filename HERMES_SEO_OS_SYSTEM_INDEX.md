# Hermes SEO OS — System Index

> **Julian Goldie–style multi-agent SEO operating system** on your local AusAI stack.  
> **Start:** `HERMES_SEO_OS\LAUNCH_HERMES_SEO_OS.bat`  
> **Portal:** `HERMES_SEO_OS\HERMES_SEO_OS.html`

## Why this exists

Julian Goldie’s YouTube “Hermes Agent OS / OpenClaw SEO” setup turns one keyword into content, social, video, and ranking ops using a swarm of agents. This folder is that **mission-control idea**, rebuilt for:

- Free **Ollama + OpenRouter** (no Claude lock-in)
- Your **Hermes** install + **OpenClaw** gateway
- **AusAI Tech** brand memory and offers
- Safe **draft outbox** (human publish)

## Quick map

| Path | Role |
|---|---|
| `HERMES_SEO_OS/pipeline/seo_pipeline.py` | 12-stage swarm runner |
| `HERMES_SEO_OS/agents/SWARM.md` | Agent roster |
| `HERMES_SEO_OS/memory/BRAND_VOICE.md` | Offers, tone, CTAs |
| `HERMES_SEO_OS/memory/KEYWORD_BANK.json` | Seed keywords |
| `HERMES_SEO_OS/outbox/` | Generated packs |
| `HERMES_SEO_OS/config.json` | Models, site URL, publish mode |
| `LAUNCH_HERMES_SEO_OS.bat` | Menu launcher |
| `HERMES_SEO_OS.html` | Visual portal |

## Commands

```bat
HERMES_SEO_OS\LAUNCH_HERMES_SEO_OS.bat
python HERMES_SEO_OS\pipeline\seo_pipeline.py --keyword "AI automation consultant Australia"
python HERMES_SEO_OS\pipeline\seo_pipeline.py --from-bank 0
python HERMES_SEO_OS\pipeline\seo_pipeline.py --list-outbox
```

## Related Goldie / Hermes docs (existing)

- `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md`
- `HERMES_FREE_SETUP_DOCUMENTATION.md`
- `SEO_CONTENT_CALENDAR.md`
- `LOCAL_SEO_GUIDE.md`
- `PORTAL_WAR_ROOM.html` (Lane G)

## Money loop

Pipeline drafts → edit → publish on AusAI / LinkedIn → index → social pack → inbound leads → Fiverr/AusAI checkout.
