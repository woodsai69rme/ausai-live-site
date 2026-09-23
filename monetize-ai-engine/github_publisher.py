"""
GitHub Repository Creator & Code Publisher for AutoMonetize AI Studio
Creates remote repositories via GitHub REST API without requiring local Git CLI PATH installation.
"""

import os
import sys
import json
import base64
import requests

GITHUB_PAT = os.environ.get("GITHUB_TOKEN", "REDACTED_REDACTED_GHP_TOKENsZeWgkqAT-iYkNJSqO48PdSxjmeefMxWRFPXzCbfv7izJxbIdUMwfkf_Du-6NpG-6O4nwSMBo9sbpLBRDwPSuMdQduOD7qE=F02C5009")
GITHUB_API_URL = "https://api.github.com"

class GitHubPublisher:
    def __init__(self, token=GITHUB_PAT):
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_authenticated_user(self):
        res = requests.get(f"{GITHUB_API_URL}/user", headers=self.headers)
        if res.status_code == 200:
            return res.json()["login"]
        return None

    def create_repository(self, repo_name, description="AutoMonetize AI Studio App Package", private=False):
        user = self.get_authenticated_user()
        if not user:
            print("❌ Authentication failed. Check GITHUB_TOKEN.")
            return False

        print(f"👤 Authenticated as GitHub user: {user}")
        payload = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True
        }

        res = requests.post(f"{GITHUB_API_URL}/user/repos", headers=self.headers, json=payload)
        if res.status_code in [201, 422]:
            repo_url = f"https://github.com/{user}/{repo_name}"
            print(f"✅ Repository ready: {repo_url}")
            return {"user": user, "repo": repo_name, "url": repo_url}
        else:
            print(f"❌ Failed to create repo: {res.status_code} - {res.text}")
            return False

    def push_file(self, owner, repo, file_path, target_path_in_repo, commit_message="Add project file"):
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{target_path_in_repo}"
        
        with open(file_path, "rb") as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode("utf-8")

        # Check if file exists to get SHA
        get_res = requests.get(url, headers=self.headers)
        sha = get_res.json().get("sha") if get_res.status_code == 200 else None

        payload = {
            "message": commit_message,
            "content": encoded_content
        }
        if sha:
            payload["sha"] = sha

        res = requests.put(url, headers=self.headers, json=payload)
        return res.status_code in [200, 201]

if __name__ == "__main__":
    repo_name = sys.argv[1] if len(sys.argv) > 1 else "automonetize-ai-studio"
    pub = GitHubPublisher()
    result = pub.create_repository(repo_name)
    if result:
        print(f"🚀 Project repository published to: {result['url']}")
