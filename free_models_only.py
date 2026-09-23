#!/usr/bin/env python3
"""Free AI Models Only - Complete selection of 100% free models + cloud APIs."""
import sys
import json
from pathlib import Path

# ============================================================
# OPENROUTER FREE MODELS (35 models, unified API) - LIVE
# ============================================================
FREE_OPENROUTER = [
    # (model_id, ctx_k, modalities, best_for, provider)
    ("google/gemma-4-26b-a4b-it:free", 256, ["image","text","video"], "Best multimodal reasoning (256K) [Google]", "Google"),
    ("google/gemma-4-31b-it:free", 256, ["image","text","video"], "Largest free Gemma (256K, dense) [Google]", "Google"),
    ("stealth/ox-alpha", 1024, ["text","image","video"], "Best free coding/agentic (1M ctx) [Stealth]", "Stealth"),
    ("minimax/minimax-m3:free", 1024, ["text","image","video"], "MiniMax M3 multimodal (1M ctx) [MiniMax]", "MiniMax"),
    ("thinkingmachines/inkling:free", 1024, ["text","image","audio"], "Inkling multimodal (1M ctx) [Thinking Machines]", "Thinking Machines"),
    ("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", 256, ["text","audio","image","video"], "Multimodal CoT + extraction (256K) [NVIDIA]", "NVIDIA"),
    ("deepseek/deepseek-v4.1-flash:free", 1000, ["text","image"], "DeepSeek V4.1 Flash - Vision+tools (1M) [DeepSeek]", "DeepSeek"),
    ("z-ai/glm-5.3-flash:free", 1000, ["text","image","video"], "GLM 5.3 Flash - Vision+tools+thinking (1M) [Z.ai]", "Z.ai"),
    ("qwen/qwen3.5:free", 256, ["text","image","video"], "Qwen3.5 multimodal family (256K) [Qwen]", "Qwen"),
    ("qwen/qwen3.6:free", 256, ["text","image"], "Qwen3.6 vision + tools (256K) [Qwen]", "Qwen"),
    ("google/gemma-4-12b-it:free", 256, ["image","text","video"], "Gemma 4 12B multimodal (256K) [Google]", "Google"),
    ("meta-llama/llama-4-maverick:free", 256, ["text","image"], "Llama 4 Maverick MoE - Vision (256K) [Meta]", "Meta"),
    ("nvidia/nemotron-3-nano-12b-v2-vl:free", 128, ["text","image","video"], "Nemotron Nano 12B VL - Video understanding [NVIDIA]", "NVIDIA"),
    ("minimax/minimax-m2.7:free", 196, ["text"], "MiniMax M2.7 (196K ctx) [MiniMax]", "MiniMax"),
    ("liquid/lfm-2.5-2.6b:free", 65, ["text"], "Tiny fast model (65K ctx) [Liquid AI]", "Liquid AI"),
    # NEW: Additional vision/agent models
    ("inclusionai/ling-3.0-flash-vl:free", 256, ["text","image","video"], "InclusionAI Ling 3.0 Flash VL", "InclusionAI"),
    ("inclusionai/ling-3.0-flash-sante:free", 256, ["text"], "InclusionAI Ling 3.0 Flash Sante (medical) [InclusionAI]", "InclusionAI"),
    ("inclusionai/ling-3.0-flash-fin:free", 256, ["text"], "InclusionAI Ling 3.0 Flash Fin (financial) [InclusionAI]", "InclusionAI"),
    ("nex-agi/nex-n2.5-mini:free", 256, ["text","image"], "Nex AGI N2.5 Mini [Nex AGI]", "Nex AGI"),
    ("nex-agi/nex-n2.5-pro:free", 256, ["text","image"], "Nex AGI N2.5 Pro [Nex AGI]", "Nex AGI"),
    ("stealth/union-alpha", 256, ["text","image"], "Stealth Union Alpha [Stealth]", "Stealth"),
    ("openrouter/free", 1000, ["text","image","video"], "Auto-router selects best free model per request [OpenRouter]", "OpenRouter"),
]

# ============================================================
# LOCAL MODELS (Ollama - 100% Free, Private, Offline)
# ============================================================
FREE_LOCAL_KNOWN = [
    # (model_id, size_gb, vram_4bit_gb, ctx_k, description, install)
    ("ornith:9b", 35, 6, 256, "Daily coding driver (Ornith 1.0 9B, 69.4% SWE)", "ollama run ornith"),
    ("minicpm-v:latest", 5.5, 5.5, 32, "Vision (7.6B, image understanding) [GPT-4o level]", "ollama run minicpm-v"),
    ("moondream:latest", 1.7, 1.7, 2, "Tiny vision (1B, Phi2+CLIP) [Fastest small]", "ollama run moondream"),
    ("qwen3.5:9b", 6.6, 6.6, 256, "Multimodal coding/vision (9.7B, tools) [Best local]", "ollama run qwen3.5:9b"),
    ("nvidia/nemotron-nano-12b-v2-vl:free", 12, 8, 128, "Video understanding [NVIDIA VL]", "ollama run nemotron-nano-12b-v2-vl"),
    ("moondream2:latest", 1.8, 1.8, 2, "Improved Moondream (1.8B)", "ollama run moondream2"),
    ("qwen2.5-vl:7b", 5, 5, 32, "Qwen2.5 Vision-Large (7B, SOTA benchmarks)", "ollama run qwen2.5-vl:7b"),
    ("glm-4v:9b", 6, 6, 32, "GLM-4V - Native multimodal tools + OCR", "ollama run glm-4v"),
    ("glm-4.6v:106b", 65, 65, 1000, "GLM-4.6V - Vision, OCR, tool use [Native]", "ollama run glm-4.6v"),
    ("internvl3.5:8b", 5, 5, 32, "InternVL 3.5 - Scalable dense vision [Apache 2.0]", "ollama run internvl3.5"),
    ("idefics2:8b", 5.5, 5.5, 32, "Vision, OCR, docs [Mistral+SigLIP]", "ollama run idefics2"),
    ("smolvlm2:2.2b", 2.2, 2.2, 8, "Tiny video models [Efficient]", "ollama run smolvlm2"),
    ("molmo2:4b", 3, 3, 32, "Video, pointing, tracking [Interactive vision]", "ollama run molmo2"),
    ("deepseek-janus-pro:7b", 5, 5, 32, "Understanding + generation [Unified multimodal]", "ollama run deepseek-janus-pro"),
    ("step3-vl-10b:free", 10, 6.5, 32, "Vision, Apache 2.0 license [Open]", "ollama run step3-vl-10b"),
    ("paddleocr-vl-1.6:free", 7, 5, 32, "Document parsing [Specialized OCR]", "ollama run paddleocr-vl-1.6"),
]

# ============================================================
# OTHER FREE PROVIDERS
# ============================================================
FREE_PROVIDERS = {
    "OpenRouter": {
        "url": "https://openrouter.ai",
        "limit": "Unlimited free models",
        "models": [m[0] for m in FREE_OPENROUTER[:10]],
    },
    "Groq": {
        "url": "https://console.groq.com/keys",
        "limit": "14,400 req/day",
        "models": [
            ("llama-3.1-70b-versatile", "General reasoning, best quality"),
            ("llama-3.1-8b-instant", "Fastest general purpose"),
            ("mixtral-8x7b-32768", "MoE general"),
            ("gemma2-9b-it", "Fast Gemma 2"),
        ],
    },
    "Together AI": {
        "url": "https://api.together.xyz/settings/api-keys",
        "limit": "$1 credit (~10M tokens)",
        "models": [
            ("llama-3.1-70b-versatile", "Coding, open models"),
            ("qwen2.5-coder-32b", "Code generation"),
            ("deepseek-v3", "General reasoning"),
        ],
    },
    "Cerebras": {
        "url": "https://www.cerebras.net/free-tier",
        "limit": "Generous free tier",
        "models": [
            ("llama-3.1-70b", "Ultra-fast (2000+ tok/s)"),
            ("llama-3.1-8b", "Fast inference"),
        ],
    },
    "Google AI Studio": {
        "url": "https://aistudio.google.com",
        "limit": "Free tier with API key",
        "models": [
            ("gemini-1.5-flash", "Fastest multimodal"),
            ("gemini-1.5-pro", "Best quality multimodal"),
        ],
    },
}

# ============================================================
# TASK-BASED MODEL SELECTION
# ============================================================
MODEL_PICKER = {
    "coding": [
        "ornith:9b",
        "qwen3.5:9b",
        "meta-llama/llama-4-maverick:free",
        "openrouter/free",
    ],
    "vision": [
        "minicpm-v:latest",
        "qwen2.5-vl:7b",
        "google/gemma-4-26b-a4b-it:free",
        "openrouter/free",
    ],
    "video": [
        "minimax/minimax-m3:free",
        "openrouter/free",
        "stealth/ox-alpha",
    ],
    "reasoning": [
        "openrouter/free",
        "ornith:9b",
        "qwen3.5:9b",
        "meta-llama/llama-4-maverick:free",
    ],
    "fast": [
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "moondream:latest",
        "z-ai/glm-5.3-flash:free",
    ],
    "audio": [
        "openrouter/free",
        "faster-whisper",
        "localai",
    ],
    "embedding": [
        "nomic-embed-text:latest",
        "mxbai-embed-large:latest",
        "openrouter/free",
    ],
    "multimodal": [
        "openrouter/free",
        "qwen2.5-vl:7b",
        "google/gemma-4-26b-a4b-it:free",
    ],
}

def get_model_for_task(task):
    """Get recommended models for a given task."""
    return MODEL_PICKER.get(task, ["openrouter/free"])

def list_openrouter():
    """List all OpenRouter free models."""
    return FREE_OPENROUTER

def list_local():
    """List known local Ollama models."""
    return FREE_LOCAL_KNOWN

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = sys.argv[1]
        models = get_model_for_task(task)
        print(f"🎯 Best FREE models for '{task}':")
        for m in models:
            if m in [o[0] for o in FREE_OPENROUTER]:
                model_info = [o for o in FREE_OPENROUTER if o[0] == m][0]
                print(f"  OPENROUTER: {m} - {model_info[2]} - {model_info[3]} [{model_info[4]}]")
                print(f"    → model: {m}")
            elif m in [l[0] for l in FREE_LOCAL_KNOWN]:
                model_info = [l for l in FREE_LOCAL_KNOWN if l[0] == m][0]
                print(f"  LOCAL: {m} - {model_info[2]}GB VRAM, {model_info[3]}ctx - {model_info[4]}")
                print(f"    → ollama run {m}")
            else:
                print(f"  {m}")
    else:
        print("""
========================================================================
  FREE AI MODELS ONLY - Complete Free Selection (100% Free, Zero Paid)
========================================================================

Usage: python free_models_only.py <task>

Tasks: coding, vision, video, reasoning, fast, audio, embedding, multimodal

Providers:
  • OpenRouter: 35 free models, 1 API key, up to 1M context, multimodal
  • Local (Ollama): 17 free models, run via `ollama run <model>`
  • Other: Groq (14K req/day), Together AI, Cerebras, Google AI Studio

========================================================================
        """)
        print(f"📦 OpenRouter free models: {len(FREE_OPENROUTER)}")
        print(f"📦 Local known models: {len(FREE_LOCAL_KNOWN)}")
        for t, models in MODEL_PICKER.items():
            print(f"  {t}: {', '.join(models[:3])} ...")