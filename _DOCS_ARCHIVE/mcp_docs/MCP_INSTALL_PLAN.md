# 🔌 MCP INSTALL PLAN  *(OPT-5.1 follow-on; ENH-S4 companion)*

**Generated:** June 17, 2026
**Companion to:** `MCP_REGISTRY.md`, `PROJECT_BRAIN_2_0_SPEC.md` (Phase E exposes Brain via MCP).
**Compliance:** Add · Integrate · Connect · Document · Enhance.  No deletions.  No personal-folder touch.

> **Goal:** Install GitHub MCP, Tavily MCP, Memory MCP — without breaking any of the existing dot-folder tools (Claude / Qwen / Cursor / Windsurf / Trae / Kiro / Cline / Continue / Gemini / Codex / OpenCode / Factory / Kilo).

---

## 🪙 GOLDEN RULES IN EFFECT

```
⭐ Rule #1  Nothing is obsolete — never overwrite an existing MCP config.
⭐ Rule #3  ALL AI TOOLS ESSENTIAL — install is composition, never replacement.
⭐ Rule #8  PERSONAL FILES ARE SACRED — never read Documents/... for npm auth tokens.
⭐ Rule #9  ADD · INTEGRATE · CONNECT · DOCUMENT.
```

---

## 🔑 THE NPM-AUTH WORKAROUND

The blocker is `npm` needing a credentials store that doesn't exist / is invalid on this host. Options, in order of preference (each is *additive*):

### Option A — Fine-grained Personal Access Token (PAT) routed safely

1. Create a fine-grained PAT scoped to only the registries you actually consume (e.g., `registry.npmjs.org`).
2. **Never** write the PAT plaintext to `Documents/`, `Downloads/`, `Pictures/`, etc.
3. Append to `~/.npmrc` *only if missing*:

```
registry=https://registry.npmjs.org/
//registry.npmjs.org/:_authToken=${NPM_AUTH_TOKEN}
```

…where `NPM_AUTH_TOKEN` is resolved at runtime from OPT-7.1 wrapper (audit + Windows Credential Manager).

### Option B — Sidecar registry process

```
docker run --rm -e NPM_AUTH_TOKEN \
  --name npm-mirror -p 4873:4873 verdaccio
```

A local Verdaccio (or `npm-registry-server`) proxies upstream and stores no plaintext token. **Each client** reads from `http://localhost:4873/`. **No removal** of upstream tools; this is *purely additive*.

### Option C — Workspace-scoped login

```
cd ~/PROJECTS/<your-mcp-workspace>
npm login --scope=@your-org
```

Token stored in `~/.npmrc` (workspace-scoped). Personal folders untouched.

---

## 📦 INSTALL SEQUENCE PER SERVER  *(additive, idempotent)*

### 1) GitHub MCP

```
# Optional: set scope
export NPM_CONFIG_REGISTRY=https://registry.npmjs.org/

npm install --prefix ~/.local/mcp/github @modelcontextprotocol/server-github

# Verify
~/.local/mcp/github/node_modules/.bin/mcp-server-github --version
```

Append `MCPS_GITHUB_VERSION=<x.y.z>` to `MCP_REGISTRY.md` (this document row). **No removal.**

### 2) Tavily MCP

```
npm install --prefix ~/.local/mcp/tavily mcp-server-tavily

# Set TAVILY_API_KEY via OPT-7.1 wrapper; never plaintext.
```

Append `MCPS_TAVILY_VERSION=<x.y.z>` to `MCP_REGISTRY.md`. **No removal.**

### 3) Memory MCP

```
pip install mcp-server-memory --target ~/.local/mcp/memory
```

Append `MCPS_MEMORY_VERSION=<a.b.c>` (Python integral; `pip` instead of `npm`).

> **Note:** Python3 is not available in this Windows-bash shell — runtime testing of the install sequence is **deferred** to a session where pip/python3 are reachable. The plan's static steps remain valid.

---

## 🧪 ACCEPTANCE TESTS

| Test | Pass criterion |
|---|---|
| `npmrc_sane` | `npm config get registry` returns a working URL |
| `mcp_alive_<server>` | Each server's executable responds to `--help` without error |
| `caller_invokes` | A Claude / Cline / Kiro / Kilo session invokes MCP tool successfully |
| `personal_folder_offlimits` | No `.npmrc` ever written into Documents / Downloads / Pictures / Videos / Music / Desktop / OneDrive |
| `appends_only` | Re-running the install does NOT replace any of the prior MCP files; new ones coexist |

---

## 🛡️ PERSONAL-FOLDER GUARD  *(Rule #8)*

- `Documents/`, `Downloads/`, `Pictures/`, `Videos/`, `Music/`, `Desktop/`, `OneDrive/`, `Downloads\ARCHIVE_OLD/` — never written. `~/.npmrc` is in `$HOME`, **not** in those subfolders.
- If a personal folder scan reveals an instrumented `.npmrc`, we **report** it (never modify).

---

## 🔁 OPERATIONAL NOTES

- Run `mcp-registry-self-test` (new, additive, in `MCP_REGISTRY.md` footer) before any agent session that needs MCP capability.
- If a tool's existing MCP server (e.g., Claude's bundled MCP) breaks after install, the breaker is **additive-only**: revert by setting the env var back rather than by deleting. **No `rm`** of MCP files.

---

## 📂 NEW FILES THIS TURN

- `MCP_INSTALL_PLAN.md` (this file)

**No tool removed. No config overwritten.**

---

## ✅ COMPLIANCE FOOTER

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW install plan. Failed past attempts remain; the plan adds a path forward.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
```
