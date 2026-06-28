"""
Secure API Key Vault for Gemini System
Uses the OS credential manager (Windows Credential Manager) to store API keys securely.
Part of Option 7.1: Enhanced API Key Security.
"""

import keyring
import sys
import getpass

SERVICE_NAME = "GeminiSystemKeys"

def set_key(username: str, api_key: str):
    """
    Securely store an API key.
    
    Args:
        username (str): The identifier for the key (e.g., 'openrouter', 'github').
        api_key (str): The actual API key string.
    """
    try:
        keyring.set_password(SERVICE_NAME, username, api_key)
        print(f"✅ Successfully stored key for '{username}' in secure vault.")
        return True
    except Exception as e:
        print(f"❌ Failed to store key for '{username}': {e}")
        return False

def get_key(username: str) -> str:
    """
    Retrieve an API key securely.
    
    Args:
        username (str): The identifier for the key.
        
    Returns:
        str: The API key, or None if not found.
    """
    try:
        key = keyring.get_password(SERVICE_NAME, username)
        if key:
            return key
        else:
            print(f"⚠️  Key for '{username}' not found in vault.")
            return None
    except Exception as e:
        print(f"❌ Failed to retrieve key for '{username}': {e}")
        return None

def delete_key(username: str):
    """
    Remove an API key from the vault.
    
    Args:
        username (str): The identifier for the key.
    """
    try:
        keyring.delete_password(SERVICE_NAME, username)
        print(f"🗑️  Successfully deleted key for '{username}'.")
        return True
    except keyring.errors.PasswordDeleteError:
        print(f"⚠️  Key for '{username}' not found, nothing to delete.")
        return False
    except Exception as e:
        print(f"❌ Failed to delete key for '{username}': {e}")
        return False

def list_keys():
    """
    Note: Standard keyring API doesn't support listing keys for security reasons.
    We would need to maintain a separate index file if listing is required.
    For now, this just prints a message.
    """
    print("ℹ️  Keyring does not support listing keys directly.")
    print("   To verify a key exists, try retrieving it.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python api_vault.py [set|get|delete] [key_name]")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    
    if action == "set":
        if len(sys.argv) < 3:
            key_name = input("Enter key name (e.g. openrouter): ")
        else:
            key_name = sys.argv[2]
            
        secret = getpass.getpass(f"Enter API Key for '{key_name}': ")
        set_key(key_name, secret)
        
    elif action == "get":
        if len(sys.argv) < 3:
            key_name = input("Enter key name: ")
        else:
            key_name = sys.argv[2]
            
        key = get_key(key_name)
        if key:
            print(f"Key found: {key[:4]}...{key[-4:]}") # Show only start/end
            
    elif action == "delete":
        if len(sys.argv) < 3:
            key_name = input("Enter key name: ")
        else:
            key_name = sys.argv[2]
            
        delete_key(key_name)
        
    else:
        print(f"Unknown action: {action}")
