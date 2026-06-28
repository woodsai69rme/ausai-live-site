# 🔌 MCP_HOST_CONNECTOR.ps1 — companion explainer

> **The first concrete, additive host-side adapter for the MCP server list catalogued in `MCP_REGISTRY.md`. Reads the registry, performs an HTTP health-check, appends a single line per call to a configurable audit log. Never writes to source scripts, never rewrites prior docs.**

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `MCP_HOST_CONNECTOR.ps1` + NEW `MCP_HOST_CONNECTOR.md`. Nothing modified.
- ✔ Reads only `~/.config/mcp/registry.json` (or `$MCP_REGISTRY_PATH`). Never writes.
- ✔ Appends ONE line per call to `$HOME/MCP_HOST_HEALTH.log` (or `-LogPath`). Never rewrites.
- ✓ Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER picked as a registry or audit target.
- ✓ Never opens, mounts, or writes the connection to any source project (zen-mcp, mcp-zero, etc.) without the operator's explicit `-ServerName` argument.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.

---

## 1. Why this exists

`MCP_REGISTRY.md` catalogues 5 known MCP servers (zen-mcp-server, mcp-ecosystem-platform, mcp-crawl4ai-rag, mcp-zero, n8n-mcp) plus 3 planned slots. The catalog is documentation-only. **The connector is the first time an operator can actually check whether a registry entry is `up` from this host** — without hand-running `curl`.

---

## 2. Inputs

| Parameter     | Required | Default                                       | Notes                                       |
| ------------- | -------- | --------------------------------------------- | ------------------------------------------- |
| `-ServerName` | YES      | —                                             | Must match a `name` entry in the registry. |
| `-DryRun`     | no       | off                                           | Print what would happen; append no audit line. |
| `-LogPath`    | no       | `$HOME/MCP_HOST_HEALTH.log`                    | Any absolute path NOT inside a personal folder. |

Environment variables:

- `MCP_REGISTRY_PATH` — optional override of the registry location, also not in a personal folder.

---

## 3. Operation flow (additive)

1. **Resolve registry:** read `$env:MCP_REGISTRY_PATH` or `$HOME/.config/mcp/registry.json`.
2. **Personal-folder guard:** if either the registry or the log-path resolves inside any of `Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD`, throw `REFUSED: ...` and exit non-zero. **No writes are attempted.**
3. **Read-only registry parse.**
4. **Locate server entry** by `name == -ServerName`. If absent, throw `REFUSED: ...`.
5. **Health-check:** `GET <endpoint>/health` with a 5-second timeout. The endpoint URL is built deterministically — no globbing, no shell expansion.
6. **Append ONE audit line:**

   ```
   <ISO8601 UTC> | ok=<true|false> | status=<code> | server=<name> | endpoint=<url> | (error=...|bytes_shown=<n>)
   ```

7. **Exit code:** `0` on healthy response, `1` on failed health-check, `2` on argument / path refusal.

---

## 4. Never-do list

The connector **MUST NEVER**:

- DELETE the registry or the audit log. (`del` is never issued.)
- REWRITE the audit log. (`Truncate`, `Clear-Content`, `Set-Content` are never used.)
- WRITE to any path inside a personal folder. Refusal happens early.
- ATTEMPT a write of any source project under `ACTIVE_PROJECTS/`. The current scope is host-side health-check only; mounting source projects is a separate future script.
- INVENT a registry entry. The registry is the source of truth.
- BUNDLE credentials. The connector never reads `.env*` files; it never accepts tokens; it only exercises the public health URL of each registry entry.

The connector **MUST ALWAYS**:

- Honour the `-DryRun` flag.
- Stop immediately on personal-folder resolution.
- Append a single line with the ISO8601 UTC timestamp prefix.
- Return a deterministic exit code.

---

## 5. Refusal matrix

| Trigger                                          | Outcome                                   |
| ------------------------------------------------ | ----------------------------------------- |
| `-ServerName` not in registry                    | Non-zero exit, no audit line.             |
| Registry or log path inside Rule #8 personal     | Thrown `REFUSED`, exit 2, no audit line. |
| `-DryRun` set                                    | Print what would happen, no audit line.   |
| Health endpoint times out (5s)                   | Audit line with `ok=false`, exit 1.       |
| Health endpoint returns non-2xx                  | Audit line with `status=<code>`, exit 1.  |

---

## 6. Audit-log layout (one example line)

```
2026-03-08T23:42:01Z | ok=True | status=200 | server=zen-mcp-server | endpoint=http://127.0.0.1:8765 | bytes_shown=142
```

Failure example:

```
2026-03-08T23:43:55Z | ok=False | status=-1 | server=n8n-mcp | endpoint=http://127.0.0.1:5678 | error=Connection refused
```

Lines are append-only. The log file naturally grows by roughly the number of operator health-checks. No rotation script is bundled — operators are free to add their own logrotate / `Clear-Content` viewer, but never via this script.

---

## 7. Acceptance tests

- `test_healthy_mcp_server` — entry whose `/health` returns 200 → `ok=True`, exit 0, audit line present.
- `test_unhealthy_mcp_server` — entry whose `/health` returns 503 → `ok=False`, exit 1, audit line present.
- `test_unknown_server` — `-ServerName ghost-mcp` → "not found in registry", exit non-zero, NO audit line.
- `test_personal_folder_registry` — `MCP_REGISTRY_PATH` under Documents → `REFUSED` error, exit 2, NO audit line.
- `test_personal_folder_log` — `-LogPath C:\Users\karma\Downloads\audit.log` → `REFUSED` error, exit 2, NO audit line.
- `test_dry_run_no_audit` — `-DryRun` does not create the log file even if missing beforehand.

---

## 8. Compatibility with everything prior

| Prior artifact              | Status      |
| --------------------------- | ----------- |
| `MCP_REGISTRY.md`           | READ-ONLY. The catalog is the source of truth for `name` and `endpoint`. |
| `MCP_INSTALL_PLAN.md`       | Untouched. Connector covers the OPERATE step; install plan covers INSTALL. |
| `verify_backups.ps1`        | Untouched. |
| `Register-BackupTask.ps1`   | Untouched. |
| `EnvironmentSanitizer.ps1`  | Untouched. |

This connector slots between **MCP_REGISTRY.md** (catalog) and **MCP_INSTALL_PLAN.md** (install) — it is the OPERATE step.

---

## 9. Companion to OPT-5.1

This artifact plus `MCP_REGISTRY.md` plus `MCP_INSTALL_PLAN.md` together close OPT-5.1 (catalog) and OPT-5.1 follow-on (install plan). The next step under OPT-5.1 is **OPT-5.1 live**: a script that, given a registry entry, installs and starts it (install plan's step 1 → 4). That is intentionally out of scope here.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
