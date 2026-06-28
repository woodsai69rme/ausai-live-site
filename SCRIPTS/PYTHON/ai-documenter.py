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

class AIDocumenter:
    def __init__(self, directory: str, api_key: str, model: str = DEFAULT_MODEL):
        self.directory = os.path.abspath(directory)
        self.api_key = api_key
        self.model = model

    def check_requirements(self):
        npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
        try:
            subprocess.run([npx_cmd, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: 'npx' (Node.js) is not installed or not in PATH.")
            sys.exit(1)

    def bundle_codebase(self) -> str:
        print(f"[*] Packing codebase in {self.directory} for Documentation...")
        
        npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
        cmd = [
            npx_cmd, "-y", "repomix", 
            self.directory,
            "--output", REPOMIX_OUTPUT,
            "--include", "**/*.md,**/*.txt,**/*.json,**/*.js,**/*.py,**/*.ts,**/*.html,**/*.css",
            "--compress"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            output_path = os.path.join(os.getcwd(), REPOMIX_OUTPUT)
            if not os.path.exists(output_path):
                output_path = REPOMIX_OUTPUT
                
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            os.remove(output_path)
            return content
            
        except subprocess.CalledProcessError as e:
            print(f"Error running Repomix: {e.stderr if e.stderr else e.stdout}")
            sys.exit(1)

    def write_readme(self, content: str):
        print(f"[*] Generating README using {self.model} ...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/coleam00/archon",
            "X-Title": "Archon AI Auto-Documenter"
        }
        
        system_prompt = (
            "You are a Senior Technical Writer and Architect. "
            "Write a pristine, professional README.md for the provided project context. "
            "It must include: 1. Project Title & Description, 2. Key Features, 3. Architecture/Tech Stack, 4. How it works. "
            "Output ONLY the raw markdown content without any ```markdown wrapping or conversational text. "
            "If there is an existing README, intelligently blend it with your newfound context to produce a superior version."
        )
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Project Layout & Context:\n\n{content}\n\nWrite the comprehensive README.md now."}
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
            
            readme_path = os.path.join(self.directory, 'README.md')
            print(f"\n[*] Writing directly to {readme_path} ...\n")
            
            # Since AI might output markdown block, we should clean it later, but we write it stream-style
            with open(readme_path, "w", encoding="utf-8") as f:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8', errors='replace')
                        if decoded_line.startswith("data: "):
                            json_str = decoded_line[6:]
                            if json_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(json_str)
                                content_chunk = chunk['choices'][0]['delta'].get('content', '')
                                # Print to terminal for logs
                                print(content_chunk, end='', flush=True)
                                # Write to actual file
                                f.write(content_chunk)
                                f.flush()
                            except json.JSONDecodeError:
                                continue
            
            # Post-process the file to remove markdown code blocks if the AI ignored the instruction
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    final_txt = f.read()
                
                if final_txt.startswith("```markdown"):
                    final_txt = final_txt.replace("```markdown\n", "", 1)
                    if final_txt.endswith("```\n") or final_txt.endswith("```"):
                        final_txt = final_txt[:-3] if final_txt.endswith("```") else final_txt[:-4]
                    
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(final_txt.strip())
            except Exception as inner_e:
                pass # Non-critical if post-processing fails

            print("\n\n[✓] README.md successfully generated and saved.")
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AI Documenter - Auto README Generator")
    parser.get_default("directory")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to document (default: current)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenRouter model to use (default: {DEFAULT_MODEL})")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)
        
    docgen = AIDocumenter(args.directory, api_key, args.model)
    docgen.check_requirements()
    
    content = docgen.bundle_codebase()
    docgen.write_readme(content)

if __name__ == "__main__":
    main()
