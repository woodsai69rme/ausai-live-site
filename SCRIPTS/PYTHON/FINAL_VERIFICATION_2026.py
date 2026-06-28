import asyncio
import httpx
import json
import socket
import sys
from datetime import datetime

async def check_port(port, name):
    print(f"Checking {name} (Port {port})...", end=" ", flush=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    if result == 0:
        print("✅ ONLINE")
        return True
    else:
        print("❌ OFFLINE")
        return False

async def verify_system():
    print("\n" + "="*50)
    print("   ROGUE-SUN UNIFIED COMMAND: FINAL VERIFICATION   ")
    print("="*50 + "\n")

    HEADERS = {"Authorization": "Bearer army-master-key-2026"}

    # 1. Port Checks
    services = [
        (8000, "J.A.R.V.I.S. Orchestrator"),
        (8889, "EmpireOS Telemetry"),
    ]
    
    online = []
    for port, name in services:
        online.append(await check_port(port, name))
    
    if not all(online):
        print("\n⚠️  Critical infrastructure is missing. Attempting deep query anyway...")

    async with httpx.AsyncClient() as client:
        # 2. Query Orchestrator for Registered Agents
        print("\n[FLEET STATUS]")
        try:
            resp = await client.get("http://localhost:8000/agents", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                # Handle both {agents: []} and [{}, {}] formats
                agents = data.get("agents", []) if isinstance(data, dict) else data
                print(f"✅ Found {len(agents)} active agents registered.")
                for a in agents:
                    print(f"   - {a.get('id', 'unknown')} ({a.get('type', 'unknown')}): {a.get('status', 'unknown')}")
            else:
                print(f"❌ Failed to fetch agents: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ Error querying Orchestrator: {e}")

        # 3. Query Telemetry HUD
        print("\n[TELEMETRY HUD]")
        try:
            resp = await client.get("http://localhost:8889/stream", timeout=2.0)
            # We just want to see if it responds (SSE headers)
            if resp.status_code == 200 and 'text/event-stream' in resp.headers.get('content-type', ''):
                print("✅ SSE Telemetry Stream verified.")
            else:
                print(f"❌ Telemetry Stream invalid: {resp.status_code}")
        except Exception:
            # SSE might block or timeout on simple GET, checking root as fallback
            try:
                resp = await client.get("http://localhost:8889/")
                if resp.status_code == 200:
                    print("✅ Dashboard UI responding.")
            except Exception as e:
                print(f"❌ Telemetry HUD unreachable: {e}")

        # 4. End-to-End Task Execution Test
        print("\n[E2E TASK TEST]")
        test_task = {
            "agent_type": "system_001",
            "action": "report",
            "params": {"query": "Status check"}
        }
        try:
            # Using the v2 tasks endpoint
            resp = await client.post("http://localhost:8000/api/v2/tasks", json=test_task, headers=HEADERS)
            if resp.status_code in [200, 201, 202]:
                res_data = resp.json()
                print("✅ Task successfully queued in Orchestrator V2.")
                print(f"   Task ID: {res_data.get('id', 'unknown')}")
            else:
                print(f"❌ Task queuing failed: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ E2E Task Error: {e}")

    print("\n" + "="*50)
    print("   VERIFICATION CYCLE COMPLETE   ")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(verify_system())
