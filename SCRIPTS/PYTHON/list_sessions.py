#!/usr/bin/env python3
"""
List all Augment sessions with metadata
"""
import os
import json
from datetime import datetime

sessions_dir = os.path.expanduser('~/.augment/sessions')
if not os.path.exists(sessions_dir):
    print(f"Sessions directory not found: {sessions_dir}")
    exit(1)

print("AUGMENT SESSIONS")
print("=" * 80)
print(f"{'Session ID':<38} {'Created':<25} {'Modified':<25} {'First Message':<50}")
print("=" * 80)

session_files = sorted([f for f in os.listdir(sessions_dir) if f.endswith('.json')])

for session_file in session_files:
    session_path = os.path.join(sessions_dir, session_file)
    try:
        with open(session_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session_id = data.get('sessionId', 'Unknown')
        created = data.get('created', 'Unknown')
        modified = data.get('modified', 'Unknown')
        
        # Get first message preview
        first_message = ""
        if 'chatHistory' in data and len(data['chatHistory']) > 0:
            first_exchange = data['chatHistory'][0]
            if 'exchange' in first_exchange:
                req_msg = first_exchange['exchange'].get('request_message', '')
                if req_msg:
                    first_message = req_msg[:50] + "..." if len(req_msg) > 50 else req_msg
                else:
                    first_message = "(empty request)"
        
        print(f"{session_id:<38} {created:<25} {modified:<25} {first_message:<50}")
        
    except Exception as e:
        print(f"Error reading {session_file}: {e}")

print("\n" + "=" * 80)
print(f"Total sessions: {len(session_files)}")
print("\nTo reload a session, use its session ID in Augment.")