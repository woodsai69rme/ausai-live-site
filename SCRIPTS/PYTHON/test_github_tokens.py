import requests

tokens = [
    "REDACTED_ghp_TOKENW1Duz2S7IMVPQ64t0K2lgtKA6e0wSZFsZeWgkqAT-iYkNJSqO48PdSxjmeefMxWRFPXzCbfv7izJxbIdUMwfkf_Du-6NpG-6O4nwSMBo9sbpLBRDwPSuMdQduOD7qE=F02C5009",
    "REDACTED_ghp_TOKENW1Duz2S7IMVPQ64t0K2lgtKA6e0wSZFsZeWgkqAT-iYkNJSqO48PdSxjmeefMxWRFPXzCbfv7izJxbIdUMwfkf_Du-6NpG-6O4nwSMBo9sbpLBRDwPSuMdQduOD7qE",
    "REDACTED_ghp_TOKENkT2tkYPYTWKG3SKFp9EzuL"
]

for i, token in enumerate(tokens):
    print(f"Testing token {i}...")
    headers = {"Authorization": f"token {token}"}
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"Token {i} is VALID! User: {user.get('login')}")
        else:
            print(f"Token {i} is INVALID. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error testing token {i}: {e}")
