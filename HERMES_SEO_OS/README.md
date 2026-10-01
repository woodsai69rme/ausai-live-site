# Hermes SEO OS — Julian Goldie–style (local AusAI)

> **One-click:** `HERMES_SEO_OS\LAUNCH_HERMES_SEO_OS.bat`  
> **Portal:** `HERMES_SEO_OS\HERMES_SEO_OS.html`  
> **Pipeline:** `python HERMES_SEO_OS\pipeline\seo_pipeline.py --keyword "…"`

Inspired by **Julian Goldie’s Hermes Agent OS / OpenClaw SEO swarm** on YouTube: multi-agent SEO that turns a keyword into content, social, YouTube scripts, outreach, and a publish plan — while you stay in control.

---

## Goldie stack → this PC

| Julian Goldie piece | Your machine |
|---|---|
| Hermes Agent | `hermes-agent/` + this OS |
| OpenClaw gateway | `.openclaw` · :18789 |
| LLM “brain” (Claude etc.) | **Ollama local** + **OpenRouter free** |
| Memory / Obsidian | `HERMES_SEO_OS/memory/` |
| Publish + index | `outbox/` drafts → human publish + GSC |
| SEO calendar | `SEO_CONTENT_CALENDAR.md` |
| Local SEO | `LOCAL_SEO_GUIDE.md` |

---

## 12-agent swarm

See `agents/SWARM.md`. Pipeline runs them as stages:

```
keyword_scout → outline → article → SEO pack → internal links
→ social → YouTube → outreach → publish plan → index → QA
```

---

## Quick start

```bat
HERMES_SEO_OS\LAUNCH_HERMES_SEO_OS.bat
```

Or CLI:

```bat
python HERMES_SEO_OS\pipeline\seo_pipeline.py --keyword "n8n consultant Australia"
python HERMES_SEO_OS\pipeline\seo_pipeline.py --from-bank 0
python HERMES_SEO_OS\pipeline\seo_pipeline.py --list-outbox
```

Requires **Ollama** running (`http://127.0.0.1:11434`) for full drafts. OpenRouter free is used if `TOOLS/core_llm.py` falls back.

---

## Outbox layout

Each run creates:

```
outbox/YYYYMMDD_HHMMSS__slug/
  01_keywords.json
  02_outline.md
  03_article.md          ← main draft
  04_seo_pack.json
  05_internal_links.md
  06_social.md
  07_youtube.md
  08_outreach.md
  09_publish.md
  10_index.md
  11_qa.md
  manifest.json
  README.md
```

---

## Overnight / money loop (Goldie-style)

1. Pick keyword from bank or calendar  
2. Run pipeline  
3. Human edit `03_article.md` (15–30 min)  
4. Publish to AusAI blog / Medium / LinkedIn article  
5. Request indexing + post social pack  
6. Repeat 3×/week → compound traffic → clients  

**Does not auto-publish live** until you change `config.json` → `publish.mode` and add CMS keys (by design — avoids spam risk).

---

## Golden Rules

- Enhance only; personal folders (Rule #8) never accessed  
- No fake case studies or guaranteed #1 ranks  
- Append-only outbox  

---

## Related

- `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md`  
- `HERMES_FREE_SETUP_DOCUMENTATION.md`  
- `PORTAL_WAR_ROOM.html`  
- `MASTER_MONEY_PLAN.md`  
