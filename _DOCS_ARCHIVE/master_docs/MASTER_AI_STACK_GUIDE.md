# 🚀 Ultimate 200GB-Compatible AI Stack: Master Guide

This document serves as the definitive reference for your local AI ecosystem. The stack is designed to provide high-performance reasoning, coding, uncensored chat, and creative media generation within a ~73GB footprint.

## 🏛️ System Architecture

- **LLM Engine:** Ollama (Port 11434)
- **Image/Video UI:** ComfyUI
- **Audio Engine:** Whisper.cpp & Audiocraft (Python)
- **Intelligence Bridge:** EmpireOS (Port 3142)

---

## 🧠 1. Language Models (Ollama)

Access these via `ollama run <model_name>` or via the API.

| Model | Size | Primary Use Case |
| :--- | :--- | :--- |
| **Qwen-2.5-7B** | 4.5 GB | Daily general chat and fast reasoning. |
| **Qwen-2.5-14B** | 9.0 GB | Enhanced reasoning (uses system RAM offload). |
| **Qwen-2.5-32B** | 20 GB | Complex logic, math, and difficult coding tasks. |
| **Qwen-2.5-Coder-7B** | 4.5 GB | Ultra-fast code autocomplete and small refactors. |
| **DeepSeek-Coder-V2-Lite**| 9.5 GB | Advanced multi-file refactoring and architectural code. |
| **Dolphin-Qwen-2.5-7B** | 4.5 GB | Uncensored chat (no moralizing or refusals). |
| **Hermes-2-Pro-Llama-3** | 4.5 GB | Agent function calling and tool use (n8n/Autogen). |
| **LLaVA-1.6-7B** | 4.5 GB | Vision: Analyzing screenshots, UI layouts, and charts. |
| **Nomic-Embed-Text** | 0.3 GB | Vector embeddings for local RAG and memory systems. |

---

## 🎨 2. Image & Video Generation (ComfyUI)

Models are located in `C:\Users\karma\ComfyUI\models\checkpoints`.

- **SDXL Turbo:** High-speed 1-step latent diffusion for real-time prototyping.
- **Juggernaut XL v9:** Industry-standard for photorealism and cinematic quality.
- **AnimateDiff SD1.5:** Specialized for creating lightweight video loops and animations.
  - *Custom Node:* `ComfyUI-AnimateDiff-Evolved` is installed for timeline control.

---

## 🎵 3. Audio & Voice

- **Whisper.cpp (Medium):** High-accuracy speech-to-text.
  - *Path:* `C:\Users\karma\whisper.cpp\models\ggml-medium.bin`
- **MusicGen-Small:** Text-to-audio background music generation.
  - *Engine:* Installed via `audiocraft` Python library.

---

## 📂 4. Critical Path Mapping

| Content | Target Directory |
| :--- | :--- |
| **LLM Binary Store** | Managed by `%USERPROFILE%\.ollama` |
| **ComfyUI Checkpoints** | `C:\Users\karma\ComfyUI\models\checkpoints` |
| **Manual GGUF Files** | `C:\Users\karma\downloads` |
| **Whisper Models** | `C:\Users\karma\whisper.cpp\models` |
| **EmpireOS Integration**| `C:\Users\karma\EmpireOS` |

---

## 🛠️ 5. Maintenance & Monitoring

- **Check Downloads:** Use `ollama list` to verify model availability.
- **Disk Usage:** Total model size is ~73GB. System currently has ~259GB free.
- **Scripts:**
  - `C:\Users\karma\install_stack.py`: The master automation script.
  - `START_GOD_MODE.bat`: Launches the unified dashboard.

---

*Documentation generated on 30 April 2026 for Karma System Administration.*
