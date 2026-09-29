# What's Left · Master (all tracks) — 2026-07-17_i

**Updated:** 2026-07-17  
**Do-all rule:** Automate everything that does not need your passwords, payment tokens, or account UI.

---

## Snapshot

| Track | Automation | Score / tests | Blocks live value |
|-------|------------|---------------|-------------------|
| **Free AI / War Room / Drive RAG** | **COMPLETE** | free stack ALL PASSED · drive self-test 22/22 | Cloud Drive mount only (optional) |
| **Cash / Gumroad / Stripe / Fiverr** | Ready tooling; **A$0 live** | setup **11/22 (50%)** · tests **47/47** | Your tokens + product listing |
| **Remote desktop (CRD)** | Host READY | chromoting RUNNING | Share to second Gmail + phone PIN |

---

## A · Free stack — DONE (no rework)

- Catalog: `FREE_RESOURCES_MASTER.md` · registry · War Room Free tab  
- Drive RAG: lean backup · FTS SQLite · Ollama answer fallbacks · zip staging excluded  
- Helpers: `drive-connect` · Archon `/health` · launchers  
- This run: folder_mirror backup · workspace + drive re-ingest · export_zip ready for upload  

| Signal | Now |
|--------|-----|
| RAG workspace / drive | ~3367 / ~2052 (no `_zip_staging`) |
| Local mirror | `BACKUPS\GOOGLE_DRIVE_MIRROR` |
| Zip for manual upload | `BACKUPS\GOOGLE_DRIVE_MIRROR\warroom_backup_20260717_063602.zip` |
| My Drive letter | **not mounted** |

**Human optional:** Drive tray → Mirror folder or letter · upload the zip at [drive.google.com](https://drive.google.com) · optional rclone.

Detail: `WHAT_IS_LEFT_FREE_DRIVE_STACK.md`

---

## B · Cash / revenue — HUMAN ONLY (ordered)

| # | Action | Where | ~Time |
|---|--------|-------|------|
| 1 | Gumroad access token (one non-# line) | `CONFIG\gumroad_token.txt` | 2 min |
| 2 | List A$47 + A$67 products | ZIPs under `REVENUE_GENERATORS\...\dist\` | 15 min |
| 3 | 3 Stripe **Live** Payment Links | `CONFIG\payment_links.env` | 20 min |
| 4 | Real Calendly username | same file | 5 min |
| 5 | Wire site | `python TOOLS\apply_payment_links.py --apply` + redeploy | 5 min |
| 6 | CRD share woodsai + ashlee + phone PIN | remotedesktop.google.com/access | 10 min |
| 7 | Fiverr 3 gigs | `FIVERR_PASTE_PACKAGE.md` | 30 min |
| 8 | Week-1 outreach | `OUTREACH_WEEK1.md` after live | ongoing |
| 9 | Flip SLEEP `dry_run` | **Only after first real A$** | later |

**Honesty:** Automation cannot invent payment credentials. Until 1–7: **A$0**.

Detail: `PROCEED_ALL_STATUS.md` · `WHATS_LEFT_2026-07-17_f.md`

---

## C · After you paste keys

```bat
python TOOLS\proceed_all.py --check
python TOOLS\apply_payment_links.py --apply
python TOOLS\test_setup_stack.py
EXECUTE_ALL_OPTIONS.bat /nopause
```

Or say: **proceed all**

---

## D · Daily free-stack (already works offline)

```bat
python TOOLS\test_free_stack.py
python TOOLS\drive_backup_rag\drive_backup_rag.py status
python TOOLS\drive_backup_rag\drive_backup_rag.py drive-connect
python TOOLS\drive_backup_rag\drive_backup_rag.py backup --method folder_mirror --run
OPEN_FREE_RESOURCES.bat
LAUNCH_DRIVE_BACKUP_RAG.bat
```

---

## E · Do-all this run (2026-07-17_i)

| Action | Result |
|--------|--------|
| Free stack retest | ALL PASSED |
| Drive self-test | 22/22 |
| Setup tests | 47/47 |
| Setup score refresh | 11/22 (50%) |
| Lean backup | 50 sources · 163 files · ~2.8 MB |
| Workspace + drive ingest | clean · no zip_staging |
| export_zip | `warroom_backup_20260717_063602.zip` |
| proceed_all --check | Stripe/Calendly placeholders still NEED |
| Docs | X: + `_DOCS_ARCHIVE` session `_i` |

**Nothing left that agents can finish without your account UI.**
