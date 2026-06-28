import requests

token = "REDACTED_ghp_TOKENatYC9WFVSHXZ3CihjZsSRL"
repo_name = "DevMonitor-Widget"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "name": repo_name,
    "public": True,
    "description": "DevMonitor Widget - AI Army Integration"
}

try:
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repository {repo_name} created successfully!")
        print(f"Clone URL: {response.json().get('clone_url')}")
    elif response.status_code == 422:
        print(f"Repository {repo_name} already exists.")
        # Optionally get the clone_url if it exists
        response = requests.get(f"https://api.github.com/user/repos", headers=headers)
        if response.status_code == 200:
            repos = response.json()
            for repo in repos:
                if repo['name'] == repo_name:
                    print(f"Clone URL: {repo.get('clone_url')}")
                    break
    else:
        print(f"Failed to create repository. Status: {response.status_code}, Response: {response.text}")
except Exception as e:
    print(f"Error creating repository: {e}")
