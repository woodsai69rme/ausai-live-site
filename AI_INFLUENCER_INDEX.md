# 🤳 AI_INFLUENCER_INDEX.md

> **Master index for the AI Influencer Factory — autonomous content engine.** Covers the factory runtime, config, shorts generator, and social media monitor. Uses Ollama (qwen2.5), Piper TTS, ComfyUI, and n8n to produce fully automated AI influencer content.

**Generated:** 2026-06-28
**Parent systems:** ComfyUI, n8n, Voice PA

---

## 📁 FILE INVENTORY (4 components)

### 🔷 Core Factory

| File | Purpose |
|---|---|
| `ai_influencer_factory.py` | Autonomous content engine: script generation → TTS → video → publish |
| `ai_influencer_config.json` | Influencer persona config, platform settings, schedule |

### 🔷 Sub-modules

| Directory | Purpose |
|---|---|
| `ai_shorts_generator/` | Shorts generator: docs, tests, src for short-form content |
| `ai_social_media_monitor/` | Social media monitoring and engagement tracking |

---

## 🏗️ CONTENT PIPELINE

```
ai_influencer_factory.py
     │
     ├──► Ollama (qwen2.5) ──► Script generation
     ├──► Piper TTS ──────────► Voice synthesis
     ├──► ComfyUI ────────────► Image/video generation
     ├──► n8n ────────────────► Publishing automation
     │
     └──► Output: C:\Users\karma\MEDIA\AI_Influencer
```

---

## 🎯 PLATFORM TARGETS

- YouTube Shorts / TikTok
- LinkedIn
- Facebook
- Instagram

---

## 🔒 SECURITY BOUNDARIES

- **Local-first:** All generation runs locally — no cloud API dependencies for content
- **Rule #8 fence:** Outputs to MEDIA/AI_Influencer, never personal folders
- **Credentials:** Config stored in `ai_influencer_config.json` (gitignored pattern)

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| ComfyUI | `ComfyUI/COMFYUI_SYSTEM_INDEX.md` |
| n8n Automation | `N8N_AUTOMATION_SYSTEM_INDEX.md` |
| Voice PA | `VOICE_PA_SYSTEM_INDEX.md` |
| Workspace Master | `WORKSPACE_INDEX.md` |

---

*Golden Rules: append, preserve, protect.*
