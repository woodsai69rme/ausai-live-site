# FREE RESOURCES MASTER — AI models, APIs, tools, research

> **Generated:** 2026-07-16  
> **Purpose:** One catalog of **every free (or free-tier) resource** on this stack — local models, cloud free IDs, APIs, CLIs, skills, RAG, voice, media, research.  
> **Dashboard:** `WAR_ROOM_CONTROL_DASHBOARD.html` → tab **Free Resources**  
> **Registry JSON:** `FREE_RESOURCES_REGISTRY.json`  
> **Launcher:** `OPEN_FREE_RESOURCES.bat`  
> **Policy:** OpenRouter is the **only** approved cloud AI path (`CLAUDE.md`). Prefer Ollama offline. Never commit secrets.

---

## 0 · Start here (60 seconds)

| Action | Command |
|--------|---------|
| Open War Room Free tab | `OPEN_WAR_ROOM_CONTROL.bat` → **Free Resources** |
| Free local hub menu | `TOOLS\FREE_LOCAL_HUB.bat` |
| List Ollama models | `ollama list` |
| OpenRouter free ID list | `type ComfyUI\config\openrouter_free_models.txt` |
| Switch free model | `ComfyUI\tools\free_model_switch.bat list` |
| Capability registry | `python TOOLS\free_local_registry.py --list` |
| **Self-test all free stack** | `python TOOLS\test_free_stack.py` |
| Self-test + Ollama answer | `python TOOLS\test_free_stack.py --answer` |
| Drive RAG self-test | `python TOOLS\drive_backup_rag\drive_backup_rag.py self-test` |
| pytest invariants | `python -m pytest tests\unit\test_free_resources_stack.py -q` |
| Drive backup + local RAG | `LAUNCH_DRIVE_BACKUP_RAG.bat` |
| Drive connect (My Drive mount) | `python TOOLS\drive_backup_rag\drive_backup_rag.py drive-connect` |
| What's left (free/drive track) | `notepad WHAT_IS_LEFT_FREE_DRIVE_STACK.md` |
| This doc | `notepad FREE_RESOURCES_MASTER.md` |

**Cost model**

| Tier | Cost | When to use |
|------|------|-------------|
| **Local (Ollama / ComfyUI / SQLite)** | $0 unlimited | Daily coding, RAG, voice, privacy |
| **OpenRouter `:free` models** | $0 (rate-limited) | Cloud when VRAM busy / heavy models |
| **Provider free tiers** (Groq, DeepSeek, Gemini, HF) | $0 with quotas | Optional keys — **prefer OpenRouter** for cloud |
| **Paid** | Real money | Revenue tools only (Stripe/Gumroad); not required for AI core |

---

## 1 · Local AI models (Ollama) — installed free

**Endpoint:** `http://localhost:11434` · `ollama serve` (often auto)

| Name (as installed) | Size | Best for |
|---------------------|------|----------|
| `hf.co/deepreinforce-ai/Ornith-1.0-35B-GGUF:Q4_K_M` | 21 GB MoE | Best coding (~75% SWE-Bench); use CPU MoE offload on 8 GB VRAM |
| `ornith:9b` / `ornith:latest` | 5.6 GB | Fast full-VRAM coding |
| `richardyoung/qwythos-9b-abliterated:latest` | 5.6 GB | Long-context / distill style |
| `minicpm-v:latest` | ~5.5 GB | Vision |
| `gemma4:26b` | 17 GB | Agentic workflows |
| `phi4-mini:latest` | 2.5 GB | Fast STEM; runs **with** ComfyUI |
| `deepseek-r1:8b` | 5.2 GB | Chain-of-thought reasoning |
| `qwen2.5-coder:latest` | 4.7 GB | Default coding fallback |
| `nomic-embed-text:latest` | 274 MB | RAG embeddings (Drive RAG, FTS re-rank) |

**VRAM strategy (RTX 4060 8 GB)**

| ComfyUI state | Prefer |
|---------------|--------|
| Generating | OpenRouter free **or** `phi4-mini` |
| Idle | `ornith:9b` or `qwen2.5-coder` |
| Stopped | Ornith-35B MoE (with `--n-cpu-moe` style offload) |

**Useful free pulls (not all installed)**

```text
llama3.2  llama3.1:8b  qwen2.5:7b  qwen2.5:14b  mistral  mixtral  phi3
codellama  openhermes  gemma2
```

**Local APIs (no key)**

```bash
# Chat
curl http://localhost:11434/api/chat -d "{\"model\":\"qwen2.5-coder:latest\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}"

# CLI helpers
python ComfyUI\tools\local_ai_assistant.py chat --prompt "..."
python ComfyUI\tools\local_ai_assistant.py converse
python ComfyUI\tools\local_ai_assistant.py review --file PATH
python ComfyUI\tools\local_ai_assistant.py browse --url URL --prompt Q
```

**Alt local serve:** LM Studio `http://localhost:1234` (optional OpenAI-compatible).

---

## 2 · OpenRouter free models (approved cloud)

**Endpoint:** `https://openrouter.ai/api/v1/chat/completions`  
**Key:** `OPENROUTER_API_KEY` in env (never commit)  
**Canonical operator list:** `ComfyUI\config\openrouter_free_models.txt`  
**Broader catalog:** `ComfyUI\config\OPENROUTER_ALL_FREE_MODELS.txt`  
**API notes:** `ComfyUI\config\FREE_MODELS_API_ACCESS.md`  
**Refresh:** `python ComfyUI\tools\music_video_studio.py list-free-models`

### 2.1 Operator text→text free IDs (16 — brainstorm-safe)

```text
google/gemma-4-26b-a4b-it:free
google/gemma-4-31b-it:free
qwen/qwen3-next-80b-a3b-instruct:free
meta-llama/llama-3.3-70b-instruct:free
meta-llama/llama-3.2-3b-instruct:free
nvidia/nemotron-nano-9b-v2:free
liquid/lfm-2.5-1.2b-instruct:free
openai/gpt-oss-120b:free
openai/gpt-oss-20b:free
nousresearch/hermes-3-llama-3.1-405b:free
nvidia/nemotron-3-super-120b-a12b:free
cognitivecomputations/dolphin-mistral-24b-venice-edition:free
cohere/north-mini-code:free
liquid/lfm-2.5-1.2b-thinking:free
qwen/qwen3-coder:free
tencent/hy3:free
```

### 2.2 Additional / specialized free-tier IDs (live catalog)

Also seen free in July 2026 snapshots (specialized or heavier — verify live):

| ID | Notes |
|----|--------|
| `google/lyria-3-clip-preview` / `lyria-3-pro-preview` | Audio + video gen |
| `nvidia/nemotron-3-nano-30b-a3b:free` | Heavy nano |
| `nvidia/nemotron-3-nano-omni-…:free` | Multimodal |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | Very heavy MoE |
| `nvidia/nemotron-3.5-content-safety:free` | Classification |
| `nvidia/nemotron-nano-12b-v2-vl:free` | Vision + video |
| `poolside/laguna-m.1:free` / `laguna-xs-2.1:free` | Agentic defaults |
| `qwen/qwen3-coder-480b-a35b:free` | Massive coder |
| `openrouter/free` | Catch-all routing (ambiguous) |
| `openrouter/fusion` | Multi-model panel (budget routing) |

### 2.3 Quick-switch keys (`ComfyUI\tools\free_model_switch.bat`)

| Key | Model |
|-----|--------|
| `creative` | `google/gemma-4-26b-a4b-it:free` |
| `balanced` | `meta-llama/llama-3.3-70b-instruct:free` |
| `qwen3` | `qwen/qwen3-next-80b-a3b-instruct:free` |
| `fast` | `meta-llama/llama-3.2-3b-instruct:free` |
| `coding` | `qwen/qwen3-coder:free` (cloud) / `qwen2.5-coder` (Ollama) |
| `reasoning` | `tencent/hy3:free` / Ollama `deepseek-r1:8b` |
| `heavy` | Hermes-3 405B free class |
| `ornith35` / `ornith9` | Local Ornith GGUF |

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"google/gemma-4-26b-a4b-it:free\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"
```

---

## 3 · Other free-tier cloud APIs (optional keys)

Per policy, **route cloud chat via OpenRouter first**. These are free-tier backups / specialized:

| Provider | Free models / notes | Key env (if used) |
|----------|---------------------|-------------------|
| **DeepSeek direct** | `deepseek-chat`, `deepseek-coder`, `deepseek-reasoner` | `DEEPSEEK_API_KEY` |
| **Groq** | `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, Mixtral class | `GROQ_API_KEY` |
| **Google AI** | Gemini Flash / Gemma free tier | `GEMINI_API_KEY` / `GOOGLE_API_KEY` |
| **Hugging Face** | Inference free quota; pull GGUFs for Ollama | `HF_TOKEN` |
| **Cerebras** | High free token weekly (tier) | provider key |
| **Together / Fireworks** | Limited free credits | provider key |
| **xAI** | Free credits / Grok API when available | `XAI_API_KEY` |

**Hermes free stack docs:** `HERMES_FREE_SETUP_DOCUMENTATION.md` · `~/.hermes/*FREE*`

---

## 4 · Free local tools & services (ports)

| Service | Port | Cost | Start |
|---------|------|------|-------|
| Ollama | 11434 | Free | auto / `ollama serve` |
| OpenClaw gateway | 18789 | Free OSS | `LAUNCH_OPENCLAW_PEERS.bat` → [1] |
| ComfyUI | 8188 | Free OSS | `ComfyUI\launch_music_video_studio.bat` |
| Archon main / MCP / agents / UI | 8181 / 8051 / 8052 / 3737 | Free local | `START_ARCHON_STACK.bat` |
| AI Army | 8001 | Free | `python AI_ARMY\server.py` |
| AI Agency | 8010 | Free | `AI_AGENCY\launch_ai_agency.bat` |
| n8n | 5678 | Free self-host | docker / agency stack |
| Portal War Room | 3199 | Free | `OPEN_PORTAL_WAR_ROOM.bat` |
| LM Studio | 1234 | Free app | optional |
| Drive RAG | SQLite file | Free | `TOOLS\drive_backup_rag\` |

---

## 5 · Free voice stack

| Tool | Cost | Invoke |
|------|------|--------|
| Voice AI Assistant | Free | `TOOLS\VOICE_AI_ASSISTANT.bat` · `python TOOLS\voice_ai_assistant.py --loop --mic` |
| Omni Voice | Free | `TOOLS\OMNI_VOICE_ASSISTANT.bat` |
| Voice PA audit | Free | `python ai_voice_pa.py --source mic:10 --run` |
| edge-tts neural | Free (no key) | `tts_engine=edge` in config |
| Hermes voice | Free | `TOOLS\HERMES_VOICE.bat` |
| Whisper (Music Studio) | Free local | `ComfyUI\launch_music_video_studio.bat` → transcribe |
| n8n voice webhook | Free self-host | `voice_command_workflow.json` |

---

## 6 · Free browser + computer use

| Capability | Method | Invoke |
|------------|--------|--------|
| Browse + summarize | Headless Chromium + Ollama | `local_ai_assistant.py browse` |
| Multi-step agent | Playwright + Ollama | `agency_cli.py browse --goal …` |
| HTTP research | Fetch + Ollama | `agency_cli.py skill web_research` |
| Auto social upload | Browser-Use | `ComfyUI\tools\auto_poster.py` |
| Screenshot / describe | pyautogui + vision model | Omni / Voice AI |
| Open apps | Local PA | `omni_voice_assistant.py --text "open chrome"` |
| Workspace files only | Rule #8 | personal folders fenced |
| OpenClaw browser | Gateway tools | `openclaw agent --message "…"` |
| Pi terminal agent | Free OSS CLI | `pi` |
| Sunshine + Moonlight | Free remote desktop | `SUNSHINE_MOONLIGHT_SETUP.md` |

---

## 7 · Free RAG / knowledge

| Layer | Tech | Cost | Command |
|-------|------|------|---------|
| **Drive / workspace RAG** | SQLite FTS5 + optional `nomic-embed-text` | Free | `LAUNCH_DRIVE_BACKUP_RAG.bat` |
| **Drive backup (mirror)** | folder_mirror / zip / desktop / rclone | Free | `drive_backup_rag.py backup` |
| **Archon** | Supabase pgvector + MCP | Free self-host | `START_ARCHON_STACK.bat` · `archon:perform_rag_query` |
| **Plans index** | 698+ plans | Free | `python TOOLS\free_local_registry.py` search plans |
| **Code examples** | Archon MCP | Free | `archon:search_code_examples` |

---

## 8 · Free research — YouTube · social · GitHub · awesome lists

### YouTube / media (free)

| Tool | Role |
|------|------|
| **yt-dlp** | Download / extract (modern JS runtime for 2026 YT) |
| **youtube_transcript_api** / SLEEP_CASH | Captions harvest |
| **Whisper** via Music Video Studio | MP3 → lyrics TXT+SRT |
| **librosa** analyze-audio | BPM, beats, spectral |
| **ComfyUI** | Image/video gen (local models) |
| **Faceless shorts factory** | `SLEEP_TRIPLE\opt_b_faceless_shorts.py` |
| Docs | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` · `AWESOME_YOUTUBE_REPOS_2026.md` |

### GitHub / discovery (free)

| Tool | Role |
|------|------|
| `CLONE_ALL_GITHUB_REPOS.bat` | Bulk clone |
| GitHub public API | No key for public read (rate limits); PAT for higher limits |
| Plans search | free_local_registry / voice |

### Awesome lists (free catalogs)

| List | URL / path |
|------|------------|
| Awesome YouTube repos | `AWESOME_YOUTUBE_REPOS_2026.md` |
| awesome-web-agents | https://github.com/steel-dev/awesome-web-agents |
| awesome-ai-agents-2026 | https://github.com/ARUNAGIRINATHAN-K/awesome-ai-agents-2026 |
| trycua/acu (computer use) | https://github.com/trycua/acu |
| awesome-agents | https://github.com/kyrolabs/awesome-agents |
| awesome-video | https://github.com/sitkevij/awesome-video |
| awesome-selfhosted | https://github.com/awesome-selfhosted/awesome-selfhosted |
| awesome-openclaw-skills | https://github.com/VoltAgent/awesome-openclaw-skills |
| ClawHub | https://clawhub.ai |

---

## 9 · Free agent frameworks & peers (installed / PATH)

| Peer | Role | Launch |
|------|------|--------|
| **OpenClaw** | Channels + browser + skills gateway | `openclaw gateway` · `LAUNCH_OPENCLAW_PEERS.bat` |
| **Pi** | Minimal terminal coder | `pi` |
| **Hermes** | Self-improving free chat | Hermes / free model switch |
| **OpenCode / Kilo** | Coding CLIs | `opencode` · `kilo` |
| **Agent Zero** | Multi-tool agent UI | `agent-zero` |
| **Oracle / Jarvis / Paperclip** | Personas | `START-ALL-AI-TOOLS.bat` 8–10 |
| **AI Agency** | Virtual IT team + 10 skills | `:8010` |
| **AI Army / Footclan** | Mass dispatch | `:8001` · `FOOTCLAN_EXECUTOR.py` |
| **Grok skills / subagents** | document-this, explore, plan, language pros… | this TUI |
| **Pinokio** | 1-click AI apps | Pinokio app |
| **Browser-Use** | Web agent library | auto_poster / CLI |

Full map: `OPENCLAW_PI_AND_PEERS.md`

---

## 10 · Free skills (Agency · Grok · registry)

### Agency skills (Ollama, $0)

`web_research` · `deploy_check` · `code_audit` · `prospect_scan` · `content_draft` · `social_calendar` · `campaign_brief` · `competitor_marketing` · `seo_copy` · `email_sequence`

```bat
python TOOLS\free_local_registry.py --skills
python AI_AGENCY\tools\agency_cli.py skill deploy_check
```

### free_local_registry capability groups (71 total)

`voice` · `browser` · `computer` · `revenue` · `local_ai` · `plans` · `knowledge` · `skills` · `drive_rag` · `openclaw_peers` · `agents` · `grok_skills`

### Grok skills (examples)

`document-this` · `check-work` · `review` · `diagnose` · `design` · `execute-plan` · `docx` · `pptx` · `xlsx` · vercel-* · web-design-guidelines · pinokio · gepeto

### MCP free tools (Archon)

`archon:perform_rag_query` · `archon:search_code_examples` · `archon:manage_project` · `archon:manage_task` · `archon:get_available_sources`

---

## 11 · Free media / creative tooling

| Tool | Free use |
|------|----------|
| **ComfyUI** | Local gen; workflow recipes for 8 GB VRAM |
| **Music Video Studio** | transcribe, BPM, brainstorm (OpenRouter free), wizard |
| **edge-tts** | Narration without API key |
| **Whisper** | Local speech-to-text |
| **BLIP** (studio) | Video frame captioning |
| **FFmpeg** (system) | Mux/cut/encode (install if missing) |
| Workflow recipes | `ComfyUI\workflow_templates\workflow_recipes.md` |

---

## 12 · Free automation & overnight factories

| Tool | Notes |
|------|-------|
| n8n self-host | Workflows + voice webhook |
| SLEEP_TRIPLE opt_a–e | Digital products, shorts, crypto observe, alerts, POD |
| War room doctor | `python war_room.py health` |
| free_local_registry | Capability map CLI |
| Task scheduler | `install_monitor_scheduler.bat --dry-run` |

---

## 13 · Free dashboards (HTML / local)

| File | Content |
|------|---------|
| `WAR_ROOM_CONTROL_DASHBOARD.html` | Full command + **Free Resources** tab |
| `PORTAL_WAR_ROOM.html` | Live service probes |
| `AI_TOOLS_DASHBOARD.html` | Coding assistants + local models |
| `AI_AND_IT_TOOLKIT.html` | Operator toolkit |
| `UNIFIED_MASTER_DASHBOARD.html` | Empire + recovery + phone |
| `MASTER_ALL_DASHBOARD.html` | Top hub |
| `AUSAI_OPS_DASHBOARD.html` | Ops KPIs |

---

## 14 · Canonical files (source of truth)

| Path | Role |
|------|------|
| `FREE_RESOURCES_MASTER.md` | **This catalog** |
| `FREE_RESOURCES_REGISTRY.json` | Machine-readable inventory |
| `OPEN_FREE_RESOURCES.bat` | Open catalog + War Room free tab |
| `ComfyUI\config\openrouter_free_models.txt` | Operator OpenRouter free IDs |
| `ComfyUI\config\OPENROUTER_ALL_FREE_MODELS.txt` | Broader free list |
| `ComfyUI\config\FREE_MODELS_API_ACCESS.md` | API examples |
| `ComfyUI\tools\free_model_switch.bat` | Quick model switch |
| `TOOLS\free_local_registry.py` | 71 free capabilities |
| `TOOLS\FREE_LOCAL_HUB.bat` | Free hub menu |
| `TOOLS\FREE_LOCAL_SYSTEM_INDEX.md` | Free hub index |
| `HERMES_FREE_SETUP_DOCUMENTATION.md` | Hermes free stack |
| `WAR_ROOM_CONTROL.md` | War room runbook |
| `DRIVE_BACKUP_RAG.md` | Free backup + RAG |
| `OPENCLAW_PI_AND_PEERS.md` | Peer agents |
| Lean Drive mirror | `BACKUPS\GOOGLE_DRIVE_MIRROR` (includes this catalog) |
| Drive RAG SQLite | `BACKUPS\drive_rag\drive_rag.sqlite` |

**Backup + RAG (proceed-all 2026-07-16):** Free Resources are on the lean `backup_include` list. After `folder_mirror --run` + `ingest --collection workspace|drive --run`, FTS queries like `free openrouter models` hit this catalog in both workspace and drive collections.

---

## 15 · Not free / excluded from “pure free hub”

- Stripe / Gumroad / paid marketplaces (revenue; need keys)
- Direct OpenAI / Anthropic keys (**forbidden** — use OpenRouter)
- Some browser-use cloud agents if billed
- Paid Firecrawl / Serper / Tavily when free quota exhausted  
  → Prefer Ollama + Playwright + HTTP fetch first

---

## 16 · Daily free-first recipe

1. `ollama list` — local models up  
2. `TOOLS\FREE_LOCAL_HUB.bat` or voice loop for hands  
3. Heavy cloud job → OpenRouter `:free` via `free_model_switch.bat`  
4. Knowledge → Drive RAG query or Archon when stack is up  
5. Research → yt-dlp / awesome lists / Agency `web_research`  
6. Overnight → SLEEP_TRIPLE dry-run first, then `--run`  
7. Document → `/document-this` skill  

---

*Append-only catalog. Snapshot date: 2026-07-16. Free cloud IDs drift — re-run `list-free-models` before trusting a new ID.*
