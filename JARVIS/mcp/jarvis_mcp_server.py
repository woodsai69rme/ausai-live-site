#!/usr/bin/env python3
"""
JARVIS Model Context Protocol (MCP) Server.
Exposes JARVIS capabilities as standardized tools to Claude Code, Cursor, Windsurf, and Antigravity:
• jarvis_click_ui: Visual grounding & Set-of-Marks UI element clicking
• jarvis_create_invoice: Voice/text note to publication-ready PDF & HTML invoice
• jarvis_tars_proposal: Automated 3-tier enterprise client proposal generator
• jarvis_spark_explode: 1-Click viral 15+ asset content explosion engine
• jarvis_memory_query: Hybrid SQLite persistent memory search
• jarvis_speak: Neural voice speech synthesis (Kokoro/SAPI)
• jarvis_status: Real-time system telemetry & port watchdog
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
sys.path.insert(0, str(JARVIS_DIR / "core"))

from jarvis_arrow import show_ai_arrow_by_query
from jarvis_employees import SPARKEmployee, TARSEmployee
from jarvis_gateway import EmpireGateway
from jarvis_invoice import JarvisInvoiceEngine
from jarvis_kokoro import get_neural_voice
from jarvis_memory import get_memory
from jarvis_som import get_som


TOOLS = [
    {
        "name": "jarvis_click_ui",
        "description": "Locate and point an AI Arrow at or click any button/menu on the user's screen using visual Set-of-Marks grounding.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_description": {"type": "string", "description": "Description of the UI element to locate (e.g. 'Submit button', 'Settings gear')"},
                "mode": {"type": "string", "enum": ["guide", "takeover"], "default": "guide", "description": "Whether to visually point at or click the element"}
            },
            "required": ["target_description"]
        }
    },
    {
        "name": "jarvis_create_invoice",
        "description": "Generate a publication-ready PDF and HTML invoice from natural language prompt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Invoice details (e.g. 'Bill Wayne Enterprises $4,500 for Autonomous AI Setup due in 14 days')"}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "jarvis_tars_proposal",
        "description": "Use TARS AI Employee to compile a 3-tier customized client proposal with pricing, deliverables, and SOW.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Name of the prospect/client"},
                "service_scope": {"type": "string", "description": "Description of services (e.g. 'Autonomous Computer-Use & Social Media AI Swarm')"}
            },
            "required": ["client_name", "service_scope"]
        }
    },
    {
        "name": "jarvis_spark_explode",
        "description": "Use SPARK AI Employee to explode 1 core topic into 15+ multi-platform assets (LinkedIn, X, YouTube scripts, Meta Ads).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Core topic or announcement to explode"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "jarvis_memory_query",
        "description": "Search JARVIS Mem0 persistent SQLite long-term memory for past facts, client details, and preferences.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "jarvis_speak",
        "description": "Speak text aloud through JARVIS neural voice synthesis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to synthesize aloud"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "jarvis_status",
        "description": "Get real-time operational status across all JARVIS subsystems and Empire ports (3142, 6970, 8000, 8088).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if name == "jarvis_click_ui":
            desc = arguments.get("target_description", "")
            mode = arguments.get("mode", "guide")
            show_ai_arrow_by_query(desc, mode=mode)
            return {"status": "SUCCESS", "message": f"AI Arrow dispatched for '{desc}' (mode: {mode})"}

        elif name == "jarvis_create_invoice":
            prompt = arguments.get("prompt", "")
            inv = JarvisInvoiceEngine()
            res = inv.process_voice_note_to_invoice(prompt)
            return {"status": "SUCCESS", "invoice": res}

        elif name == "jarvis_tars_proposal":
            client = arguments.get("client_name", "")
            scope = arguments.get("service_scope", "")
            tars = TARSEmployee()
            res = tars.generate_proposal(client, scope)
            return {"status": "SUCCESS", "proposal": res}

        elif name == "jarvis_spark_explode":
            topic = arguments.get("topic", "")
            spark = SPARKEmployee()
            out_file = spark.explode_content(topic)
            return {"status": "SUCCESS", "file": str(out_file), "content": out_file.read_text(encoding="utf-8")}

        elif name == "jarvis_memory_query":
            q = arguments.get("query", "")
            mem = get_memory()
            res = mem.search_memories(q)
            return {"status": "SUCCESS", "memories": res}

        elif name == "jarvis_speak":
            txt = arguments.get("text", "")
            voice = get_neural_voice()
            voice.speak(txt)
            return {"status": "SUCCESS", "spoken": txt}

        elif name == "jarvis_status":
            gw = EmpireGateway()
            services = gw.audit_all_services(verbose=False)
            return {"status": "ONLINE", "system": "JARVIS Autonomous Copilot v2.2", "services": services}

        else:
            return {"status": "ERROR", "message": f"Unknown tool: {name}"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def run_stdio_server():
    """Run JSON-RPC MCP server over standard I/O."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            req = json.loads(line.strip())
            req_id = req.get("id")
            method = req.get("method")

            if method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                res = handle_tool_call(name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    }
                }
            elif method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "jarvis-mcp-server", "version": "2.2.0"}
                    }
                }
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("[+] Testing JARVIS MCP Tools...")
        status_res = handle_tool_call("jarvis_status", {})
        print(f"Status Result: {status_res}")
        print(f"Tools Registered: {len(TOOLS)}")
        print("[✓] MCP Server Ready for Stdio JSON-RPC.")
    else:
        run_stdio_server()
