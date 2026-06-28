import os
import subprocess
import requests
import sys

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path):
        print(f"File already exists: {target_path}")
        return
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded: {target_path}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def run_command(command):
    print(f"Running: {command}")
    try:
        # Use shell=True and utf-8 encoding to avoid capture issues
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(f"Success: {result.stdout}")
    except Exception as e:
        print(f"Command failed: {e}")

# 1. Ollama Models
ollama_models = [
    "qwen2.5-coder",
    "deepseek-coder-v2",
    "llava",
    "hermes2-pro"
]
for model in ollama_models:
    run_command(f"ollama pull {model}")

# 2. Manual Downloads
downloads = [
    ("https://huggingface.co/bartowski/Dolphin-2.9.4-Qwen2.5-7B-GGUF/resolve/main/Dolphin-2.9.4-Qwen2.5-7B-Q4_K_M.gguf", 
     "C:/Users/karma/downloads/dolphin-2.9.4-qwen-2.5-7b-Q4_K_M.gguf"),
    ("https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors", 
     "C:/Users/karma/ComfyUI/models/checkpoints/sd_xl_turbo_1.0_fp16.safetensors"),
    ("https://huggingface.co/RunDiffusion/Juggernaut-XL-v9/resolve/main/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors", 
     "C:/Users/karma/ComfyUI/models/checkpoints/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"),
    ("https://huggingface.co/guoyww/AnimateDiff/resolve/main/mm_sd_v15_v2.ckpt", 
     "C:/Users/karma/ComfyUI/models/animatediff_models/mm_sd_v15_v2.ckpt"),
    ("https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin", 
     "C:/Users/karma/whisper.cpp/models/ggml-medium.bin")
]

for url, path in downloads:
    download_file(url, path)

# 3. Create Dolphin Modelfile and Model
modelfile_path = "C:/Users/karma/downloads/Modelfile"
modelfile_content = "FROM C:/Users/karma/downloads/dolphin-2.9.4-qwen-2.5-7b-Q4_K_M.gguf"
with open(modelfile_path, "w") as f:
    f.write(modelfile_content)
run_command(f"ollama create dolphin-qwen -f {modelfile_path}")

# 4. ComfyUI Nodes
custom_nodes_path = "C:/Users/karma/ComfyUI/custom_nodes"
if os.path.exists(custom_nodes_path):
    print("Installing ComfyUI AnimateDiff node...")
    run_command(f"cd /d {custom_nodes_path} && git clone --depth 1 https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git")

# 5. Audio Tools
print("Installing core audio libraries...")
run_command("pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --prefer-binary")
run_command("pip install openai-whisper audiocraft --prefer-binary")

print("Stack installation script completed.")
