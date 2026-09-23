# Full Workspace and Archon Audit

**Audit date:** 2026-09-17  
**Scope:** Repository/workspace root, Archon frontend/backend surfaces, security controls, CI, tests, Docker configuration, and documentation governance.  
**Status:** Advice and documentation complete; remediation remains staged and approval-gated.

## Executive verdict

The Archon application has a coherent architecture:

```text
React/Vite frontend -> FastAPI server -> MCP/agent services -> Supabase
```

The surrounding Git worktree is not a clean application repository. It is a large Windows user workspace containing many projects, dashboards, archives, runtime state, private data, browser/session artifacts, and credentials. The application should not be treated as production-ready until authentication failure behavior and repository/credential hygiene are addressed.

**Overall risk:** High  
**Production approval:** Not approved  
**Primary reason:** fail-open authentication behavior when Supabase is unavailable, combined with credential-bearing material in the worktree/history.

## Golden Rules

These rules govern all future work:

1. **Nothing is obsolete.** Preserve historical work and context unless the owner explicitly approves disposal.
2. **All projects are permanent.** Archive and isolate; do not casually delete or collapse projects.
3. **All AI tools are essential.** Integrate, connect, document, or archive tools rather than removing them by assumption.
4. **Add, integrate, connect, document.** New work should improve the wider ecosystem and remain discoverable.
5. **Enhance, don’t reduce.** Preserve existing capability and behavior unless a replacement is proven and backed up.
6. **Personal folders are read-only.** Do not alter personal files, external drives, archives, or private records without explicit approval.
7. **Never commit secrets.** Credentials, API keys, tokens, cookies, SSH keys, session exports, and private data do not belong in Git.
8. **Append-only everything.** Add audit history and status records; do not erase or rewrite historical evidence by default.
9. **No destructive actions without explicit approval.** This includes deletion, mass moves, history rewrites, force-pushes, credential revocation, deployment, and live-service changes.
10. **Preserve and verify.** Keep backups, report exact verification results, and never claim a failing check passed.
11. **Keep the knowledge graph current.** After code changes, run the repository graph update when graphify is available.

## Action policy

### Safe to perform during normal audit work

- Read and inspect files, configuration, tests, and logs.
- Run non-destructive tests, linters, typechecks, builds, and security validators.
- Add documentation, tests, and reversible source changes.
- Create reports, manifests, inventories, and remediation plans.
- Update links and indexes without deleting existing documentation.

### Requires explicit approval

- Delete, move, or bulk-clean files.
- Modify personal folders or external drives.
- Rotate/revoke credentials or contact providers.
- Rewrite Git history, remove refs, force-push, or alter the remote.
- Deploy, change production infrastructure, change databases, or touch real-money services.
- Install or provision third-party services.
- Replace or remove existing AI tools/projects.

### Prohibited without authorization and safety review

- Commit active secrets or private session material.
- Upload private artifacts to external systems.
- Claim security or test success without evidence.
- Use a cleanup operation that cannot be rolled back.

## Findings

### P0 — Authentication fails open when Supabase is unavailable

**Location:** `python/src/server/middleware/auth_middleware.py`

The current behavior permits a request through when Supabase is unavailable as long as an `X-API-Key` header exists. Header presence is not proof of authentication. A database outage, invalid configuration, or initialization failure can therefore become an authentication bypass.

**Required behavior:**

- Production + Supabase unavailable: reject with `503` or `401`.
- Test/local bypass: only through an explicit opt-in setting.
- Arbitrary API-key values: always rejected when validation cannot occur.
- Add a regression test for the unavailable-Supabase case.

**Acceptance evidence:** a focused test demonstrates that a request with any arbitrary key is rejected when the validator is unavailable.

### P0 — Credential and private artifacts are present in the Git worktree/history

The repository scope includes credential-like files, `.git-credentials`, `credentials.env`, SSH material, browser cookies/session exports, token/key files, private financial data, and runtime artifacts. The worktree is also extremely large and contains many unrelated systems.

**Required response:**

1. Treat credentials as potentially exposed.
2. Rotate/revoke every affected credential class through the provider owners.
3. Review provider audit logs.
4. Preserve an encrypted forensic archive outside the active repository.
5. Create a clean Archon-only clone.
6. Prepare a separate, approval-gated history rewrite plan.
7. Only force-update a remote during an approved maintenance window.
8. Require fresh reclones after a rewrite.

No credential rotation, deletion, or history rewrite was performed by this audit.

### P1 — Internal credential endpoints depend too heavily on source-IP checks

**Location:** `python/src/server/api_routes/internal_api.py`

IP/Docker-network checks are fragile behind reverse proxies and do not replace authentication. Forwarded headers can also be misconfigured or spoofed if proxy trust is not explicit.

**Required behavior:**

- Require service authentication independent of source IP.
- Use an explicit trusted-proxy configuration.
- Keep network checks as defense in depth, not as the sole control.
- Add tests for direct, proxied, unauthorized, and malformed-origin requests.
- Avoid returning credentials in logs or broad error payloads.

### P1 — Backend test/route contract drift

The audit observed backend failures where tests mounted a router with a prefix but called unprefixed paths, producing `404` responses. A settings test also exposed a `500` versus expected `404` handling mismatch.

**Required response:**

- Define route prefixes in one place.
- Use named route helpers or a shared API contract in tests.
- Decide and document the intended error contract.
- Add tests for both the mounted application and isolated routers.
- Capture traceback-level causes before changing expected statuses.

Prior recorded result: **280 backend tests passed, 3 failed**.

### P1 — Frontend lint gate fails

The frontend had **3 ESLint errors and approximately 242 warnings** in the audit run. The production build can still succeed because Vite does not automatically type-check or lint.

**Required response:**

- Fix all blocking ESLint errors.
- Establish a warning budget and burn down warnings by category.
- Make CI run lint explicitly before build.
- Keep generated/vendor files excluded through the correct ignore configuration.

### P1 — Python version mismatch across project configuration and images

The project declares Python 3.12 while at least one server Docker image uses Python 3.11. This can produce dependency, syntax, and runtime differences between local CI and deployment.

**Required response:**

- Select one supported Python version.
- Align `pyproject.toml`, Dockerfiles, CI, local setup documentation, and lockfiles.
- Add a CI assertion that reports the runtime version.

### P1 — Production frontend container behavior needs confirmation

The frontend container configuration was identified as using development-server behavior where a static production server is expected.

**Required response:**

- Build the frontend in a builder stage.
- Serve the generated static assets with the intended production web server.
- Keep development server commands limited to local development.
- Add a container smoke test for the served application and health endpoint.

### P2 — Repository scope is unsafe and unmaintainable

The worktree contains approximately 18,674 tracked files, approximately 855 untracked paths, thousands of HTML files, large duplicated dashboards/backups, unrelated applications, runtime databases, personal records, and private artifacts. Git status also shows extensive pre-existing modifications and untracked material.

**Required response:**

- Do not bulk-clean this worktree.
- Preserve it as a historical workspace/archive.
- Create a separate clean Archon repository from an approved allowlist.
- Define ownership and backup locations for every retained project.
- Add repository boundary checks so personal/runtime directories cannot be staged accidentally.

### P2 — Large frontend bundle and stale dependency metadata

The audit identified bundle-size and stale Browserslist/dependency-maintenance concerns.

**Required response:**

- Measure the production bundle by route/chunk.
- Code-split heavy pages and optional integrations.
- Update Browserslist and dependencies during a controlled, separately verified pass.
- Do not combine dependency upgrades with security fixes unless necessary.

### P2 — Audit/log formatting hygiene

`git diff --check` reported many CRLF/trailing-whitespace findings in append-only audit material.

**Required response:**

- Preserve existing historical logs.
- Apply formatting normalization only to newly maintained files or through an approved migration.
- Configure line-ending behavior consistently for future files.

## Verification record

The prior audit run recorded the following:

| Check | Result | Interpretation |
|---|---:|---|
| Backend tests | 280 passed, 3 failed | Not release-ready; route/error contracts need correction |
| Frontend ESLint | 3 errors, ~242 warnings | CI quality gate fails |
| Python compile checks | Passed for inspected source/changed files | Syntax is not the primary blocker |
| Security documentation validator | Passed | Documentation structure is valid, not proof of clean secrets |
| Full tracked-file secret scan | Did not complete cleanly at workspace scale | Treat credential exposure as unresolved |
| TypeScript/build checks | Build can pass independently; type/lint gates remain separate | Build success is insufficient |
| `git diff --check` | Many findings in historical audit material | Hygiene issue; preserve history before normalization |

The results above are evidence from the audit session, not a claim that all current files are clean. Re-run after any remediation.

## Remediation sequence

### Phase 0 — Containment (approval required for external actions)

- Stop treating the workspace root as a deployable repository.
- Do not push or deploy from this worktree.
- Identify and quarantine credential-bearing material without deleting it.
- Begin provider rotation using the existing rotation checklist.

### Phase 1 — Reversible application fixes

- Change authentication to fail closed.
- Add unavailable-Supabase regression coverage.
- Harden internal credential routes with service authentication.
- Correct route-prefix and error-contract tests.
- Fix the three blocking frontend lint errors.
- Align Python runtime declarations and Docker images.
- Make CI run lint, typecheck, tests, and build as distinct required gates.

### Phase 2 — Clean repository boundary

- Build an Archon-only allowlist.
- Export a preserved, encrypted archive outside the active repository.
- Create a clean clone and verify it independently.
- Configure ignore rules and staging checks.
- Obtain explicit approval before any remote history rewrite.

### Phase 3 — Performance and maintenance

- Measure and split frontend bundles.
- Update dependency metadata in a controlled pass.
- Normalize only newly maintained documentation line endings.
- Add recurring security and repository-boundary checks.

## Approval gates

No action below is complete merely because it is documented:

- [ ] Owner approves credential rotation/revocation.
- [ ] Provider audit logs reviewed.
- [ ] Encrypted forensic archive verified.
- [ ] Archon allowlist approved.
- [ ] Clean clone built and tested.
- [ ] Remote history rewrite approved and scheduled.
- [ ] New clone instructions distributed after rewrite.
- [ ] Production deployment approved after all P0/P1 gates pass.

## Current conclusion

The correct next move is to stabilize security and isolate repository boundaries before adding features. Documentation preserves the findings and the owner’s Golden Rules; it does not silently authorize destructive cleanup, credential changes, history rewriting, or deployment.
