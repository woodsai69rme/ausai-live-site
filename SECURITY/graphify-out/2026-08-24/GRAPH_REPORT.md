# Graph Report - SECURITY  (2026-08-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 143 nodes · 155 edges · 12 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `373cdf5f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Credential Incident Response
- Repository Audit and Remediation Status
- Forensic Archive and Worktree Export Plan — 2026-08-24
- Disposable-Clone Rewrite Ref Scope — 2026-08-24
- Security and Remediation Documentation Manifest — 2026-08-24
- Provider Workstreams
- Remediation Implemented
- External Action Handoff — 2026-08-24
- History Rewrite Readiness — 2026-08-24
- validate_security_docs.py
- Credential Incident Response
- Security Documentation

## God Nodes (most connected - your core abstractions)
1. `Forensic Archive and Worktree Export Plan — 2026-08-24` - 14 edges
2. `Repository Audit and Remediation Status` - 12 edges
3. `scan_paths()` - 11 edges
4. `Remediation Implemented` - 9 edges
5. `Security and Remediation Documentation Manifest — 2026-08-24` - 9 edges
6. `Disposable-Clone Rewrite Ref Scope — 2026-08-24` - 9 edges
7. `History Rewrite Readiness — 2026-08-24` - 8 edges
8. `Original Findings` - 7 edges
9. `External Action Handoff — 2026-08-24` - 6 edges
10. `Credential Incident Response` - 6 edges

## Surprising Connections (you probably didn't know these)
- `check_security_docs()` --calls--> `scan_paths()`  [EXTRACTED]
  SECURITY/validate_security_docs.py → SECURITY/secret_scan.py

## Import Cycles
- None detected.

## Communities (12 total, 0 thin omitted)

### Community 0 - "Credential Incident Response"
Cohesion: 0.18
Nodes (19): Namespace, Finding, main(), _paths_from_args(), _print_text(), Path, Fail-closed scan for high-confidence credentials in repository files.  The scann, Resolve a path and reject symlink/path traversal outside the worktree. (+11 more)

### Community 1 - "Repository Audit and Remediation Status"
Cohesion: 0.11
Nodes (17): Active-Code Enhancements Reviewed, Change Record, Critical: credential-shaped material in tracked history, Executive Summary, External Actions Still Required, Git and Archive Boundary, High: broad automation permissions, High: previously non-blocking CI checks (+9 more)

### Community 2 - "Forensic Archive and Worktree Export Plan — 2026-08-24"
Cohesion: 0.13
Nodes (14): Acceptance record, Artifact layout, Current blockers and next handoff, Forensic Archive and Worktree Export Plan — 2026-08-24, Non-actions, Phase 1 — Freeze and capture read-only state, Phase 2 — Export all worktree bytes and Git evidence, Phase 3 — Build and encrypt the payload (+6 more)

### Community 3 - "Disposable-Clone Rewrite Ref Scope — 2026-08-24"
Cohesion: 0.13
Nodes (14): 1. Active local branch to publish, 2. Protected local evidence branch, 3. Tags, 4. Remote branches on `origin`, 5. Remote tags on `origin`, Current read-only inventory, Current verification and blockers, Decision status (+6 more)

### Community 4 - "Security and Remediation Documentation Manifest — 2026-08-24"
Cohesion: 0.14
Nodes (13): Active AI Influencer Studio, Approval-gated actions, CI and workflows, Documentation maintenance rule, Documentation map, Git and archive boundary, Golden Rules applied, Graphify evidence (+5 more)

### Community 5 - "Provider Workstreams"
Cohesion: 0.18
Nodes (10): Before History Scrubbing, Credential Rotation Checklist, Current Local Boundary, GitHub, Google, OpenAI-Compatible Providers, Provider Workstreams, SSH and Git Credentials (+2 more)

### Community 6 - "Remediation Implemented"
Cohesion: 0.22
Nodes (9): CI and workflow hardening, Drive/RAG self-test portability, Enhanced security validation, Full Stack catalog test drift, Graphify restoration and scoped graphs, Remediation Implemented, Secret-scanning guardrail, Security runbooks (+1 more)

### Community 7 - "External Action Handoff — 2026-08-24"
Cohesion: 0.22
Nodes (8): External Action Handoff — 2026-08-24, History scrubbing, Local verification completed, Provider credential work, Read-only evidence, Related documents, Required approval gates, Status

### Community 8 - "History Rewrite Readiness — 2026-08-24"
Cohesion: 0.22
Nodes (8): Approval gates before execution, Current read-only inventory, Disposable-clone procedure, Explicit non-actions in this session, History Rewrite Readiness — 2026-08-24, Post-rewrite checks, Related documents, State

### Community 9 - "validate_security_docs.py"
Cohesion: 0.39
Nodes (8): check_document_files(), check_security_docs(), check_workflows(), _load_text(), main(), Path, Validate the repository security documentation and workflow guardrails.  This co, validate()

### Community 10 - "Credential Incident Response"
Cohesion: 0.29
Nodes (6): CI policy, Credential Incident Response, History scrubbing, Immediate containment, Local checks, Preserve without re-exposing

### Community 11 - "Security Documentation"
Cohesion: 0.29
Nodes (6): Control Boundaries, Current Status, Related Operational Evidence, Security Documentation, Start Here, Validation Contract

## Knowledge Gaps
- **90 isolated node(s):** `Executive Summary`, `Scope and Repository Shape`, `Critical: credential-shaped material in tracked history`, `High: unhealthy repository boundary`, `High: previously non-blocking CI checks` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Repository Audit and Remediation Status` connect `Repository Audit and Remediation Status` to `Remediation Implemented`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `scan_paths()` connect `Credential Incident Response` to `validate_security_docs.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `Remediation Implemented` connect `Remediation Implemented` to `Repository Audit and Remediation Status`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `Executive Summary`, `Scope and Repository Shape`, `Critical: credential-shaped material in tracked history` to the rest of the system?**
  _90 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Repository Audit and Remediation Status` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `Forensic Archive and Worktree Export Plan — 2026-08-24` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `Disposable-Clone Rewrite Ref Scope — 2026-08-24` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._