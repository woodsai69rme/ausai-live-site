"""Google Drive reference-media uploader.

Implements the ``refdrive.txt`` workflow:

- Collect images and ``.mp4`` videos (max 15 MB) from Downloads and all drives.
- Dedupe by **content hash** (md5), never by filename -- names collide.
- Always copy / never replace: the done list is append-only, so re-runs never
  re-upload identical content.
- Filters: no svg/bmp/gif, nothing <= 250 KB, no screenshots older than 7 days.
- Slow uploads: a persisted pending + done list, with small batches and delays
  between batches so slow connections can resume at any point.

The upload itself is driven through Playwright against the web Drive folder
(the shared folder is not a mounted drive). Nothing is ever deleted locally or
remotely; the tool only reads local files and uploads them.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Default shared folder from shareg.txt / refdrive.txt.
DEFAULT_FOLDER_ID = "13Ck6VKzc2pVIPBNW33wWjSTSDmRjYP2f"
DEFAULT_FOLDER_URL = f"https://drive.google.com/drive/folders/{DEFAULT_FOLDER_ID}?usp=sharing"

# File policy from refdrive.txt.
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTS = {".mp4"}
SUPPORTED_EXTS = IMAGE_EXTS | VIDEO_EXTS
BANNED_EXTS = {".svg", ".bmp", ".gif"}
MIN_BYTES = 250_000  # 250 KB, inclusive
MAX_BYTES = 15 * 1024 * 1024  # 15 MB, inclusive
SCREENSHOT_MAX_AGE_DAYS = 7

SCREENSHOT_NAME_PATTERNS = (
    re.compile(r"screenshot", re.IGNORECASE),
    re.compile(r"\bscrn\b", re.IGNORECASE),
    re.compile(r"screen[ _-]?shot", re.IGNORECASE),
    re.compile(r"^screenshot", re.IGNORECASE),
)

PLAYWRIGHT_CONTEXT_DIR = r"C:\Users\karma\AppData\Local\Google\Chrome\User Data\Default_Automated"

# Drive API OAuth2 paths (backend="drive_api"). The token is created by a
# one-time InstalledAppFlow and refreshed automatically afterwards.
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_TOKEN_PATH = Path("~/.ai_influencer_studio/gdrive_token.json").expanduser()
DEFAULT_CLIENT_SECRETS_PATH = Path("~/.ai_influencer_studio/gdrive_client_secrets.json").expanduser()

try:  # optional dependency (browser extra)
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - exercised only when playwright is absent
    sync_playwright = None  # type: ignore[assignment]

try:  # optional dependency for the Drive API backend
    from google.oauth2.credentials import Credentials as GDriveCredentials
    from googleapiclient.discovery import build as gdrive_build
except ImportError:  # pragma: no cover - exercised only when google client absent
    GDriveCredentials = None  # type: ignore[assignment,misc]
    gdrive_build = None  # type: ignore[assignment]


def _md5(path: Path) -> str:
    """Compute the content md5 of a file in chunks (safe for large media)."""
    digest = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_screenshot_name(name: str) -> bool:
    """True when the filename looks like a screenshot (Windows/Phone convention)."""
    return any(pattern.search(name) for pattern in SCREENSHOT_NAME_PATTERNS)


def is_eligible(path: Path, *, now: datetime | None = None) -> tuple[bool, str]:
    """Apply the refdrive filter policy to a single file.

    Returns ``(eligible, reason)`` where reason is empty when eligible.
    """
    if not path.is_file():
        return False, "not a file"
    ext = path.suffix.lower()
    if ext in BANNED_EXTS:
        return False, f"banned extension {ext}"
    if ext not in SUPPORTED_EXTS:
        return False, f"unsupported extension {ext}"
    try:
        size = path.stat().st_size
    except OSError as exc:
        return False, f"cannot stat: {exc}"
    if size < MIN_BYTES:
        return False, f"below 250 KB ({size} bytes)"
    if size > MAX_BYTES:
        return False, f"above 15 MB ({size} bytes)"
    if is_screenshot_name(path.name):
        now = now or datetime.now(UTC)
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        except (OSError, OverflowError, ValueError):
            return True, ""
        age_days = (now - mtime).total_seconds() / 86400
        if age_days > SCREENSHOT_MAX_AGE_DAYS:
            return False, f"screenshot older than {SCREENSHOT_MAX_AGE_DAYS} days"
    return True, ""


@dataclass
class UploadState:
    """Persisted pending + done lists keyed by content md5."""

    folder_id: str = DEFAULT_FOLDER_ID
    folder_url: str = DEFAULT_FOLDER_URL
    updated_at: str = ""
    pending: list[dict[str, Any]] = field(default_factory=list)
    done: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> UploadState:
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now(UTC).isoformat()
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @property
    def done_md5s(self) -> set[str]:
        return {item["md5"] for item in self.done}

    def is_done(self, md5: str) -> bool:
        return md5 in self.done_md5s


def scan_source_dirs(source_dirs: Iterable[Path | str], *, now: datetime | None = None) -> list[dict[str, Any]]:
    """Recursively scan directories for eligible media, deduped by content md5.

    Returns a list of candidate dicts: ``{path, md5, size, kind, is_screenshot}``.
    """
    seen: dict[str, dict[str, Any]] = {}
    for source in source_dirs:
        root = Path(source)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            eligible, reason = is_eligible(path, now=now)
            if not eligible:
                continue
            try:
                md5 = _md5(path)
            except OSError:
                continue
            # First path seen wins; identical content is never re-added.
            if md5 in seen:
                continue
            ext = path.suffix.lower()
            seen[md5] = {
                "path": str(path),
                "md5": md5,
                "size": path.stat().st_size,
                "kind": "video" if ext in VIDEO_EXTS else "image",
                "is_screenshot": is_screenshot_name(path.name),
            }
    # Stable order by path for reproducible batches.
    return sorted(seen.values(), key=lambda item: item["path"])


def _folder_id_from_url(folder_url: str) -> str:
    """Extract the Drive folder id embedded in a folders/ URL."""
    match = re.search(r"folders/([A-Za-z0-9_-]+)", folder_url)
    return match.group(1) if match else DEFAULT_FOLDER_ID


class GDriveUploader:
    """Collect, dedupe, and slowly upload reference media to a shared Drive folder."""

    def __init__(
        self,
        state_path: Path,
        folder_url: str | None = None,
        user_data_dir: str | None = None,
        cdp_url: str | None = None,
        token_path: Path | None = None,
        client_secrets_path: Path | None = None,
        rclone_remote: str | None = None,
        rclone_path: str = "refmedia",
    ) -> None:
        self.state_path = Path(state_path)
        self.state = UploadState.load(self.state_path)
        if folder_url:
            self.state.folder_url = folder_url
        if not self.state.folder_id:
            self.state.folder_id = _folder_id_from_url(self.state.folder_url)
        self.user_data_dir = user_data_dir or PLAYWRIGHT_CONTEXT_DIR
        self.cdp_url = cdp_url
        self.token_path = Path(token_path) if token_path else DEFAULT_TOKEN_PATH
        self.client_secrets_path = Path(client_secrets_path) if client_secrets_path else DEFAULT_CLIENT_SECRETS_PATH
        self.rclone_remote = rclone_remote or ""
        self.rclone_path = rclone_path or "refmedia"

    # -- Drive API auth ------------------------------------------------------

    def _drive_credentials(self) -> Any:
        """Return valid Drive OAuth2 credentials, running the one-time OAuth flow if needed."""
        if GDriveCredentials is None:
            raise RuntimeError(
                "Drive API backend needs google-auth + google-api-python-client; "
                "run 'pip install google-auth google-auth-oauthlib google-api-python-client'"
            )
        from google.auth.transport.requests import Request as GAuthRequest
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if self.token_path.exists():
            creds = GDriveCredentials.from_authorized_user_file(str(self.token_path), DRIVE_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(GAuthRequest())
                except Exception:
                    creds = None
            if not creds or not creds.valid:
                if not self.client_secrets_path.exists():
                    raise RuntimeError(
                        f"Drive API OAuth client secrets not found: {self.client_secrets_path} — "
                        "download a Google Cloud OAuth Desktop client JSON and save it there"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(self.client_secrets_path), DRIVE_SCOPES)
                creds = flow.run_local_server(port=0)
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def _drive_service(self) -> Any:
        """Build an authenticated Drive v3 service object."""
        return gdrive_build("drive", "v3", credentials=self._drive_credentials(), cache_discovery=False)

    # -- collection ----------------------------------------------------------

    def collect(self, source_dirs: Iterable[Path | str], *, now: datetime | None = None) -> dict[str, Any]:
        """Scan sources, filter, dedupe by content, and refresh the pending list.

        Files already in the done list (by md5) are skipped. Pending entries
        whose source file no longer exists are dropped. Existing pending
        entries are preserved.
        """
        candidates = scan_source_dirs(source_dirs, now=now)
        done_md5s = self.state.done_md5s

        existing = {item["md5"]: item for item in self.state.pending}
        merged: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            if candidate["md5"] in done_md5s:
                continue
            merged[candidate["md5"]] = existing.get(candidate["md5"], candidate)

        self.state.pending = sorted(merged.values(), key=lambda item: item["path"])
        self.state.save(self.state_path)
        return {
            "scanned": len(candidates),
            "already_done": len([c for c in candidates if c["md5"] in done_md5s]),
            "pending": len(self.state.pending),
            "done": len(self.state.done),
            "state_path": str(self.state_path),
        }

    # -- status --------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        pending_bytes = sum(item.get("size", 0) for item in self.state.pending)
        return {
            "folder_url": self.state.folder_url,
            "pending": len(self.state.pending),
            "pending_bytes": pending_bytes,
            "pending_mb": round(pending_bytes / 1e6, 1),
            "done": len(self.state.done),
            "state_path": str(self.state_path),
            "updated_at": self.state.updated_at,
        }

    # -- upload --------------------------------------------------------------

    def upload_pending(
        self,
        *,
        batch_size: int = 20,
        delay_seconds: float = 45.0,
        headless: bool = True,
        max_batches: int | None = None,
        user_data_dir: str | None = None,
        cdp_url: str | None = None,
        stop_event: threading.Event | None = None,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
        backend: str = "browser",
    ) -> dict[str, Any]:
        """Upload pending files, marking each done; ``backend`` picks the transport.

        ``backend="browser"`` drives the Drive web UI via Playwright in small
        paced batches (``delay_seconds`` paces batches for slow connections;
        ``user_data_dir``/``cdp_url`` pick the Chrome session).
        ``backend="drive_api"`` uploads directly through the Drive API using
        OAuth2 credentials (no browser, resumable per-file uploads; see
        ``upload_pending_via_api``).

        On any exception a file/batch stays pending and is retried on the next
        run. The done list is append-only, so content is never uploaded twice
        even if a re-run is restarted mid-batch. ``stop_event`` requests a
        graceful stop at the next boundary; ``on_progress`` is invoked with a
        snapshot dict after each unit of work.
        """
        if backend == "drive_api":
            return self.upload_pending_via_api(
                batch_size=batch_size,
                delay_seconds=delay_seconds,
                max_batches=max_batches,
                stop_event=stop_event,
                on_progress=on_progress,
            )
        if backend == "rclone":
            return self.upload_pending_via_rclone(
                batch_size=batch_size,
                delay_seconds=delay_seconds,
                max_batches=max_batches,
                stop_event=stop_event,
                on_progress=on_progress,
            )
        return self._upload_pending_browser(
            batch_size=batch_size,
            delay_seconds=delay_seconds,
            headless=headless,
            max_batches=max_batches,
            user_data_dir=user_data_dir,
            cdp_url=cdp_url,
            stop_event=stop_event,
            on_progress=on_progress,
        )

    def _upload_pending_browser(
        self,
        *,
        batch_size: int,
        delay_seconds: float,
        headless: bool,
        max_batches: int | None,
        user_data_dir: str | None,
        cdp_url: str | None,
        stop_event: threading.Event | None,
        on_progress: Callable[[dict[str, Any]], None] | None,
    ) -> dict[str, Any]:
        """Playwright web-UI upload path (kept for signed-in profiles / CDP)."""
        if not self.state.pending:
            return {"status": "nothing_pending", "uploaded": 0, "batch_count": 0}

        if sync_playwright is None:
            raise RuntimeError("playwright is not installed; run 'pip install playwright' and 'playwright install chromium'")

        upload_dir = user_data_dir or self.user_data_dir
        upload_cdp = cdp_url or self.cdp_url
        total_pending = len(self.state.pending)
        uploaded: list[str] = []
        batch_count = 0

        def _progress() -> None:
            if on_progress is not None:
                on_progress(
                    {
                        "batch_count": batch_count,
                        "uploaded": len(uploaded),
                        "total": total_pending,
                        "remaining_pending": len(self.state.pending),
                        "done": len(self.state.done),
                    }
                )

        with sync_playwright() as p:
            browser = None
            context = None
            if upload_cdp:
                browser = p.chromium.connect_over_cdp(upload_cdp)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.new_page()
            else:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=upload_dir,
                    headless=headless,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                )
                page = context.new_page()
            page.set_viewport_size({"width": 1400, "height": 900})
            page.goto(self.state.folder_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            pending = list(self.state.pending)
            while pending:
                if stop_event is not None and stop_event.is_set():
                    break
                batch = pending[:batch_size]
                pending = pending[batch_size:]
                batch_count += 1
                print(f"[*] Uploading batch {batch_count} ({len(batch)} files)...", flush=True)
                try:
                    self._upload_batch(page, [item["path"] for item in batch])
                    # Drive needs time to process; add each file to the append-only done list.
                    for item in batch:
                        self.state.done.append(
                            {
                                "path": item["path"],
                                "md5": item["md5"],
                                "size": item.get("size", 0),
                                "kind": item.get("kind", ""),
                                "uploaded_at": datetime.now(UTC).isoformat(),
                            }
                        )
                        uploaded.append(item["path"])
                    self.state.pending = [
                        item for item in self.state.pending if item["md5"] not in {b["md5"] for b in batch}
                    ]
                    self.state.save(self.state_path)
                    _progress()
                except Exception as exc:  # keep the batch pending for retry
                    print(f"[!] Batch {batch_count} failed, keeping pending: {exc}", flush=True)
                    _progress()
                if pending and delay_seconds > 0 and not (stop_event is not None and stop_event.is_set()):
                    time.sleep(delay_seconds)
                if max_batches is not None and batch_count >= max_batches:
                    break
            if browser is not None:
                page.close()
            else:
                context.close()

        if stop_event is not None and stop_event.is_set() and self.state.pending:
            status = "stopped"
        else:
            status = "done" if not self.state.pending else "partial"
        return {
            "status": status,
            "uploaded": len(uploaded),
            "batch_count": batch_count,
            "remaining_pending": len(self.state.pending),
        }

    def upload_pending_via_api(
        self,
        *,
        batch_size: int = 20,
        delay_seconds: float = 45.0,
        max_batches: int | None = None,
        stop_event: threading.Event | None = None,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """Upload pending files through the Drive API (no browser, resumable).

        Each file is uploaded with a resumable ``MediaFileUpload`` and marked
        done immediately on success, so an interrupted run only re-attempts
        files that never completed. Uses the shared folder id from the state.
        """
        if not self.state.pending:
            return {"status": "nothing_pending", "uploaded": 0, "batch_count": 0}
        if GDriveCredentials is None or gdrive_build is None:
            raise RuntimeError(
                "Drive API backend needs google-auth + google-api-python-client; "
                "run 'pip install google-auth google-auth-oauthlib google-api-python-client'"
            )

        from googleapiclient.http import MediaFileUpload

        service = self._drive_service()
        total_pending = len(self.state.pending)
        uploaded: list[str] = []
        batch_count = 0
        failed: list[str] = []

        def _progress() -> None:
            if on_progress is not None:
                on_progress(
                    {
                        "batch_count": batch_count,
                        "uploaded": len(uploaded),
                        "failed": len(failed),
                        "total": total_pending,
                        "remaining_pending": len(self.state.pending),
                        "done": len(self.state.done),
                    }
                )

        pending = list(self.state.pending)
        while pending:
            if stop_event is not None and stop_event.is_set():
                break
            batch = pending[:batch_size]
            pending = pending[batch_size:]
            batch_count += 1
            print(f"[*] Drive API batch {batch_count} ({len(batch)} files)...", flush=True)
            for item in batch:
                if stop_event is not None and stop_event.is_set():
                    break
                path = Path(item["path"])
                if not path.exists():
                    failed.append(item["path"])
                    print(f"[!] Source gone, skipping: {path}", flush=True)
                    continue
                try:
                    media = MediaFileUpload(
                        str(path),
                        mimetype="video/mp4" if item.get("kind") == "video" else "image/jpeg",
                        resumable=True,
                        chunksize=1024 * 1024,
                    )
                    request = service.files().create(
                        body={"name": path.name, "parents": [self.state.folder_id]},
                        media_body=media,
                        fields="id,name",
                    )
                    response = None
                    while response is None:
                        _, response = request.next_chunk()
                    # Success: move to the append-only done list by content md5.
                    self.state.done.append(
                        {
                            "path": item["path"],
                            "md5": item["md5"],
                            "size": item.get("size", 0),
                            "kind": item.get("kind", ""),
                            "drive_file_id": response.get("id"),
                            "uploaded_at": datetime.now(UTC).isoformat(),
                        }
                    )
                    uploaded.append(item["path"])
                    self.state.pending = [x for x in self.state.pending if x["md5"] != item["md5"]]
                    self.state.save(self.state_path)
                    _progress()
                except Exception as exc:  # keep this file pending for retry
                    failed.append(item["path"])
                    print(f"[!] File upload failed, keeping pending: {path.name}: {exc}", flush=True)
                    _progress()
            if pending and delay_seconds > 0 and not (stop_event is not None and stop_event.is_set()):
                time.sleep(delay_seconds)
            if max_batches is not None and batch_count >= max_batches:
                break

        if stop_event is not None and stop_event.is_set() and self.state.pending:
            status = "stopped"
        else:
            status = "done" if not self.state.pending else "partial"
        return {
            "status": status,
            "uploaded": len(uploaded),
            "failed": len(failed),
            "batch_count": batch_count,
            "remaining_pending": len(self.state.pending),
        }

    def upload_pending_via_rclone(
        self,
        *,
        batch_size: int = 20,
        delay_seconds: float = 45.0,
        max_batches: int | None = None,
        stop_event: threading.Event | None = None,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """Upload pending files through the rclone CLI (checksum-aware, no browser).

        Requires ``rclone`` on PATH with a Google Drive remote configured once
        via ``rclone config`` (e.g. ``gdrive:`` pointing at the account that
        owns the shared folder). Each file is copied with
        ``rclone copyto --checksum`` into ``<remote>:<path>/``; a file is moved
        to the append-only done list only when its copy exits 0, so an
        interrupted run resumes without re-uploading identical content (rclone
        skips files whose remote checksum already matches).
        """
        if not self.state.pending:
            return {"status": "nothing_pending", "uploaded": 0, "batch_count": 0}
        if not self.rclone_remote:
            raise RuntimeError(
                "rclone backend needs a configured remote; set gdrive_rclone_remote "
                "to e.g. 'gdrive:' and run 'rclone config' once"
            )
        executable = shutil.which("rclone")
        if not executable:
            raise RuntimeError(
                "rclone is not installed; install it (e.g. 'winget install Rclone.Rclone') "
                "and run 'rclone config' to authorize the Google Drive remote"
            )

        total_pending = len(self.state.pending)
        uploaded: list[str] = []
        batch_count = 0
        failed: list[str] = []
        remote_dir = f"{self.rclone_remote.rstrip('/')}/{self.rclone_path.lstrip('/')}"

        def _progress() -> None:
            if on_progress is not None:
                on_progress(
                    {
                        "batch_count": batch_count,
                        "uploaded": len(uploaded),
                        "failed": len(failed),
                        "total": total_pending,
                        "remaining_pending": len(self.state.pending),
                        "done": len(self.state.done),
                    }
                )

        pending = list(self.state.pending)
        while pending:
            if stop_event is not None and stop_event.is_set():
                break
            batch = pending[:batch_size]
            pending = pending[batch_size:]
            batch_count += 1
            print(f"[*] rclone batch {batch_count} ({len(batch)} files)...", flush=True)
            for item in batch:
                if stop_event is not None and stop_event.is_set():
                    break
                path = Path(item["path"])
                if not path.exists():
                    failed.append(item["path"])
                    print(f"[!] Source gone, skipping: {path}", flush=True)
                    continue
                try:
                    result = subprocess.run(
                        [executable, "copyto", str(path), f"{remote_dir}/{path.name}", "--checksum"],
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )
                    if result.returncode != 0:
                        raise RuntimeError(result.stderr.strip() or f"rclone exited with {result.returncode}")
                    self.state.done.append(
                        {
                            "path": item["path"],
                            "md5": item["md5"],
                            "size": item.get("size", 0),
                            "kind": item.get("kind", ""),
                            "remote": f"{remote_dir}/{path.name}",
                            "uploaded_at": datetime.now(UTC).isoformat(),
                        }
                    )
                    uploaded.append(item["path"])
                    self.state.pending = [x for x in self.state.pending if x["md5"] != item["md5"]]
                    self.state.save(self.state_path)
                    _progress()
                except Exception as exc:  # keep this file pending for retry
                    failed.append(item["path"])
                    print(f"[!] File upload failed, keeping pending: {path.name}: {exc}", flush=True)
                    _progress()
            if pending and delay_seconds > 0 and not (stop_event is not None and stop_event.is_set()):
                time.sleep(delay_seconds)
            if max_batches is not None and batch_count >= max_batches:
                break

        if stop_event is not None and stop_event.is_set() and self.state.pending:
            status = "stopped"
        else:
            status = "done" if not self.state.pending else "partial"
        return {
            "status": status,
            "uploaded": len(uploaded),
            "failed": len(failed),
            "batch_count": batch_count,
            "remaining_pending": len(self.state.pending),
        }

    @staticmethod
    def _upload_batch(page: Any, paths: list[str]) -> None:
        """Set files on the Drive file input; raise on failure so the batch retries."""
        file_inputs = page.locator('input[type="file"]').all()
        if file_inputs:
            file_inputs[0].set_input_files(paths)
            time.sleep(15)
            return
        # Fall back to the '+ New' -> 'File upload' menu flow.
        new_btn = page.locator('button:has-text("New"), [aria-label*="New"], [data-tooltip*="New"]').first
        if new_btn.is_visible():
            new_btn.click()
            time.sleep(2)
            with page.expect_file_chooser() as fc_info:
                page.locator('text="File upload"').first.click()
            file_chooser = fc_info.value
            file_chooser.set_files(paths)
            time.sleep(15)
            return
        raise RuntimeError("no file input or '+ New' upload control found on Drive")
