import requests

token = "REDACTED_ghp_TOKENatYC9WFVSHXZ3CihjZsSRL"
repo_name = "DevMonitor-Widget"
owner = "woodsai69rme"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

try:
    # Check if main branch exists
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo_name}/branches/main", headers=headers)
    if response.status_code == 200:
        print("Branch 'main' exists.")
    else:
        print(f"Branch 'main' does not exist. Status: {response.status_code}")

    # Check for recent commits
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo_name}/commits", headers=headers)
    if response.status_code == 200:
        commits = response.json()
        print(f"Total commits: {len(commits)}")
        if len(commits) > 0:
            print(f"Latest commit: {commits[0]['commit']['message']}")
    else:
        print(f"Failed to fetch commits. Status: {response.status_code}")

except Exception as e:
    print(f"Error checking repository: {e}")
