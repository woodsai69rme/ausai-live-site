import requests
import base64
import os

token = "REDACTED_ghp_TOKENatYC9WFVSHXZ3CihjZsSRL"
repo_name = "DevMonitor-Widget"
owner = "woodsai69rme"
base_dir = r"C:\Users\karma\Desktop\DevMonitorWidget"

files_to_upload = [
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "DEVELOPER_GUIDE.md",
    "FEATURES.md",
    "QUICKSTART.md",
    "README.md",
    "USER_GUIDE.md",
    "assets/sounds/README.md",
    "docs/ARCHITECTURE.md",
    "docs/AUDIO_SYSTEM.md",
    "docs/market_research/CHAT_HISTORY_SUMMARY.md",
    "docs/market_research/DEEP_DIVE_STRATEGY.md",
    "docs/market_research/ENHANCEMENT_BACKLOG.md",
    "docs/market_research/MASTER_RECREATION_PROMPT_DEEP_DIVE.md",
    "docs/market_research/MONETIZATION_STRATEGY.md",
    "docs/market_research/PROJECT_AUDIT_FINAL.md",
    "docs/market_research/ULTIMATE_REGENESIS_PROMPT.md",
    "docs/market_research/generic_templates/GENERIC_ENHANCEMENT_BACKLOG.md",
    "docs/market_research/generic_templates/GENERIC_MARKETING_STRATEGY.md",
    "docs/market_research/generic_templates/GENERIC_MONETIZATION_STRATEGY.md",
    "docs/market_research/generic_templates/GENERIC_PROJECT_AUDIT.md",
    "docs/market_research/generic_templates/GENERIC_RECREATION_PROMPT.md",
    "future_roadmap.md",
    "plans/APPLICATION_RUN_REPORT.md",
    "plans/AUDIO_FREEZE_FIX_PLAN.md",
    "plans/COMPREHENSIVE_AUDIT_REPORT.md",
    "plans/TEST_REPORT.md",
    "walkthrough.md"
]

def upload_file(path):
    full_path = os.path.join(base_dir, path.replace("/", os.sep))
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return

    with open(full_path, "rb") as f:
        content = f.read()
    
    encoded_content = base64.b64encode(content).decode("utf-8")
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if file already exists to get its SHA
    sha = None
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha")
    
    data = {
        "message": f"Upload {path}",
        "content": encoded_content,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
        
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"Successfully uploaded: {path}")
    else:
        print(f"Failed to upload {path}: {response.status_code} - {response.text}")

# Ensure the main branch exists or create it
def ensure_main_branch():
    url = f"https://api.github.com/repos/{owner}/{repo_name}/branches/main"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        # Create an empty commit to initialize the repo if needed
        # Actually, just uploading a file will create the branch if it doesn't exist
        pass

for file_path in files_to_upload:
    upload_file(file_path)
