#!/usr/bin/env python3
"""Read-only Freebuff wrapper for the Full Stack catalog.

This module is the deterministic boundary described by
``FULL_STACKYT_FREEBUFF_INTEGRATION_SPEC.md``. It reads the same validated
catalog/execution-pack data as ``full_stackyt_query.py`` and never performs
network access, installation, execution, authentication, status mutation, or
external actions.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import full_stackyt_query as query

ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "1.0"
SKILL_NAME = "full_stackyt_freebuff"

_SIDE_EFFECT_PATTERNS = (
    r"\binstall\b",
    r"\bexecute\b",
    r"\b(?:run|launch)\b.{0,50}\b(?:tool|item|skill|plugin|mcp|agent|browser extension|catalog item)\b",
    r"\bload\b.{0,30}\b(skill|plugin|mcp|browser extension)\b",
    r"\b(?:change|update|mutate)\b.{0,20}\bstatus\b",
    r"\badopt\b",
    r"\bpublish\b",
    r"\bsend\b",
    r"\btrade\b",
    r"\bauthenticat(?:e|ion)\b",
    r"\bconnect\b.{0,30}\b(account|trading|bank|crm)\b",
    r"\b(cookie|cookies|credentials?|patient records?|production)\b",
)


def _safe_defaults(**overrides: Any) -> Namespace:
    values: dict[str, Any] = {
        "query": None,
        "category": None,
        "risk": None,
        "fit": None,
        "tier": None,
        "status": None,
        "evidence": None,
        "source": "all",
        "license": "all",
        "video_position": None,
    }
    values.update(overrides)
    return Namespace(**values)


def _base_response(question: str, *, status: str = "ok", intent: str = "search") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "skill": SKILL_NAME,
        "mode": "read-only",
        "status": status,
        "intent": intent,
        "question": question,
        "answer": "",
        "results": [],
        "explanation": {
            "evidence_state": None,
            "proven": [],
            "sources": [],
            "citations": [],
            "record_paths": [],
            "related_videos": [],
            "confidence": None,
            "ambiguity": [],
            "not_proven": [
                "Installation safety, compatibility, maintenance quality, and adoption approval are not proven by this catalog.",
            ],
            "next_safe_action": "Review the cited source and evidence before any separate, explicitly approved evaluation.",
        },
        "validation": {
            "catalog_loaded": False,
            "execution_pack_loaded": False,
            "catalog_videos": None,
            "catalog_items": None,
            "execution_records": None,
            "error": None,
            "freshness": None,
            "evidence_policy": None,
        },
        "safety": {
            "read_only": True,
            "network_access": False,
            "credentials_requested": False,
            "catalog_execution": False,
            "status_mutation": False,
            "external_actions": False,
        },
    }


def _iter_strings(value: Any):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _iter_strings(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            yield from _iter_strings(nested)
    elif isinstance(value, str):
        yield value


def _assert_public_safe(catalog: dict[str, Any], pack: dict[str, Any]) -> None:
    private_path = re.compile(r"(?<![A-Za-z])(?:[A-Za-z]:[\\\\/]|(?:^|[\\\\/])(?:Users|home|private|tmp)(?:[\\\\/]|$))", re.IGNORECASE)
    for label, payload in (("catalog", catalog), ("execution pack", pack)):
        for text in _iter_strings(payload):
            if private_path.search(text):
                raise ValueError(f"{label} contains a private/local path")

    for record in pack.get("records", []):
        source = record.get("source_evidence", {})
        action = record.get("bounded_next_action", {})
        if source.get("official_source_verified") != bool(source.get("official_source_url")):
            raise ValueError("execution-pack source verification is inconsistent")
        if action.get("allow_auto_install") or action.get("allow_auto_execute"):
            raise ValueError("execution-pack contains an automatic action")


def _load() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    catalog, pack, records = query.load_data()
    if catalog.get("schema_version") != SCHEMA_VERSION or pack.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("catalog or execution pack schema version is unsupported")
    _assert_public_safe(catalog, pack)

    # Keep provenance explicit: each result points to its immutable execution
    # record, while the shared query loader remains the source of validation.
    record_positions = {
        record.get("tool_name"): position
        for position, record in enumerate(pack.get("records", []))
    }
    items = query.build_items(catalog, records)
    for item in items:
        position = record_positions.get(item.get("name"))
        if position is None:
            raise ValueError(f"missing execution record for {item.get('name')!r}")
        item["execution_record_path"] = f"FULL_STACKYT_EXECUTION_PACK.json#/records/{position}"

    validation = {
        "catalog_loaded": True,
        "execution_pack_loaded": True,
        "catalog_videos": len(catalog.get("videos", [])),
        "catalog_items": len(catalog.get("tools", [])),
        "execution_records": len(pack.get("records", [])),
        "schema_version": SCHEMA_VERSION,
        "freshness": query.freshness_metadata(catalog),
        "snapshot_id": query.package_snapshot_id(catalog, pack),
        "evidence_policy": catalog.get("evidence_policy"),
        "error": None,
    }
    return catalog, pack, items, validation


def _attach_validation(response: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    response["validation"] = validation
    return response


def _item_explanation(items: list[dict[str, Any]], *, ambiguity: list[str] | None = None) -> dict[str, Any]:
    related: list[dict[str, Any]] = []
    for item in items:
        related.extend(item.get("related_videos", []))
    # Keep result payloads deterministic and avoid repeating the same related video.
    seen: set[tuple[Any, Any]] = set()
    unique_related = []
    for video in related:
        key = (video.get("video_id"), video.get("url"))
        if key not in seen:
            seen.add(key)
            unique_related.append(video)
    evidence = sorted({str(item.get("evidence_level") or "unknown") for item in items})
    sources = sorted({source for item in items for source in item.get("source_files", [])})
    record_paths = sorted({path for item in items for path in [item.get("execution_record_path")] if path})
    citations = [
        {
            "item": item.get("name"),
            "record_path": item.get("execution_record_path"),
            "source_files": item.get("source_files", []),
            "official_source_url": item.get("official_source_url"),
            "video_urls": [video.get("url") for video in item.get("related_videos", []) if video.get("url")],
        }
        for item in items
    ]
    next_actions = sorted({str(item.get("next_safe_action") or "review-source") for item in items})
    confidences = sorted({str(item.get("verification_confidence")) for item in items if item.get("verification_confidence")})
    proven = []
    for item in items:
        proven.append(f"The saved catalog describes {item.get('name')} as: {item.get('what_it_does')}")
        if item.get("official_source_verified"):
            proven.append(f"An official source URL is recorded for {item.get('name')}.")
    return {
        "evidence_state": evidence[0] if len(evidence) == 1 else evidence,
        "proven": proven,
        "sources": sources,
        "citations": citations,
        "record_paths": record_paths,
        "related_videos": unique_related,
        "confidence": confidences[0] if len(confidences) == 1 else (confidences or "conservative title/catalog evidence"),
        "ambiguity": ambiguity or [],
        "not_proven": [
            limitation
            for item in items
            for limitation in item.get("limitations", [])
        ] or ["No implementation, safety, compatibility, maintenance, or adoption claim is established by this catalog."],
        "next_safe_action": next_actions[0] if len(next_actions) == 1 else next_actions,
    }


def _explain_answer(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No matching Full Stack catalog item was found."
    if len(items) == 1:
        item = items[0]
        source = item.get("official_source_url") or "unverified"
        return (
            f"{item['name']} is cataloged as {item.get('category')} with "
            f"{item.get('workspace_fit')} workspace fit and {item.get('risk')} risk. "
            f"It is described as: {item.get('what_it_does')} "
            f"The channel evidence is {item.get('evidence_level')}; official source: {source}."
        )
    return f"{len(items)} Full Stack catalog items matched the read-only query."


def search(query_text: str | None = None, **filters: Any) -> dict[str, Any]:
    """Search the validated catalog and return an explainable response."""
    question = query_text or ""
    response = _base_response(question, intent="search")
    try:
        catalog, pack, items, validation = _load()
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        response["status"] = "unavailable"
        response["answer"] = "Catalog unavailable or stale; no answer was produced from partial data."
        response["validation"] = {**response["validation"], "error": str(exc)}
        return response

    args = _safe_defaults(query=query_text, **filters)
    matched = [item for item in items if query.matches(item, args)]
    response["results"] = matched
    response["answer"] = _explain_answer(matched)
    response["explanation"] = _item_explanation(matched)
    response["explanation"]["ambiguity"] = (
        [f"{len(matched)} items matched; narrow by exact name, category, tier, or risk."]
        if len(matched) > 1 else []
    )
    return _attach_validation(response, validation)


def _resolve_item(items: list[dict[str, Any]], name: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    lowered = str(name).casefold().strip()
    exact = [item for item in items if str(item.get("name", "")).casefold() == lowered]
    if exact:
        return exact[0], exact
    candidates = [item for item in items if lowered and lowered in str(item.get("name", "")).casefold()]
    return (candidates[0] if len(candidates) == 1 else None), candidates


def compare(name_a: str, name_b: str) -> dict[str, Any]:
    """Compare two exact catalog identities using only saved evidence."""
    question = f"Compare {name_a} and {name_b}"
    response = _base_response(question, intent="compare")
    try:
        _, _, items, validation = _load()
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        response["status"] = "unavailable"
        response["answer"] = "Catalog unavailable or stale; no comparison was produced from partial data."
        response["validation"]["error"] = str(exc)
        return response

    first, first_candidates = _resolve_item(items, name_a)
    second, second_candidates = _resolve_item(items, name_b)
    ambiguity: list[str] = []
    if first is None:
        ambiguity.append(f"Could not resolve {name_a!r} to one exact catalog item ({len(first_candidates)} candidates).")
    if second is None:
        ambiguity.append(f"Could not resolve {name_b!r} to one exact catalog item ({len(second_candidates)} candidates).")
    if ambiguity:
        response["status"] = "ambiguous"
        response["answer"] = "Comparison requires two unambiguous catalog item names."
        response["explanation"]["ambiguity"] = ambiguity
        return _attach_validation(response, validation)

    matched = [first, second]
    response["results"] = matched
    response["answer"] = (
        f"{first['name']} and {second['name']} are compared using saved catalog evidence. "
        "This comparison does not imply adoption or implementation equivalence."
    )
    explanation = _item_explanation(matched)
    explanation["ambiguity"] = []
    explanation["not_proven"] = list(dict.fromkeys(explanation["not_proven"] + [
        "Comparative fit, risk, and tier are catalog classifications, not benchmark results.",
        "No implementation, security, compatibility, maintenance, or adoption comparison was performed.",
    ]))
    response["explanation"] = explanation
    return _attach_validation(response, validation)


def explain(name: str) -> dict[str, Any]:
    """Explain one catalog item, matching its name case-insensitively."""
    response = _base_response(name, intent="explain")
    try:
        _, _, items, validation = _load()
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        response["status"] = "unavailable"
        response["answer"] = "Catalog unavailable or stale; no answer was produced from partial data."
        response["validation"]["error"] = str(exc)
        return response

    lowered = name.casefold().strip()
    exact = [item for item in items if str(item.get("name", "")).casefold() == lowered]
    candidates = exact or [item for item in items if lowered in str(item.get("name", "")).casefold()]
    if not candidates:
        response["status"] = "not_found"
        response["answer"] = f"No catalog item named {name!r} was found."
        response["explanation"]["ambiguity"] = ["The requested name is not present in the validated catalog."]
    else:
        response["results"] = candidates
        response["answer"] = _explain_answer(candidates)
        response["explanation"] = _item_explanation(
            candidates,
            ambiguity=([f"{len(candidates)} candidate items matched; exact identity is not unique."] if len(candidates) > 1 else []),
        )
    return _attach_validation(response, validation)


def summary() -> dict[str, Any]:
    """Return validated package counts with provenance and safety state."""
    response = _base_response("summary", intent="summary")
    try:
        catalog, pack, items, validation = _load()
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        response["status"] = "unavailable"
        response["answer"] = "Catalog unavailable or stale; no summary was produced from partial data."
        response["validation"]["error"] = str(exc)
        return response
    response["answer"] = (
        f"The validated Full Stack package contains {len(catalog.get('videos', []))} videos, "
        f"{len(items)} named items, and {len(pack.get('records', []))} execution records. "
        f"Snapshot freshness is {validation['freshness']['state']}."
    )
    response["results"] = [query.summary(items, catalog, pack)]
    response["explanation"] = {
        "evidence_state": "validated package counts",
        "proven": ["The counts are internally consistent with the validated local snapshot."],
        "sources": ["full_stackyt_tool_catalog.json", "FULL_STACKYT_EXECUTION_PACK.json"],
        "citations": [],
        "record_paths": [],
        "related_videos": [],
        "confidence": "high for the local validated counts",
        "ambiguity": ["Counts describe the saved snapshot, not live channel state."],
        "not_proven": ["The package does not prove that every channel video is currently available or that any catalog item is safe/adopted."],
        "next_safe_action": "Use an approved metadata-only refresh when the snapshot is stale.",
    }
    return _attach_validation(response, validation)


def videos_mention(term: str) -> dict[str, Any]:
    """Find catalog videos whose public titles contain a term."""
    response = _base_response(term, intent="video_search")
    try:
        catalog, _, _, validation = _load()
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        response["status"] = "unavailable"
        response["answer"] = "Catalog unavailable or stale; no video results were produced from partial data."
        response["validation"]["error"] = str(exc)
        return response
    videos = [video for video in catalog.get("videos", []) if term.casefold() in str(video.get("title", "")).casefold()]
    response["results"] = videos
    response["answer"] = f"{len(videos)} cataloged video title(s) mention {term!r}."
    response["explanation"] = {
        "evidence_state": "public title metadata",
        "proven": [f"{len(videos)} cataloged public video title(s) contain the requested term."] if videos else [],
        "sources": ["full_stackyt_tool_catalog.json", "FULL_STACKYT_CHANNEL_INVENTORY_2026-08-08.md"],
        "citations": [],
        "record_paths": [],
        "related_videos": videos,
        "confidence": "high for title matching; not a transcript claim",
        "ambiguity": ["Title matching does not prove the tool is demonstrated or endorsed."] if videos else ["No cataloged title contains this term."],
        "not_proven": ["The term may occur in a title without being a named project or implementation detail."],
        "next_safe_action": "Open the cited public video or verify the canonical project source manually.",
    }
    return _attach_validation(response, validation)


def compare_matrix(names: list[str]) -> dict[str, Any]:
    """Compare 3+ catalog items in a matrix view using only saved evidence."""
    question = f"Compare matrix: {', '.join(names)}"
    response = _base_response(question, intent="compare-matrix")
    try:
        _, _, items, validation = _load()
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        response["status"] = "unavailable"
        response["answer"] = "Catalog unavailable or stale; no matrix was produced from partial data."
        response["validation"]["error"] = str(exc)
        return response
    try:
        matrix_result = query.compare_matrix(items, names)
    except ValueError as exc:
        response["status"] = "ambiguous"
        response["answer"] = "Comparison matrix requires all names to resolve uniquely."
        response["explanation"]["ambiguity"] = [str(exc)]
        return _attach_validation(response, validation)
    response["results"] = matrix_result["matrix"]["rows"]
    response["answer"] = f"Matrix comparison of {len(names)} items using saved catalog evidence."
    response["explanation"] = {
        "evidence_state": "validated catalog classifications",
        "proven": [f"{len(names)} items were compared using saved catalog labels."],
        "sources": ["full_stackyt_tool_catalog.json", "FULL_STACKYT_EXECUTION_PACK.json"],
        "citations": [],
        "record_paths": [],
        "related_videos": [],
        "confidence": "conservative title/catalog evidence",
        "ambiguity": [],
        "not_proven": matrix_result["not_proven"],
        "next_safe_action": "Review the matrix as classification labels, not as benchmark or adoption results.",
    }
    return _attach_validation(response, validation)


def _refusal(question: str) -> dict[str, Any]:
    response = _base_response(question, status="refused", intent="refusal")
    response["answer"] = (
        "I can search and explain the Full Stack catalog, but this read-only Freebuff skill cannot install, execute, adopt, publish, send, trade, authenticate, use cookies/credentials, or access private data. "
        "I can provide source verification, license review, a threat-model checklist, or a synthetic fixture plan instead."
    )
    response["explanation"] = {
        "evidence_state": "integration safety policy",
        "proven": ["No side effect was attempted or permitted by the wrapper."],
        "sources": ["FULL_STACKYT_FREEBUFF_INTEGRATION_SPEC.md"],
        "citations": [],
        "record_paths": [],
        "related_videos": [],
        "confidence": "high",
        "ambiguity": [],
        "not_proven": ["No side effect was attempted."],
        "next_safe_action": "Ask for a read-only catalog explanation or a bounded evaluation plan.",
    }
    return response


def is_side_effect_request(question: str) -> bool:
    lowered = question.casefold()
    return any(re.search(pattern, lowered) for pattern in _SIDE_EFFECT_PATTERNS)


def ask(question: str) -> dict[str, Any]:
    """Route a supported natural-language Freebuff question to a safe response."""
    question = str(question or "").strip()
    if not question:
        return _refusal("empty question")
    if is_side_effect_request(question):
        return _refusal(question)

    lowered = question.casefold()
    if "when should" in lowered and ("refresh" in lowered or "re-scan" in lowered or "rescan" in lowered):
        response = _base_response(question, intent="refresh_guidance")
        try:
            _, _, _, validation = _load()
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            response["status"] = "unavailable"
            response["answer"] = "Catalog unavailable or stale; no refresh guidance was produced from unvalidated data."
            response["validation"]["error"] = str(exc)
            return response
        response["answer"] = "Use a metadata drift check monthly or when a new channel series is noticed; perform source/license review before any candidate evaluation."
        response["explanation"] = {
            "evidence_state": "documented operating policy",
            "proven": ["The saved operating specification recommends periodic metadata-only drift review."],
            "sources": ["FULL_STACKYT_SNAPSHOT_AND_REFRESH_SPEC.md", "FULL_STACKYT_REFRESH_OPERATIONS.md"],
            "citations": [],
            "record_paths": [],
            "related_videos": [],
            "confidence": "high",
            "ambiguity": [],
            "not_proven": ["A refresh does not make a catalog item current, safe, compatible, or adopted."],
            "next_safe_action": "Run the metadata-only refresh CLI and review its old/new drift report.",
        }
        return _attach_validation(response, validation)
    if "compare" in lowered or " versus " in f" {lowered} " or " vs " in f" {lowered} ":
        try:
            _, _, items, _ = _load()
            names = sorted((str(item.get("name")) for item in items), key=len, reverse=True)
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            names = []
        selected = [name for name in names if re.search(rf"(?<![A-Za-z0-9]){re.escape(name.casefold())}(?![A-Za-z0-9])", lowered)]
        selected = list(dict.fromkeys(selected))
        if len(selected) == 2:
            return compare(selected[0], selected[1])
        if len(selected) > 2:
            response = _base_response(question, status="ambiguous", intent="compare")
            response["answer"] = "Comparison is ambiguous because more than two catalog names matched the question."
            response["explanation"]["ambiguity"] = [f"Matched names: {', '.join(selected)}"]
            return response
        response = _base_response(question, status="ambiguous", intent="compare")
        response["answer"] = "Comparison requires two named catalog items, for example: compare OpenCut and OpenMontage."
        response["explanation"]["ambiguity"] = ["Two unambiguous catalog item names were not found in the question."]
        return response
    if "which videos" in lowered and ("mention" in lowered or "contain" in lowered):
        term_match = re.search(r"(?:mention|contain)\s+(.+?)(?:\?|$)", question, re.IGNORECASE)
        return videos_mention((term_match.group(1).strip() if term_match else question).strip(" .'\""))
    if "summary" in lowered or "how many" in lowered or "counts" in lowered:
        return summary()

    # Prefer an exact known item name embedded in the question.
    try:
        _, _, items, _ = _load()
        names = sorted((str(item.get("name")) for item in items), key=len, reverse=True)
    except (OSError, json.JSONDecodeError, KeyError, ValueError):
        names = []
    for name in names:
        if name.casefold() in lowered and (
            lowered.startswith("what is")
            or "what is proven" in lowered
            or "what is not proven" in lowered
            or "next safe action" in lowered
            or lowered.startswith("tell me about")
            or lowered.startswith("explain")
        ):
            return explain(name)

    filters: dict[str, Any] = {}
    if re.search(r"\bT[1-5](?:[- ]|$)", question, re.IGNORECASE):
        tier = re.search(r"\b(T[1-5](?:-[a-z-]+)?)\b", question, re.IGNORECASE)
        if tier:
            candidate = tier.group(1).lower()
            tier_map = {
                "t1": "T1-quick-win", "t2": "T2-high-fit-controlled", "t3": "T3-high-risk-review",
                "t4": "T4-verify-only", "t5": "T5-exploratory",
            }
            filters["tier"] = tier_map.get(candidate, next((value for value in tier_map.values() if value.casefold() == candidate.casefold()), candidate))
    if ("high-risk" in lowered or "high risk" in lowered) and any(
        term in lowered for term in ("browser", "desktop")
    ):
        response = search(None, risk="High")
        response["results"] = [
            item for item in response["results"]
            if any(term in str(item.get("category", "")).casefold() for term in ("browser", "desktop"))
        ]
        response["answer"] = _explain_answer(response["results"])
        response["explanation"] = _item_explanation(response["results"])
        response["explanation"]["ambiguity"] = []
        return response
    if "high-risk" in lowered or "high risk" in lowered:
        filters["risk"] = "High"
    if "verified source" in lowered or "verified sources" in lowered:
        filters["source"] = "verified"
    if "license-unverified" in lowered or "license unverified" in lowered or "unverified license" in lowered:
        filters["license"] = "unverified"
    if filters:
        return search(None, **filters)
    return search(question)


def format_response(response: dict[str, Any], *, locale: str = "en-US") -> str:
    """Render locale-stable response text; evidence values remain unchanged."""
    supported = {"en-US", "en-GB", "iso", "es", "fr", "de"}
    if locale not in supported:
        raise ValueError(f"unsupported locale; use one of: {', '.join(sorted(supported))}")
    # Locale stubs do not translate evidence values, IDs, URLs, or enums.
    labels = {
        "en-US": {"evidence": "Evidence", "sources": "Sources", "records": "Records", "confidence": "Confidence", "proven": "Proven", "not_proven": "Not proven", "next": "Next safe action", "mode": "Mode"},
        "en-GB": {"evidence": "Evidence", "sources": "Sources", "records": "Records", "confidence": "Confidence", "proven": "Proven", "not_proven": "Not proven", "next": "Next safe action", "mode": "Mode"},
        "es": {"evidence": "Evidencia", "sources": "Fuentes", "records": "Registros", "confidence": "Confianza", "proven": "Probado", "not_proven": "No probado", "next": "Próxima acción segura", "mode": "Modo"},
        "fr": {"evidence": "Preuve", "sources": "Sources", "records": "Enregistrements", "confidence": "Confiance", "proven": "Prouvé", "not_proven": "Non prouvé", "next": "Prochaine action sûre", "mode": "Mode"},
        "de": {"evidence": "Beweis", "sources": "Quellen", "records": "Datensätze", "confidence": "Vertrauen", "proven": "Bewiesen", "not_proven": "Nicht bewiesen", "next": "Nächste sichere Aktion", "mode": "Modus"},
        "iso": {"evidence": "Evidence", "sources": "Sources", "records": "Records", "confidence": "Confidence", "proven": "Proven", "not_proven": "Not proven", "next": "Next safe action", "mode": "Mode"},
    }
    l = labels.get(locale, labels["en-US"])
    lines = [response.get("answer", "")]
    explanation = response.get("explanation", {})
    lines.append(f"{l['evidence']}: {explanation.get('evidence_state') or 'not available'}")
    sources = explanation.get("sources") or []
    if sources:
        lines.append(f"{l['sources']}: {', '.join(sources)}")
    record_paths = explanation.get("record_paths") or []
    if record_paths:
        lines.append(f"{l['records']}: {', '.join(record_paths)}")
    confidence = explanation.get("confidence")
    if confidence:
        lines.append(f"{l['confidence']}: {confidence}")
    proven = explanation.get("proven") or []
    if proven:
        lines.append(f"{l['proven']}: {'; '.join(proven)}")
    citations = explanation.get("citations") or []
    if citations:
        lines.append(f"Citations: {json.dumps(citations, ensure_ascii=False, sort_keys=True)}")
    ambiguity = explanation.get("ambiguity") or []
    if ambiguity:
        lines.append(f"Ambiguity: {'; '.join(ambiguity)}")
    not_proven = explanation.get("not_proven") or []
    if not_proven:
        lines.append(f"{l['not_proven']}: {'; '.join(not_proven)}")
    validation = response.get("validation", {})
    freshness = validation.get("freshness") or {}
    if freshness:
        lines.append(f"Freshness: {freshness.get('state', 'unknown')} (captured {freshness.get('captured_at_utc') or 'unknown'})")
    lines.append(f"{l['next']}: {explanation.get('next_safe_action')}")
    lines.append(f"{l['mode']}: read-only; no catalog item was installed or executed.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", help="natural-language read-only catalog question")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.question:
        parser.error("a read-only catalog question is required")
    response = ask(args.question)
    if args.as_json or args.format == "json":
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print(format_response(response))
    return 0 if response["status"] in {"ok", "refused", "not_found"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
