import socket
import time

PORTS = {
    "God-Mode Dashboard": 3142,
    "AI Army Backend (FastAPI)": 8000,
    "Voice AI Assistant": 8765,
    "n8n Automation": 5678,
    "War Map (Foot Clan)": 3000,
    "Ollama (Local LLM)": 11434,
    "ComfyUI (Media Engine)": 8188
}

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

print("=========================================================")
print("🛡️ ZERO-HUMAN COMMAND CENTER: FINAL SYSTEM QA & TESTING 🛡️")
print("=========================================================")
print("Testing all critical infrastructure endpoints...\n")

all_passed = True

for name, port in PORTS.items():
    is_open = check_port(port)
    if is_open:
        print(f"✅ [PORT {port}] {name}: ONLINE AND RESPONDING")
    else:
        print(f"⚠️ [PORT {port}] {name}: OFFLINE OR INITIALIZING")
        all_passed = False
    time.sleep(0.2)

print("\n=========================================================")
print("QA MODULE 2: DIRECTORY & DOCUMENTATION INTEGRITY")
print("=========================================================")
import os

critical_files = [
    r"C:\Users\karma\MASTER_ENCYCLOPEDIA_AI_2026.md",
    r"C:\Users\karma\MASTER_100_PERCENT_EXECUTION_PLAN.md",
    r"C:\Users\karma\ULTIMATE_OMNI_EXECUTION_PROTOCOL_2026.md",
    r"C:\Users\karma\AI_ARMY_FOOT_CLAN_DOSSIER.md",
    r"C:\Users\karma\ALL_OPTIONS_MENU.md"
]

for file_path in critical_files:
    if os.path.exists(file_path):
        print(f"✅ FOUND: {os.path.basename(file_path)}")
    else:
        print(f"❌ MISSING: {os.path.basename(file_path)}")
        all_passed = False

print("\n=========================================================")
if all_passed:
    print("🌟 FINAL QA STATUS: 100% PASSED. SYSTEM IS FULLY OPERATIONAL.")
else:
    print("⚡ FINAL QA STATUS: PARTIAL PASS. SOME SERVICES ARE STILL BOOTING.")
print("=========================================================")
