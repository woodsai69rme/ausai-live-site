# Local AI Fleet — Development Environment

Welcome to the unified local-AI toolchain at `C:\Users\karma\`. This environment runs a **local-first, cloud-fallback** fleet of AI agents, coding tools, creative studios, and dashboards — all launchable from a single menu.

## Quick Start

1. **Launch the fleet menu:** Double-click `START-ALL-AI-TOOLS.bat`
2. **Read the master docs:** Open `ALL-TOOLS-CONFIGURED.md`
3. **Quick index:** See `ALL_TOOLS_QUICK_REFERENCE.md` for a one-page menu map

## Fleet Overview

| Layer | Tools | Status |
|-------|-------|--------|
| **Gateway** | OpenClaw (port 18789) | ✅ Active |
| **Autonomous Agents** | Hermes, Agent Zero, Oracle, Jarvis, Paperclip | 2 active, 1 cloned, 3 configs ready |
| **Coding Tools** | Kilo AI, OpenCode AI | ✅ Ready |
| **Local Models** | Ollama (qwen2.5-coder, phi3) | ✅ Ready |
| **Creative** | Tadpole Studio (music), ComfyUI (video/image) | ✅ Ready |
| **Dashboard** | God-Mode (port 3142) | ✅ Ready |

## Documentation

| Document | Purpose |
|----------|---------|
| [`ALL-TOOLS-CONFIGURED.md`](ALL-TOOLS-CONFIGURED.md) | **Master fleet docs** — configs, ports, models, troubleshooting |
| [`ALL_TOOLS_QUICK_REFERENCE.md`](ALL_TOOLS_QUICK_REFERENCE.md) | One-page index of all 16 launcher options |
| [`OPENCLAW_HERMES_SETUP_AND_RESEARCH.md`](OPENCLAW_HERMES_SETUP_AND_RESEARCH.md) | OpenClaw gateway + Hermes agent deep dive |
| [`ORACLE_JARVIS_PAPERCLIP_SETUP.md`](ORACLE_JARVIS_PAPERCLIP_SETUP.md) | Oracle / Jarvis / Paperclip setup + schemas |
| [`TODO_TRACKER.md`](TODO_TRACKER.md) | Append-only project tracker |

## Security

- No hardcoded API keys in configs — only public model identifiers.
- Git history scrubbed for PATs and secrets.
- Personal folders protected (Rule #8) — never touched by automation.
- Audit logs are append-only and isolated per persona.

## Requirements

- Git, Python 3.12+, `uv`, Node.js 20+, Ollama
- OpenRouter API key (for cloud fallback; optional if running local-only)
- Optional: CUDA for ComfyUI GPU acceleration

## Contributing

1. Follow secure coding practices.
2. Never commit secrets — use environment variables.
3. Update `ALL-TOOLS-CONFIGURED.md` when adding new tools or agents.
4. Run `gitleaks detect --source . --verbose` before committing.