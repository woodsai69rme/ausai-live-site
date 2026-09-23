"""Invariant tests for fast_port_check DEFAULT_PORTS coverage."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "TOOLS"
sys.path.insert(0, str(TOOLS))

from fast_port_check import DEFAULT_PORTS, HUB_PORTS, check_ports, format_report  # noqa: E402


def test_default_ports_include_enhanced_services():
    assert 3199 in DEFAULT_PORTS
    assert 3737 in DEFAULT_PORTS
    assert 54321 in DEFAULT_PORTS
    assert DEFAULT_PORTS[3199] == "Portal War Room"
    assert DEFAULT_PORTS[3737] == "Archon UI"
    assert DEFAULT_PORTS[54321] == "Supabase local"


def test_check_ports_returns_triples():
    results = check_ports({3199: "Portal War Room"}, timeout=0.2)
    assert len(results) == 1
    name, port, online = results[0]
    assert name == "Portal War Room"
    assert port == 3199
    assert isinstance(online, bool)


def test_format_report_non_empty():
    report = format_report(check_ports({8181: "Archon Server"}, timeout=0.2))
    assert "Archon Server" in report
    assert ":8181" in report


def test_hub_ports_match_master_dashboard():
    assert len(HUB_PORTS) == 9
    assert HUB_PORTS[8765] == "DevMonitor telemetry"
    assert HUB_PORTS[17890] == "PasteGrab API"
    assert HUB_PORTS[3142] == "God Mode Next.js"