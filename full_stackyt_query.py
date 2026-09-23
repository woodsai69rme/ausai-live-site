#!/usr/bin/env python3
"""Read-only query CLI for the Full Stack YouTube research package."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "full_stackyt_tool_catalog.json"
PACK_PATH = ROOT / "FULL_STACKYT_EXECUTION_PACK.json"


def load_data() -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    videos = catalog.get("videos", [])
    tools = catalog.get("tools", [])
    records_list = pack.get("records", [])
    if len(videos) != catalog.get("coverage", {}).get("verified_metadata_entries"):
        raise ValueError("catalog video count does not match coverage metadata")
    if len({row.get("url") for row in videos}) != len(videos) or any(not row.get("url", "").startswith("https://www.youtube.com/watch?v=") for row in videos):
        raise ValueError("catalog contains duplicate or non-canonical video URLs")
    if len(tools) != len(catalog.get("adoption_matrix", [])) or len(records_list) != len(tools):
        raise ValueError("catalog and execution-pack item counts are inconsistent")
    if {row.get("name") for row in tools} != {row.get("tool_name") for row in records_list}:
        raise ValueError("catalog and execution-pack item names are inconsistent")
    expected_safety = {
        "auto_install": False,
        "auto_execute": False,
        "credential_changes": False,
        "external_account_actions": False,
        "production_changes": False,
        "media_downloads": False,
    }
    if pack.get("safety_invariants") != expected_safety:
        raise ValueError("package safety invariants are not all disabled")
    if any(row.get("status") != "Backlog" for row in records_list):
        raise ValueError("execution pack contains a non-Backlog record")
    if any(row.get("bounded_next_action", {}).get("allow_auto_install") or row.get("bounded_next_action", {}).get("allow_auto_execute") for row in records_list):
        raise ValueError("execution pack contains an automatic action")
    official_count = sum(bool(row.get("source_evidence", {}).get("official_source_url")) for row in records_list)
    license_count = sum(bool(row.get("source_evidence", {}).get("license_verified")) for row in records_list)
    if pack.get("counts", {}).get("official_sources_verified") != official_count or pack.get("counts", {}).get("official_urls_included") != official_count:
        raise ValueError("execution-pack official-source counts are inconsistent")
    if pack.get("counts", {}).get("license_verified") != license_count:
        raise ValueError("execution-pack license counts are inconsistent")
    records = {row["tool_name"]: row for row in records_list}
    if len(records) != len(records_list):
        raise ValueError("execution pack contains duplicate tool names")
    return catalog, pack, records


def package_snapshot_id(catalog: dict[str, Any], pack: dict[str, Any]) -> str:
    """Return a deterministic ID for the saved catalog/execution-pack pair."""
    # Hash the complete validated inputs, not only a summary of names/timestamps.
    # A classification, evidence, license, description, or policy change must
    # produce a new identity even when video IDs and record names are unchanged.
    payload = {"catalog": catalog, "execution_pack": pack}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def freshness_metadata(catalog: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Calculate honest saved-snapshot freshness from the catalog UTC timestamp."""
    refresh = catalog.get("refresh", {})
    captured = refresh.get("refreshed_at_utc")
    result: dict[str, Any] = {
        "captured_at_utc": captured,
        "state": "unknown",
        "age_seconds": None,
        "stale_after_days": 30,
        "source": "full_stackyt_tool_catalog.json",
    }
    if not isinstance(captured, str) or not captured:
        return result
    try:
        parsed = datetime.fromisoformat(captured.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        age = (current - parsed.astimezone(timezone.utc)).total_seconds()
    except (TypeError, ValueError):
        return result
    result["age_seconds"] = round(age, 3)
    if age < 0:
        result["state"] = "future-dated"
    elif age <= 7 * 86400:
        result["state"] = "current"
    elif age <= 30 * 86400:
        result["state"] = "aging"
    else:
        result["state"] = "stale"
    return result


# --- Stale-data policy -----------------------------------------------------

STALE_POLICY_DEFAULT = {
    "stale_after_days": 30,
    "stale_mode": "caveat",  # "caveat" or "fail-closed"
}


def stale_policy(catalog: dict[str, Any], *, stale_after_days: int | None = None, stale_mode: str | None = None) -> dict[str, Any]:
    """Return the configured stale-data policy for the saved snapshot."""
    days = stale_after_days if stale_after_days is not None else STALE_POLICY_DEFAULT["stale_after_days"]
    mode = stale_mode or STALE_POLICY_DEFAULT["stale_mode"]
    if mode not in {"caveat", "fail-closed"}:
        raise ValueError(f"unsupported stale mode: {mode!r}; use 'caveat' or 'fail-closed'")
    freshness = freshness_metadata(catalog)
    state = freshness.get("state", "unknown")
    is_stale = state == "stale"
    return {
        "stale_after_days": days,
        "mode": mode,
        "freshness_state": state,
        "is_stale": is_stale,
        "action": "refuse" if is_stale and mode == "fail-closed" else ("caveat" if is_stale else "ok"),
    }


def evidence_metadata(item: dict[str, Any]) -> dict[str, Any]:
    """Return explicit evidence-quality fields without changing catalog status."""
    return {
        "evidence_level": item.get("evidence_level", "unknown"),
        "evidence_basis": item.get("evidence_basis", "unknown"),
        "official_source_verified": bool(item.get("official_source_verified")),
        "verification_confidence": item.get("verification_confidence"),
        "license_verified": bool(item.get("license_verified")),
        "license_claim": item.get("license_claim"),
        "status": item.get("status"),
        "status_is_approval": False,
        "local_workspace_evidence": item.get("local_workspace_evidence"),
        "evidence_owner": item.get("evidence_owner"),
        "review_date": item.get("review_date"),
        "aliases": item.get("aliases", []),
        "maintenance_observed_at": item.get("maintenance_observed_at"),
    }


def build_items(catalog: dict[str, Any], records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    videos_by_position = {row["position"]: row for row in catalog.get("videos", [])}
    items: list[dict[str, Any]] = []
    for tool in catalog.get("tools", []):
        name = tool["name"]
        record = records.get(name, {})
        source = record.get("source_evidence", {})
        context = record.get("context", {})
        action = record.get("bounded_next_action", {})
        related_videos = [
            {
                "position": position,
                "title": videos_by_position[position].get("title"),
                "url": videos_by_position[position].get("url"),
                "video_id": videos_by_position[position].get("video_id"),
            }
            for position in tool.get("video_positions", [])
            if position in videos_by_position
        ]
        items.append({
            "name": name,
            "category": tool.get("category"),
            "what_it_does": tool.get("what_it_does"),
            "evidence_basis": tool.get("evidence_basis"),
            "video_count": tool.get("video_count", len(related_videos)),
            "video_positions": tool.get("video_positions", []),
            "related_videos": related_videos,
            "evidence_level": tool.get("evidence_level", source.get("evidence_status", "unknown")),
            "workspace_fit": context.get("workspace_fit", tool.get("workspace_fit")),
            "risk": context.get("risk", tool.get("risk")),
            "tier": context.get("tier"),
            "status": record.get("status", tool.get("status", "unknown")),
            "official_source_verified": bool(source.get("official_source_url")),
            "official_source_url": source.get("official_source_url"),
            "source_type": source.get("source_type"),
            "verification_confidence": source.get("verification_confidence"),
            "license": source.get("license"),
            "license_verified": bool(source.get("license_verified")),
            "license_claim": source.get("license_claim"),
            "local_workspace_evidence": source.get("local_workspace_evidence"),
            "evidence_owner": source.get("evidence_owner"),
            "review_date": source.get("review_date"),
            "aliases": source.get("aliases", []),
            "maintenance_observed_at": source.get("maintenance_observed_at"),
            "evidence_metadata": evidence_metadata({
                "evidence_level": tool.get("evidence_level", source.get("evidence_status", "unknown")),
                "evidence_basis": tool.get("evidence_basis"),
                "official_source_verified": bool(source.get("official_source_url")),
                "verification_confidence": source.get("verification_confidence"),
                "license_verified": bool(source.get("license_verified")),
                "license_claim": source.get("license_claim"),
                "status": record.get("status", tool.get("status", "unknown")),
                "local_workspace_evidence": source.get("local_workspace_evidence"),
                "evidence_owner": source.get("evidence_owner"),
                "review_date": source.get("review_date"),
                "aliases": source.get("aliases", []),
                "maintenance_observed_at": source.get("maintenance_observed_at"),
            }),
            "requires_threat_model": bool(action.get("requires_threat_model")),
            "next_safe_action": action.get("action_type", tool.get("evaluation_action")),
            "manual_steps": action.get("manual_steps", []),
            "limitations": [
                "Channel mention is discovery evidence only.",
                "Source verification does not prove safety, compatibility, maintenance, or adoption.",
                "No catalog item is installed or executed by this package.",
            ],
            "source_files": ["full_stackyt_tool_catalog.json", "FULL_STACKYT_EXECUTION_PACK.json"],
        })
    return items


def matches(item: dict[str, Any], args: argparse.Namespace) -> bool:
    haystack = " ".join(str(item.get(key, "")) for key in ("name", "category", "what_it_does", "tier", "risk", "workspace_fit"))
    if args.query and args.query.lower() not in haystack.lower():
        return False
    for attr in ("category", "risk", "fit", "tier", "status", "evidence"):
        expected = getattr(args, attr)
        if expected:
            key = "workspace_fit" if attr == "fit" else ("evidence_level" if attr == "evidence" else attr)
            if str(item.get(key, "")).lower() != expected.lower():
                return False
    if args.source != "all" and (item["official_source_verified"] != (args.source == "verified")):
        return False
    if args.license != "all" and (item["license_verified"] != (args.license == "verified")):
        return False
    if args.video_position is not None and args.video_position not in item["video_positions"]:
        return False
    return True


def summary(items: list[dict[str, Any]], catalog: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    def counts(key: str) -> dict[str, int]:
        output: dict[str, int] = {}
        for item in items:
            value = str(item.get(key, "unknown"))
            output[value] = output.get(value, 0) + 1
        return dict(sorted(output.items()))
    return {
        "matched_items": len(items),
        "catalog_videos": len(catalog.get("videos", [])),
        "catalog_items": len(catalog.get("tools", [])),
        "execution_records": len(pack.get("records", [])),
        "tiers": counts("tier"),
        "risks": counts("risk"),
        "workspace_fit": counts("workspace_fit"),
        "evidence": counts("evidence_level"),
        "verified_sources": sum(item["official_source_verified"] for item in items),
        "verified_licenses": sum(item["license_verified"] for item in items),
        "freshness": freshness_metadata(catalog),
        "snapshot_id": package_snapshot_id(catalog, pack),
        "evidence_policy": catalog.get("evidence_policy"),
    }


def compare_matrix(items: list[dict[str, Any]], names: list[str]) -> dict[str, Any]:
    """Build a read-only comparison matrix for 3+ named items.

    Returns a deterministic matrix of catalog classifications. It does not
    perform benchmarks or prove safety, compatibility, or adoption.
    """
    lowered = [str(n).casefold().strip() for n in names]
    selected = []
    for item in items:
        item_name = str(item.get("name", "")).casefold()
        if item_name in lowered:
            selected.append(item)
    if len(selected) != len(names):
        found = {str(i.get("name", "")).casefold() for i in selected}
        missing = [n for n in lowered if n not in found]
        raise ValueError(f"could not resolve all names; missing: {missing}")
    # Order by the order names were given
    name_order = {n.casefold(): i for i, n in enumerate(names)}
    selected.sort(key=lambda i: name_order.get(str(i.get("name", "")).casefold(), 999))
    columns = ("category", "workspace_fit", "risk", "tier", "evidence_level", "official_source_verified", "license_verified", "status")
    matrix = {"headers": ["name", *columns], "rows": []}
    for item in selected:
        row = {"name": item.get("name")}
        for col in columns:
            row[col] = item.get(col)
        matrix["rows"].append(row)
    return {
        "schema_version": "1.0",
        "intent": "compare-matrix",
        "mode": "read-only",
        "matrix": matrix,
        "not_proven": [
            "Matrix classifications are catalog labels, not benchmark results.",
            "No implementation, security, compatibility, maintenance, or adoption comparison was performed.",
        ],
        "safety": {
            "read_only": True,
            "catalog_execution": False,
            "external_actions": False,
        },
    }


def print_item(item: dict[str, Any], explain: bool = False) -> None:
    source = item["official_source_url"] or "unverified"
    license_state = item["license"] if item["license_verified"] else (item["license_claim"] or "unverified")
    print(f"{item['name']} | {item['category']} | {item['tier']} | risk={item['risk']} | fit={item['workspace_fit']} | {item['evidence_level']}")
    print(f"  What: {item['what_it_does']}")
    print(f"  Source: {source} ({item['verification_confidence'] or 'not corroborated'})")
    print(f"  License: {license_state}")
    print(f"  Next safe action: {item['next_safe_action']}")
    print(f"  Status: {item['status']}")
    if item["related_videos"]:
        for video in item["related_videos"]:
            print(f"  Video {video['position']}: {video['title']} — {video['url']}")
    if explain:
        print("  Limitations:")
        for limitation in item["limitations"]:
            print(f"    - {limitation}")
        if item["manual_steps"]:
            print("  Manual steps:")
            for step in item["manual_steps"]:
                print(f"    - {step}")
        print(f"  Evidence files: {', '.join(item['source_files'])}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="case-insensitive search across name, category, description, tier, risk, and fit")
    parser.add_argument("--category")
    parser.add_argument("--risk")
    parser.add_argument("--fit")
    parser.add_argument("--tier")
    parser.add_argument("--status")
    parser.add_argument("--evidence")
    parser.add_argument("--source", choices=("all", "verified", "unverified"), default="all")
    parser.add_argument("--license", choices=("all", "verified", "unverified"), default="all")
    parser.add_argument("--video-position", type=int)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--explain", action="store_true")
    parser.add_argument("--summary", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    # Keep redirected CLI output portable on Windows and POSIX shells.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        catalog, pack, records = load_data()
        items = [item for item in build_items(catalog, records) if matches(item, args)]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"full_stackyt query: unable to read validated package data: {exc}", file=sys.stderr)
        return 2
    if args.limit >= 0 and not args.summary:
        items = items[: args.limit]
    if args.as_json:
        payload = summary(items, catalog, pack) if args.summary else {"query": vars(args), "results": items}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.summary:
        print(json.dumps(summary(items, catalog, pack), ensure_ascii=False, indent=2))
        return 0
    if not items:
        print("No Full Stack catalog items matched.")
        return 1
    for index, item in enumerate(items):
        if index:
            print()
        print_item(item, explain=args.explain)
    print(f"\nMatched {len(items)} item(s). Read-only; no catalog tool was installed or executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
