# Graph Report - SECURITY  (2026-08-23)

## Corpus Check
- 5 files · ~3,442 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 55 nodes · 53 edges · 7 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `373cdf5f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Credential Incident Response
- secret_scan.py
- Provider Workstreams
- Credential Rotation Checklist
- Remediation Implemented
- Original Findings
- Security Documentation

## God Nodes (most connected - your core abstractions)
1. `Repository Audit and Remediation Status` - 11 edges
2. `Original Findings` - 7 edges
3. `Remediation Implemented` - 7 edges
4. `Credential Incident Response` - 6 edges
5. `Provider Workstreams` - 6 edges
6. `Security Documentation` - 5 edges
7. `Credential Rotation Checklist` - 5 edges
8. `scan_file()` - 4 edges
9. `main()` - 4 edges
10. `tracked_files()` - 2 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (7 total, 0 thin omitted)

### Community 0 - "Credential Incident Response"
Cohesion: 0.29
Nodes (6): CI policy, Credential Incident Response, History scrubbing, Immediate containment, Local checks, Preserve without re-exposing

### Community 1 - "secret_scan.py"
Cohesion: 0.43
Nodes (6): Path, main(), Fail-closed scan for high-confidence credentials in the repository and Git histo, Scan incrementally so large generated/archive files cannot exhaust RAM., scan_file(), tracked_files()

### Community 2 - "Provider Workstreams"
Cohesion: 0.18
Nodes (10): Before History Scrubbing, Credential Rotation Checklist, Current Local Boundary, GitHub, Google, OpenAI-Compatible Providers, Provider Workstreams, SSH and Git Credentials (+2 more)

### Community 3 - "Credential Rotation Checklist"
Cohesion: 0.20
Nodes (9): Change Record, Executive Summary, External Actions Still Required, Git and Archive Boundary, Operating Rules Going Forward, Related Documents, Repository Audit and Remediation Status, Scope and Repository Shape (+1 more)

### Community 4 - "Remediation Implemented"
Cohesion: 0.29
Nodes (7): CI and workflow hardening, Full Stack catalog test drift, Graphify restoration and scoped graphs, Remediation Implemented, Secret-scanning guardrail, Security runbooks, SLEEP_TRIPLE status semantics

### Community 5 - "Original Findings"
Cohesion: 0.29
Nodes (7): Critical: credential-shaped material in tracked history, High: broad automation permissions, High: previously non-blocking CI checks, High: unhealthy repository boundary, Medium: data and test drift, Medium/High: optimistic runtime status, Original Findings

### Community 6 - "Security Documentation"
Cohesion: 0.33
Nodes (5): Control Boundaries, Current Status, Related Operational Evidence, Security Documentation, Start Here

## Knowledge Gaps
- **37 isolated node(s):** `Executive Summary`, `Scope and Repository Shape`, `Critical: credential-shaped material in tracked history`, `High: unhealthy repository boundary`, `High: previously non-blocking CI checks` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Repository Audit and Remediation Status` connect `Credential Rotation Checklist` to `Remediation Implemented`, `Original Findings`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `Original Findings` connect `Original Findings` to `Credential Rotation Checklist`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `Remediation Implemented` connect `Remediation Implemented` to `Credential Rotation Checklist`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **What connects `Executive Summary`, `Scope and Repository Shape`, `Critical: credential-shaped material in tracked history` to the rest of the system?**
  _37 weakly-connected nodes found - possible documentation gaps or missing edges._