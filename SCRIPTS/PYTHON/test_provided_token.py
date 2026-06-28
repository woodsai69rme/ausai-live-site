import requests

token = "REDACTED_ghp_TOKENatYC9WFVSHXZ3CihjZsSRL"
headers = {"Authorization": f"token {token}"}
try:
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"Token is VALID! User: {user.get('login')}")
    else:
        print(f"Token is INVALID. Status: {response.status_code}, Response: {response.text}")
except Exception as e:
    print(f"Error testing token: {e}")
