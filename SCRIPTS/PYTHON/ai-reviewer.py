import os
import subprocess
import json
import argparse
import sys
import requests
from typing import Optional

# Configuration
DEFAULT_MODEL = "openrouter/free"
REPOMIX_OUTPUT = "repomix-output.xml"

class AIReviewer:
    def __init__(self, directory: str, api_key: str, model: str = DEFAULT_MODEL):
        self.directory = os.path.abspath(directory)
        self.api_key = api_key
        self.model = model

    def check_requirements(self):
        """Check if npx is available."""
        npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
        try:
            subprocess.run([npx_cmd, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: 'npx' (Node.js) is not installed or not in PATH.")
            sys.exit(1)

    def bundle_codebase(self) -> str:
        """Run repomix to pack the codebase."""
        print(f"[*] Packing codebase in {self.directory}...")
        
        npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
        cmd = [
            npx_cmd, "-y", "repomix", 
            self.directory,
            "--output", REPOMIX_OUTPUT,
            "--include", "**/*.md,**/*.txt,**/*.json,**/*.js,**/*.py,**/*.ts,**/*.html,**/*.css",
            "--compress"
        ]
        
        try:
            # Run in the target directory to respect .gitignore
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            output_path = os.path.join(os.getcwd(), REPOMIX_OUTPUT)
            if not os.path.exists(output_path):
                # Try relative to the script directory if it wasn't in CWD
                output_path = REPOMIX_OUTPUT
                
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Clean up temporary file
            os.remove(output_path)
            return content
            
        except subprocess.CalledProcessError as e:
            print(f"Error running Repomix: {e.stderr if e.stderr else e.stdout}")
            sys.exit(1)

    def get_analysis(self, content: str):
        """Send content to OpenRouter for deep analysis."""
        print(f"[*] Sending to {self.model} (Deep Understanding mode)...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/coleam00/archon", # Site name for OpenRouter rankings
            "X-Title": "Archon AI Document Reviewer"
        }
        
        system_prompt = (
            "You are a Senior Architect and Document Analyst. Your task is to deeply read and understand "
            "the provided codebase/documents. Do not just search for keywords. Understand the context, "
            "architecture, purpose, and logic of the project. "
            "\n\nProvide a comprehensive summary covering:"
            "\n1. Overall Project Purpose & Objective"
            "\n2. Key Architectural Components & Logic"
            "\n3. Significant Documentation Review (what is described vs what is implemented)"
            "\n4. Critical Insights or Issues found during the deep dive."
        )
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the project context:\n\n{content}\n\nPlease perform a deep-dive review."}
            ],
            "stream": True
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                stream=True
            )
            response.raise_for_status()
            
            print("\n" + "="*50)
            print("DEEP ANALYSIS REPORT")
            print("="*50 + "\n")
            
            full_content = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        json_str = decoded_line[6:]
                        if json_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(json_str)
                            content_chunk = chunk['choices'][0]['delta'].get('content', '')
                            print(content_chunk, end='', flush=True)
                            full_content += content_chunk
                        except json.JSONDecodeError:
                            continue
            print("\n\n" + "="*50)
            return full_content
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AI Document Reviewer - Deep Codebase Understanding")
    parser.get_default("directory")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to review (default: current)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenRouter model to use (default: {DEFAULT_MODEL})")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)
        
    reviewer = AIReviewer(args.directory, api_key, args.model)
    reviewer.check_requirements()
    
    content = reviewer.bundle_codebase()
    reviewer.get_analysis(content)

if __name__ == "__main__":
    main()
