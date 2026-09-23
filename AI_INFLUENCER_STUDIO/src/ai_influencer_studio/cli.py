"""CLI entry point for AI Influencer Studio."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine

from ai_influencer_studio.adapters.video import VideoAdapter
from ai_influencer_studio.config import StudioConfig
from ai_influencer_studio.model_registry import ModelRegistry, _snapshot_is_fresh
from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine
from ai_influencer_studio.repurposer import VideoRepurposer


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def cmd_config(args: argparse.Namespace) -> int:
    """Open or create the studio configuration file."""
    config = StudioConfig.from_file()
    config.save()
    print(f"Configuration saved to: {config.data_dir / 'config.json'}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    """Generate content using the legacy pipeline."""
    config = StudioConfig.from_file()
    content_type = args.type
    topic = args.topic

    if content_type in {"post", "caption", "blog", "video_script"}:
        from ai_influencer_studio.adapters.content import ContentAdapter

        adapter = ContentAdapter(config)
        if content_type == "post":
            result = adapter.generate_post(topic, args.platform)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif content_type == "caption":
            print(adapter.generate_caption(topic, args.platform))
        elif content_type == "blog":
            print(adapter.generate_blog(topic, args.word_count))
        elif content_type == "video_script":
            print(adapter.generate_video_script(topic, args.duration))
    elif content_type == "talking_head":
        from ai_influencer_studio.adapters.video import VideoAdapter

        adapter = VideoAdapter(config)
        result = adapter.generate_talking_head_short(topic)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif content_type == "social_video":
        from ai_influencer_studio.adapters.video import VideoAdapter

        adapter = VideoAdapter(config)
        result = adapter.generate_social_video(topic, args.platform, args.style)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif content_type == "music_video":
        if not args.audio:
            print("--audio is required for music_video", file=sys.stderr)
            return 1
        from ai_influencer_studio.adapters.video import VideoAdapter

        adapter = VideoAdapter(config)
        result = adapter.generate_music_video(
            args.audio,
            genre=args.genre,
            mood=args.mood,
            platforms=args.platforms,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown content type: {content_type}", file=sys.stderr)
        return 1

    return 0


def cmd_schedule(args: argparse.Namespace) -> int:
    """Schedule a post for later publishing."""
    from ai_influencer_studio.adapters.automation import AutomationAdapter

    config = StudioConfig.from_file()
    adapter = AutomationAdapter(config)
    scheduled_at = datetime.fromisoformat(args.when)
    post_id = adapter.schedule_post(
        platform=args.platform,
        content=args.content,
        scheduled_at=scheduled_at,
        media_paths=args.media_paths,
        hashtags=args.hashtags,
    )
    print(f"Scheduled post {post_id} for {scheduled_at}")
    return 0


def cmd_schedule_list(args: argparse.Namespace) -> int:
    """List scheduled posts."""
    from ai_influencer_studio.adapters.automation import AutomationAdapter

    config = StudioConfig.from_file()
    adapter = AutomationAdapter(config)
    posts = adapter.list_scheduled_posts()
    if not posts:
        print("No scheduled posts.")
        return 0

    for post in posts:
        status = "POSTED" if post.status == "posted" else "PENDING"
        print(
            f"[{status}] {post.id}: {post.platform} @ {post.scheduled_at} "
            f"- {post.content[:60]}..."
        )
    return 0


def cmd_daemon(args: argparse.Namespace) -> int:
    """Run the background publishing scheduler."""
    _setup_logging()
    from ai_influencer_studio.core.scheduler import PublishScheduler

    config = StudioConfig.from_file()
    scheduler = PublishScheduler(config, poll_interval=args.interval)
    scheduler.start()
    print("Scheduler running. Press Ctrl+C to stop.")
    try:
        while scheduler.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nScheduler stopped.")
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    """Launch the web dashboard."""
    import uvicorn

    from ai_influencer_studio.web.app import app as web_app

    uvicorn.run(web_app, host=args.host, port=args.port)
    return 0


def cmd_model_registry_refresh(args: argparse.Namespace) -> int:
    """Refresh live Ollama/OpenRouter model metadata and emit LiteLLM config."""
    config = StudioConfig.from_file()
    registry = ModelRegistry(
        ollama_url=args.ollama_url,
        openrouter_url=args.openrouter_url,
        openrouter_api_key=config.openrouter_api_key or None,
    )
    snapshot_path = Path(args.snapshot) if args.snapshot else config.data_dir / "model_registry.json"
    if args.daily:
        try:
            snapshot = registry.refresh_daily(
                snapshot_path,
                force=args.force,
                include_ollama=not args.no_ollama,
                include_openrouter=not args.no_openrouter,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Unable to refresh daily registry: {exc}", file=sys.stderr)
            return 1
    else:
        try:
            previous = ModelRegistry.load_snapshot(snapshot_path) if snapshot_path.exists() else None
            snapshot = registry.refresh(
                include_ollama=not args.no_ollama,
                include_openrouter=not args.no_openrouter,
                previous_snapshot=previous,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Unable to refresh registry from existing snapshot: {exc}", file=sys.stderr)
            return 1
        registry.save_snapshot(snapshot, snapshot_path)
    litellm_path = Path(args.litellm_config) if args.litellm_config else config.data_dir / "litellm.generated.yaml"
    registry.emit_litellm_config(snapshot, litellm_path, ollama_url=registry.ollama_url)
    print(json.dumps({
        "checked_at": snapshot.checked_at,
        "fresh_until": snapshot.fresh_until,
        "verification_status": snapshot.verification_status,
        "verified": snapshot.verified,
        "provider_status": snapshot.provider_status,
        "models": len(snapshot.models),
        "errors": snapshot.errors,
        "aliases": snapshot.aliases,
        "snapshot": str(snapshot_path),
        "litellm_config": str(litellm_path),
    }, indent=2))
    return 0 if snapshot.models or not snapshot.errors else 1


def cmd_model_registry_status(args: argparse.Namespace) -> int:
    """Print freshness and verification status without network access."""
    config = StudioConfig.from_file()
    path = Path(args.snapshot) if args.snapshot else config.data_dir / "model_registry.json"
    try:
        snapshot = ModelRegistry.load_snapshot(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid registry snapshot: {exc}", file=sys.stderr)
        return 1
    fresh = _snapshot_is_fresh(snapshot)
    print(json.dumps({
        "snapshot": str(path),
        "checked_at": snapshot.checked_at,
        "fresh_until": snapshot.fresh_until,
        "fresh": fresh,
        "verification_status": snapshot.verification_status,
        "verified": snapshot.verified,
        "provider_status": snapshot.provider_status,
        "models": len(snapshot.models),
        "errors": snapshot.errors,
    }, indent=2))
    return 0


def cmd_model_registry_probe(args: argparse.Namespace) -> int:
    """Probe selected local models without changing catalog availability."""
    config = StudioConfig.from_file()
    snapshot_path = Path(args.snapshot) if args.snapshot else config.data_dir / "model_registry.json"
    try:
        snapshot = ModelRegistry.load_snapshot(snapshot_path)
        refs = set(args.model_ref or [])
        registry = ModelRegistry(
            ollama_url=args.ollama_url,
            openrouter_url=args.openrouter_url,
            openrouter_api_key=config.openrouter_api_key or None,
        )
        probed = registry.probe_health(
            snapshot,
            model_refs=refs or None,
            limit=args.limit,
            include_hosted=args.include_hosted,
        )
        ModelRegistry.save_snapshot(probed, snapshot_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Unable to probe model health: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "snapshot": str(snapshot_path),
        "probed": [
            {
                "provider": model.provider,
                "model_id": model.model_id,
                "health_status": model.health_status,
                "health_checked_at": model.health_checked_at,
                "health_latency_ms": model.health_latency_ms,
                "health_error": model.health_error,
            }
            for model in probed.models if model.health_checked_at
        ],
        "catalog_availability_unchanged": True,
    }, indent=2))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Report dependency availability without installing or changing anything."""
    required = [
        "fastapi", "uvicorn", "jinja2", "pydantic", "requests", "python-multipart", "schedule",
        "Pillow", "openai", "librosa", "mutagen",
    ]
    optional = ["playwright", "pypdf", "python-docx", "uiautomation", "mcp"]
    report: dict[str, Any] = {"python": sys.version.split()[0], "required": {}, "optional": {}}
    for package in required + optional:
        import_targets = {
            "python-multipart": "multipart",
            "python-docx": "docx",
            "Pillow": "PIL",
        }
        target = import_targets.get(package, package.replace("-", "_"))
        try:
            version = importlib.metadata.version(package)
            importlib.import_module(target)
            state = {"installed": True, "version": version, "importable": True}
        except (importlib.metadata.PackageNotFoundError, ImportError, ModuleNotFoundError) as exc:
            state = {"installed": False, "importable": False, "error": type(exc).__name__}
        (report["required"] if package in required else report["optional"])[package] = state
    report["status"] = "ok" if all(item.get("importable") for item in report["required"].values()) else "dependency_issue"
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ok" else 1


def cmd_health(args: argparse.Namespace) -> int:
    """Print local operational health without contacting providers."""
    config = StudioConfig.from_file()
    snapshot_path = config.data_dir / "model_registry.json"
    report: dict[str, Any] = {
        "data_dir": str(config.data_dir),
        "data_dir_exists": config.data_dir.exists(),
        "model_snapshot": str(snapshot_path),
        "model_snapshot_exists": snapshot_path.exists(),
        "scheduler_database": str(config.data_dir / "studio.db"),
        "indexer_database": str(config.data_dir / "file_indexer.sqlite"),
    }
    if snapshot_path.exists():
        try:
            snapshot = ModelRegistry.load_snapshot(snapshot_path)
            report.update({
                "catalog_fresh": _snapshot_is_fresh(snapshot),
                "catalog_verification": snapshot.verification_status,
                "provider_status": snapshot.provider_status,
                "model_count": len(snapshot.models),
                "healthy_models": sum(model.health_status == "healthy" for model in snapshot.models),
                "unhealthy_models": sum(model.health_status == "unhealthy" for model in snapshot.models),
            })
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            report["catalog_error"] = str(exc)
    print(json.dumps(report, indent=2))
    return 0


def cmd_model_registry_export_docs(args: argparse.Namespace) -> int:
    """Export an offline Markdown report from a saved registry snapshot."""
    config = StudioConfig.from_file()
    snapshot_path = Path(args.snapshot) if args.snapshot else config.data_dir / "model_registry.json"
    output_path = Path(args.output) if args.output else config.data_dir / "model_registry_report.md"
    try:
        snapshot = ModelRegistry.load_snapshot(snapshot_path)
        ModelRegistry.export_catalog_markdown(snapshot, output_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Unable to export registry report: {exc}", file=sys.stderr)
        return 1
    print(f"Model registry report written to: {output_path}")
    return 0


def cmd_model_registry_list(args: argparse.Namespace) -> int:
    """Print a previously saved model registry snapshot."""
    config = StudioConfig.from_file()
    path = Path(args.snapshot) if args.snapshot else config.data_dir / "model_registry.json"
    if not path.exists():
        print(f"Registry snapshot not found: {path}", file=sys.stderr)
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Invalid registry snapshot: {exc}", file=sys.stderr)
        return 1
    if not _valid_registry_snapshot(data):
        print(f"Invalid registry snapshot structure: {path}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(f"Checked: {data.get('checked_at', 'unknown')}")
    for model in data.get("models", []):
        price = model.get("cost_class", "unknown")
        modalities = ",".join(model.get("input_modalities", []))
        print(f"{model.get('provider', '?'):10} {model.get('model_id', '?')} [{price}; input={modalities}]")
    print("\nAliases:")
    for alias, models in data.get("aliases", {}).items():
        print(f"  {alias}: {', '.join(models) if models else '(none)'}")
    if data.get("errors"):
        print("\nProvider errors:")
        for error in data["errors"]:
            print(f"  {error.get('provider')}: {error.get('error')}")
    return 0


def _valid_registry_snapshot(data: Any) -> bool:
    """Validate the JSON shape needed by the registry listing command."""
    if not isinstance(data, dict) or not {"models", "aliases", "errors"}.issubset(data):
        return False
    if not isinstance(data["models"], list) or not isinstance(data["aliases"], dict) or not isinstance(data["errors"], list):
        return False
    for model in data["models"]:
        if not isinstance(model, dict):
            return False
        if not isinstance(model.get("provider"), str) or not isinstance(model.get("model_id"), str):
            return False
        if not isinstance(model.get("cost_class"), str):
            return False
        if not isinstance(model.get("input_modalities"), list) or not all(
            isinstance(modality, str) for modality in model["input_modalities"]
        ):
            return False
    for error in data["errors"]:
        if not isinstance(error, dict) or not isinstance(error.get("provider"), str) or not isinstance(error.get("error"), str):
            return False
    return all(
        isinstance(alias, str)
        and isinstance(models, list)
        and all(isinstance(model_ref, str) for model_ref in models)
        for alias, models in data["aliases"].items()
    )


def _safe_use_engine(args: argparse.Namespace):
    """Build the isolated safe-use engine from explicit CLI policy flags."""
    from ai_influencer_studio.safe_use.browser import PlaywrightBrowser
    from ai_influencer_studio.safe_use.engine import SafeUseEngine
    from ai_influencer_studio.safe_use.policy import SafePolicy

    config = StudioConfig.from_file()
    policy = SafePolicy(
        allowed_domains={item.strip() for item in args.domain if item.strip()},
        allowed_apps={item.strip() for item in args.app if item.strip()},
        allow_sensitive_fields=bool(args.allow_sensitive_fields),
    )
    browser = None
    if args.target == "browser":
        browser = PlaywrightBrowser(headless=not args.headed, screenshot_dir=config.data_dir / "safe-use-screenshots")
    return SafeUseEngine(policy=policy, audit_path=config.data_dir / "safe-use-audit.jsonl", browser=browser)


def _safe_intent(raw: str):
    """Parse a JSON action intent from the CLI."""
    from ai_influencer_studio.safe_use.models import ActionIntent, ActionTarget

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--intent must be valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("--intent must be a JSON object")
    try:
        return ActionIntent(
            target=ActionTarget(str(payload["target"])),
            action=str(payload["action"]),
            parameters=dict(payload.get("parameters", {})),
            reason=str(payload.get("reason", "")),
            requested_by=str(payload.get("requested_by", "operator")),
            intent_id=str(payload.get("intent_id", "")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("--intent requires target, action, and an object-valued parameters field") from exc


def cmd_safe_use_observe(args: argparse.Namespace) -> int:
    """Observe an allowlisted browser page or Windows application."""
    engine = _safe_use_engine(args)
    try:
        parameters: dict[str, Any]
        if args.target == "browser":
            parameters = {"url": args.url, "selector": args.selector, "max_chars": args.max_chars, "screenshot": args.screenshot}
        else:
            parameters = {"app": args.app_name, "max_depth": args.max_depth, "screenshot": args.screenshot}
        result = engine.observe(args.target, **{key: value for key, value in parameters.items() if value is not None})
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    finally:
        engine.close()


def cmd_safe_use_propose(args: argparse.Namespace) -> int:
    """Validate an action and print its approval-ready intent."""
    engine = _safe_use_engine(args)
    try:
        result = engine.propose(_safe_intent(args.intent))
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    finally:
        engine.close()


def cmd_safe_use_execute(args: argparse.Namespace) -> int:
    """Execute exactly one validated action when explicit approval is supplied."""
    intent = _safe_intent(args.intent)
    if not args.approve:
        print("Refusing execution: pass --approve for mutating actions.", file=sys.stderr)
        return 2
    engine = _safe_use_engine(args)
    try:
        if args.target == "browser" and intent.action != "navigate" and intent.parameters.get("url"):
            engine.observe("browser", url=str(intent.parameters["url"]), selector="body", max_chars=1)
        approval = engine.approve(intent)
        result = engine.execute(intent, approval_token=approval.token)
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    finally:
        engine.close()


def cmd_safe_use_mcp_config(args: argparse.Namespace) -> int:
    """Write an isolated Playwright MCP client configuration."""
    from ai_influencer_studio.safe_use.mcp_config import write_playwright_mcp_config

    config = StudioConfig.from_file()
    path = Path(args.output) if args.output else config.data_dir / "playwright-mcp.json"
    try:
        write_playwright_mcp_config(
            path,
            headless=not args.headed,
            isolated=not args.persistent,
            allowed_domains=args.domain,
            allowed_apps=args.app,
            enable_windows=bool(args.app),
        )
    except ValueError as exc:
        print(f"Refusing unsafe MCP config: {exc}", file=sys.stderr)
        return 2
    print(f"Playwright MCP config written to: {path}")
    return 0


def cmd_agent_run(args: argparse.Namespace) -> int:
    """Run an autonomous multi-model browser/computer task (N models, vision, free)."""
    from ai_influencer_studio.safe_use.agent import MultiModelAgent, pick_free_vision_models
    from ai_influencer_studio.safe_use.browser import PlaywrightBrowser
    from ai_influencer_studio.safe_use.engine import SafeUseEngine
    from ai_influencer_studio.safe_use.multi_model import MultiModelClient
    from ai_influencer_studio.safe_use.policy import SafePolicy

    config = StudioConfig.from_file()
    models = list(args.models)
    if not models:
        snapshot_path = Path(args.snapshot) if args.snapshot else config.data_dir / "model_registry.json"
        try:
            snapshot = ModelRegistry.load_snapshot(snapshot_path)
            models = pick_free_vision_models(snapshot, limit=4)
        except (OSError, ValueError, json.JSONDecodeError):
            models = []
        if not models:
            print("No --models supplied and no free vision models found in the registry snapshot.", file=sys.stderr)
            return 1

    policy = SafePolicy(
        allowed_domains={item.strip() for item in args.domain if item.strip()},
        allowed_apps={item.strip() for item in args.allow_app if item.strip()},
        allow_sensitive_fields=bool(args.allow_sensitive_fields),
    )
    browser = None
    if args.target == "browser":
        browser = PlaywrightBrowser(headless=not args.headed, screenshot_dir=config.data_dir / "safe-use-screenshots")
    engine = SafeUseEngine(policy=policy, audit_path=config.data_dir / "safe-use-audit.jsonl", browser=browser)

    client = MultiModelClient(
        ollama_url=args.ollama_url,
        openrouter_api_key=config.openrouter_api_key or None,
    )
    agent = MultiModelAgent(
        engine,
        models=models,
        client=client,
        max_steps=args.max_steps,
        aggregator=args.aggregator or None,
    )
    try:
        result = agent.run_task(args.task, target=args.target, url=args.url, app=args.app_name)
    finally:
        engine.close()
    print(json.dumps({"models": models, **result}, indent=2))
    return 0 if result["status"] == "done" else 1


def _file_indexer(args: argparse.Namespace):
    """Build the local indexer with the configured audit log."""
    from ai_influencer_studio.file_indexer import LocalFileIndexer
    from ai_influencer_studio.safe_use.audit import AuditLogger

    config = StudioConfig.from_file()
    return LocalFileIndexer(config.data_dir / "file_indexer.sqlite", AuditLogger(config.data_dir / "file-indexer-audit.jsonl"))


def cmd_indexer_scan(args: argparse.Namespace) -> int:
    """Scan supported local files and populate the review queue without moving files."""
    indexer = _file_indexer(args)
    try:
        result = indexer.scan(Path(args.source), Path(args.target))
    except Exception as exc:
        print(f"Indexer scan failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


def cmd_indexer_queue(args: argparse.Namespace) -> int:
    """List persistent file-review queue records."""
    indexer = _file_indexer(args)
    statuses = set(args.status) if args.status else None
    records = [record.to_dict() for record in indexer.list_queue(statuses)]
    print(json.dumps({"count": len(records), "records": records}, indent=2))
    return 0


def cmd_indexer_approve(args: argparse.Namespace) -> int:
    """Approve pending records without applying filesystem changes."""
    indexer = _file_indexer(args)
    try:
        count = indexer.approve(record_ids=args.ids or None, approve_all=args.all)
    except Exception as exc:
        print(f"Indexer approval failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"approved": count}, indent=2))
    return 0


def cmd_indexer_reject(args: argparse.Namespace) -> int:
    """Reject pending records without applying filesystem changes."""
    indexer = _file_indexer(args)
    try:
        count = indexer.reject(record_ids=args.ids or None, reject_all=args.all)
    except Exception as exc:
        print(f"Indexer rejection failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"rejected": count}, indent=2))
    return 0


def cmd_indexer_apply(args: argparse.Namespace) -> int:
    """Apply approved queue records only with explicit confirmation."""
    if not args.confirm:
        print("Refusing apply: pass --confirm to copy, verify, and remove files.", file=sys.stderr)
        return 2
    indexer = _file_indexer(args)
    try:
        result = indexer.apply(
            record_ids=args.ids or None,
            confirm=True,
            source_root=Path(args.source) if args.source else None,
            target_root=Path(args.target) if args.target else None,
        )
    except Exception as exc:
        print(f"Indexer apply failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if not result["failed"] else 1


def cmd_music_video_research(args: argparse.Namespace) -> int:
    """Research free video generators and YouTube trends."""
    if not args.generators and not args.trends:
        print("Use --generators and/or --trends to request research output.", file=sys.stderr)
        return 1
    config = StudioConfig.from_file()
    engine = MusicVideoResearchEngine(
        data_dir=config.data_dir,
        youtube_api_key=config.youtube_api_key or None,
    )
    if args.generators:
        generators = engine.research_generators(vram_gb=args.vram)
        print(json.dumps({"generators": generators}, indent=2))
    if args.trends:
        trends = engine.fetch_youtube_trends(max_results=args.max_results)
        print(json.dumps({"trends": trends}, indent=2))
    return 0


def _parse_song_arg(raw: str) -> dict:
    try:
        song = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"--song must be valid JSON: {exc}") from exc
    if not isinstance(song, dict):
        raise argparse.ArgumentTypeError("--song must be a JSON object")
    required = {"name", "audio"}
    missing = required - song.keys()
    if missing:
        raise argparse.ArgumentTypeError(f"--song missing required keys: {missing}")
    return song


def _build_engine_from_args(args: argparse.Namespace) -> MusicVideoResearchEngine:
    """Create a MusicVideoResearchEngine and scan assets if requested."""
    config = StudioConfig.from_file()
    engine = MusicVideoResearchEngine(
        data_dir=config.data_dir,
        youtube_api_key=config.youtube_api_key or None,
    )
    if getattr(args, "assets_root", None):
        engine.scan_reusable_assets(Path(args.assets_root))
    if getattr(args, "staging_root", None):
        engine.scan_gdrive_staging(Path(args.staging_root))
    return engine


def cmd_gdrive_collect(args: argparse.Namespace) -> int:
    """Scan sources, filter, and dedupe by content into the pending list."""
    from ai_influencer_studio.gdrive_uploader import GDriveUploader

    config = StudioConfig.from_file()
    state_path = Path(args.state) if args.state else config.gdrive_state_path
    uploader = GDriveUploader(state_path, folder_url=config.gdrive_folder_url)
    result = uploader.collect(args.source)
    print(json.dumps(result, indent=2))
    return 0


def cmd_gdrive_status(args: argparse.Namespace) -> int:
    """Print pending/done counts from the upload state file."""
    from ai_influencer_studio.gdrive_uploader import GDriveUploader

    config = StudioConfig.from_file()
    state_path = Path(args.state) if args.state else config.gdrive_state_path
    uploader = GDriveUploader(state_path, folder_url=config.gdrive_folder_url)
    print(json.dumps(uploader.status(), indent=2))
    return 0


def cmd_gdrive_upload(args: argparse.Namespace) -> int:
    """Upload the pending list via the chosen backend (browser or Drive API)."""
    from ai_influencer_studio.gdrive_uploader import GDriveUploader

    config = StudioConfig.from_file()
    state_path = Path(args.state) if args.state else config.gdrive_state_path
    backend = args.backend or config.gdrive_backend
    if backend not in ("browser", "drive_api", "rclone"):
        print(f"Unknown backend: {backend} (expected browser, drive_api, or rclone)", file=sys.stderr)
        return 2
    uploader = GDriveUploader(
        state_path,
        folder_url=config.gdrive_folder_url,
        user_data_dir=args.user_data_dir or config.gdrive_chrome_user_data_dir or None,
        cdp_url=args.cdp_url or config.gdrive_cdp_url or None,
        token_path=config.gdrive_token_path,
        client_secrets_path=config.gdrive_client_secrets_path,
        rclone_remote=args.rclone_remote or config.gdrive_rclone_remote or None,
        rclone_path=args.rclone_path or config.gdrive_rclone_path,
    )
    try:
        result = uploader.upload_pending(
            batch_size=args.batch_size,
            delay_seconds=args.delay,
            headless=not args.headed,
            max_batches=args.max_batches,
            backend=backend,
        )
    except Exception as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") != "partial" or args.max_batches else 1


def _iter_songs(args: argparse.Namespace):
    """Yield parsed song dicts, handling malformed JSON gracefully."""
    try:
        for raw in args.song:
            yield _parse_song_arg(raw)
    except argparse.ArgumentTypeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


def _create_plans(engine: MusicVideoResearchEngine, args: argparse.Namespace) -> list[dict]:
    """Create SongPlan dicts from parsed CLI song arguments."""
    plans: list[dict] = []
    for song in _iter_songs(args):
        character_ref = song.get("character_ref") or getattr(args, "character_ref", None)
        generation_mode = song.get("generation_mode") or getattr(args, "generation_mode", "full")
        style_bible_path = song.get("style_bible") or getattr(args, "style_bible", None)
        plan_kwargs: dict[str, Any] = {
            "song_name": song["name"],
            "audio_path": song["audio"],
            "genre": song.get("genre", ""),
            "mood": song.get("mood", ""),
            "duration": song.get("duration", 180.0),
            "character_ref": character_ref,
            "generation_mode": generation_mode,
        }
        if style_bible_path:
            plan_kwargs["style_bible_path"] = style_bible_path
        plan = engine.create_song_plan(**plan_kwargs)
        plans.append(plan.to_dict())
    return plans


def cmd_music_video_style_bible_template(args: argparse.Namespace) -> int:
    """Create a starter JSON character/style bible without overwriting files."""
    from ai_influencer_studio.music_video_researcher import MusicVideoResearchEngine

    try:
        path = MusicVideoResearchEngine.create_style_bible_template(Path(args.output))
    except (FileExistsError, OSError) as exc:
        print(f"Unable to create style bible: {exc}", file=sys.stderr)
        return 1
    print(f"Style bible template written to: {path}")
    return 0


def cmd_music_video_plan(args: argparse.Namespace) -> int:
    """Create a reusable-clip-aware plan for one or more songs."""
    engine = _build_engine_from_args(args)
    plans = _create_plans(engine, args)
    print(json.dumps({"plans": plans}, indent=2))
    return 0


def cmd_music_video_master_plan(args: argparse.Namespace) -> int:
    """Generate and save a master music video plan."""
    engine = _build_engine_from_args(args)
    _create_plans(engine, args)
    path = engine.save_master_plan(Path(args.output) if args.output else None)
    print(f"Master plan saved to: {path}")
    return 0


def cmd_music_video_execute(args: argparse.Namespace) -> int:
    """Execute a saved music video plan through the ComfyUI orchestrator."""
    config = StudioConfig.from_file()
    adapter = VideoAdapter(config)
    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"Plan file not found: {plan_path}", file=sys.stderr)
        return 1
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    songs = plan.get("songs", [])
    if not songs:
        print("No songs found in plan.", file=sys.stderr)
        return 1
    index = args.song_index
    if index < 0 or index >= len(songs):
        print(f"Invalid song index: {index}", file=sys.stderr)
        return 1
    song_plan = songs[index]
    if args.generation_mode:
        song_plan["generation_mode"] = args.generation_mode
    result = adapter.execute_music_video_plan(song_plan, platforms=args.platforms)
    print(json.dumps(result, indent=2))
    return 0


def _load_plan_song(plan_path: str, song_index: int) -> dict:
    """Load a master plan JSON and return one song plan dict (or raise clearly)."""
    path = Path(plan_path)
    if not path.exists():
        raise ValueError(f"Plan file not found: {path}")
    plan = json.loads(path.read_text(encoding="utf-8"))
    songs = plan.get("songs", [])
    if not songs:
        raise ValueError("No songs found in plan.")
    if song_index < 0 or song_index >= len(songs):
        raise ValueError(f"Invalid song index: {song_index}")
    return songs[song_index]


def cmd_youtube_metadata(args: argparse.Namespace) -> int:
    """Preview YouTube metadata generated from a song plan (no network)."""
    from ai_influencer_studio.youtube_publish import build_metadata

    try:
        song = _load_plan_song(args.plan, args.song_index)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(build_metadata(song), indent=2))
    return 0


def cmd_youtube_upload(args: argparse.Namespace) -> int:
    """Upload a finished video using metadata generated from its song plan."""
    from ai_influencer_studio.youtube_publish import YouTubePublisher, save_publish_record

    config = StudioConfig.from_file()
    try:
        song = _load_plan_song(args.plan, args.song_index)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    video_path = args.video or Path(args.plan).with_suffix(".mp4")
    if not Path(video_path).exists():
        print(f"Video file not found: {video_path}", file=sys.stderr)
        return 1
    publisher = YouTubePublisher(
        token_path=config.youtube_token_path,
        client_secrets_path=config.youtube_client_secrets_path,
    )
    try:
        result = publisher.publish_song(
            song,
            video_path,
            thumbnail_path=args.thumbnail,
            privacy=args.privacy or config.youtube_default_privacy,
            category_id=args.category or config.youtube_category_id,
            playlist_ids=args.playlist or None,
            create_playlist_title=args.create_playlist or config.youtube_playlist_title or None,
        )
    except Exception as exc:
        print(f"Publish failed: {exc}", file=sys.stderr)
        return 1
    record_path = save_publish_record(result, config.data_dir / "youtube_publish.jsonl")
    print(json.dumps(result, indent=2))
    print(f"Publish record appended to: {record_path}")
    return 0


def cmd_youtube_upload_file(args: argparse.Namespace) -> int:
    """Upload any video file directly with explicit metadata."""
    from ai_influencer_studio.youtube_publish import YouTubePublisher

    config = StudioConfig.from_file()
    publisher = YouTubePublisher(
        token_path=config.youtube_token_path,
        client_secrets_path=config.youtube_client_secrets_path,
    )
    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()] if args.tags else None
    try:
        result = publisher.upload(
            args.video,
            title=args.title or Path(args.video).stem,
            description=args.description,
            tags=tags,
            category_id=args.category or config.youtube_category_id,
            privacy=args.privacy or config.youtube_default_privacy,
            thumbnail_path=args.thumbnail,
            playlist_ids=args.playlist or None,
        )
    except Exception as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


def cmd_youtube_channel_info(args: argparse.Namespace) -> int:
    """Show the authenticated channel's statistics."""
    from ai_influencer_studio.youtube_publish import YouTubePublisher

    config = StudioConfig.from_file()
    publisher = YouTubePublisher(
        token_path=config.youtube_token_path,
        client_secrets_path=config.youtube_client_secrets_path,
    )
    try:
        info = publisher.channel_info()
    except Exception as exc:
        print(f"Channel info failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(info, indent=2))
    return 0


def cmd_youtube_analytics(args: argparse.Namespace) -> int:
    """Fetch public channel stats + top videos via the YouTube Data API key."""
    from ai_influencer_studio.youtube_client import YouTubeDataClient

    config = StudioConfig.from_file()
    client = YouTubeDataClient(api_key=config.youtube_api_key or None)
    stats = client.fetch_channel_stats(args.channel_id)
    top_videos = client.fetch_top_videos(args.channel_id, max_results=args.max_results)
    if not stats and not top_videos:
        print("No data returned — is YOUTUBE_API_KEY set and the channel id valid?", file=sys.stderr)
        return 1
    print(json.dumps({"channel": stats, "top_videos": top_videos}, indent=2))
    return 0


def cmd_youtube_create_playlist(args: argparse.Namespace) -> int:
    """Create a YouTube playlist."""
    from ai_influencer_studio.youtube_publish import YouTubePublisher

    config = StudioConfig.from_file()
    publisher = YouTubePublisher(
        token_path=config.youtube_token_path,
        client_secrets_path=config.youtube_client_secrets_path,
    )
    try:
        service = publisher._service()
        playlist_id = publisher.create_playlist(
            service,
            args.title,
            args.description,
            args.privacy or config.youtube_default_privacy,
        )
    except Exception as exc:
        print(f"Playlist creation failed: {exc}", file=sys.stderr)
        return 1
    if not playlist_id:
        print("Playlist creation failed (no id returned).", file=sys.stderr)
        return 1
    print(json.dumps({"playlist_id": playlist_id, "title": args.title}, indent=2))
    return 0


def cmd_music_video_assemble(args: argparse.Namespace) -> int:
    """Beat-snap assemble a saved plan's clips with ffmpeg."""
    from ai_influencer_studio.beat_assembly import assemble

    try:
        song = _load_plan_song(args.plan, args.song_index)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        result = assemble(
            song,
            out_path=args.output,
            audio_path=args.audio,
            beat_snap=not args.no_beat_snap,
        )
    except Exception as exc:
        print(f"Assembly failed: {exc}", file=sys.stderr)
        return 1
    summary = {key: value for key, value in result.items() if key != "command"}
    print(json.dumps(summary, indent=2))
    return 0


def cmd_repurpose(args: argparse.Namespace) -> int:
    """Create a vertical repurposed clip from an existing video."""
    config = StudioConfig.from_file()
    repurposer = VideoRepurposer()
    output_dir = config.media_dir / "repurposed"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.multi:
        platform_list = [p.strip() for p in args.platforms.split(",") if p.strip()]
        results = repurposer.create_multi_clips(
            args.input,
            output_dir,
            platforms=platform_list,
            clip_duration=args.clip_duration,
        )
        print(json.dumps({"clips": results}, indent=2))
    else:
        output_path = output_dir / f"{Path(args.input).stem}_{args.platform}.mp4"
        kwargs: dict[str, Any] = {
            "platform": args.platform,
            "start": args.start,
            "caption": args.caption,
        }
        if args.duration > 0:
            kwargs["duration"] = args.duration
        result = repurposer.create_vertical_cut(args.input, output_path, **kwargs)
        print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aisocial", description="AI Influencer Studio")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # config
    subparsers.add_parser("config", help="Create or edit configuration")

    # create
    create_parser = subparsers.add_parser("create", help="Generate content")
    create_parser.add_argument("--type", required=True, help="Content type")
    create_parser.add_argument("--topic", required=True, help="Topic or prompt")
    create_parser.add_argument("--platform", default="instagram", help="Target platform")
    create_parser.add_argument("--style", default=None, help="Visual/writing style")
    create_parser.add_argument("--audio", default=None, help="Audio file for music video")
    create_parser.add_argument("--genre", default=None, help="Music genre")
    create_parser.add_argument("--mood", default=None, help="Music mood")
    create_parser.add_argument("--platforms", nargs="+", help="Target platforms")
    create_parser.add_argument("--word-count", type=int, default=500, help="Blog word count")
    create_parser.add_argument("--duration", type=int, default=2, help="Video script duration")
    create_parser.set_defaults(func=cmd_create)

    # schedule
    schedule_parser = subparsers.add_parser("schedule", help="Schedule a post")
    schedule_parser.add_argument("--platform", required=True, help="Target platform")
    schedule_parser.add_argument("--content", required=True, help="Post content")
    schedule_parser.add_argument("--when", required=True, help="ISO datetime")
    schedule_parser.add_argument("--media-paths", nargs="*", default=[], help="Media files")
    schedule_parser.add_argument("--hashtags", nargs="*", default=[], help="Hashtags")
    schedule_parser.set_defaults(func=cmd_schedule)

    # schedule list
    schedule_list_parser = subparsers.add_parser("schedule-list", help="List scheduled posts")
    schedule_list_parser.set_defaults(func=cmd_schedule_list)

    # daemon
    daemon_parser = subparsers.add_parser("daemon", help="Run publishing scheduler")
    daemon_parser.add_argument("--interval", type=int, default=60, help="Poll interval seconds")
    daemon_parser.set_defaults(func=cmd_daemon)

    # web
    web_parser = subparsers.add_parser("web", help="Launch web dashboard")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host")
    web_parser.add_argument("--port", type=int, default=8000, help="Port")
    web_parser.set_defaults(func=cmd_web)

    # local diagnostics
    doctor_parser = subparsers.add_parser("doctor", help="Check Python dependency installation without changing anything")
    doctor_parser.set_defaults(func=cmd_doctor)

    # local health
    health_parser = subparsers.add_parser("health", help="Show local operational health without network calls")
    health_parser.set_defaults(func=cmd_health)

    # model-registry
    registry_parser = subparsers.add_parser("model-registry", help="Live Ollama/OpenRouter registry and LiteLLM config")
    registry_sub = registry_parser.add_subparsers(dest="registry_command", required=True)
    refresh_parser = registry_sub.add_parser("refresh", help="Discover providers and emit routing config")
    refresh_parser.add_argument("--ollama-url", default="http://localhost:11434")
    refresh_parser.add_argument("--openrouter-url", default="https://openrouter.ai/api/v1")
    refresh_parser.add_argument("--snapshot", default=None, help="Registry JSON output path")
    refresh_parser.add_argument("--litellm-config", default=None, help="Generated LiteLLM YAML path")
    refresh_parser.add_argument("--no-ollama", action="store_true", help="Skip local Ollama discovery")
    refresh_parser.add_argument("--no-openrouter", action="store_true", help="Skip OpenRouter discovery")
    refresh_parser.add_argument("--daily", action="store_true", help="Refresh only when the saved catalog is older than 24 hours")
    refresh_parser.add_argument("--force", action="store_true", help="Force a daily refresh")
    refresh_parser.set_defaults(func=cmd_model_registry_refresh)

    status_parser = registry_sub.add_parser("status", help="Show freshness and verification without network calls")
    status_parser.add_argument("--snapshot", default=None, help="Registry JSON input path")
    status_parser.set_defaults(func=cmd_model_registry_status)

    probe_parser = registry_sub.add_parser("probe", help="Probe selected models without changing catalog availability")
    probe_parser.add_argument("--ollama-url", default="http://localhost:11434")
    probe_parser.add_argument("--openrouter-url", default="https://openrouter.ai/api/v1")
    probe_parser.add_argument("--snapshot", default=None, help="Registry JSON input/output path")
    probe_parser.add_argument("--model-ref", action="append", default=[], help="Provider-qualified model ref; repeatable")
    probe_parser.add_argument("--limit", type=int, default=10)
    probe_parser.add_argument("--include-hosted", action="store_true", help="Explicitly allow hosted probes")
    probe_parser.set_defaults(func=cmd_model_registry_probe)

    export_docs_parser = registry_sub.add_parser("export-docs", help="Export an offline Markdown report from a snapshot")
    export_docs_parser.add_argument("--snapshot", default=None, help="Registry JSON input path")
    export_docs_parser.add_argument("--output", default=None, help="Markdown report output path")
    export_docs_parser.set_defaults(func=cmd_model_registry_export_docs)

    list_parser = registry_sub.add_parser("list", help="Inspect a saved registry snapshot")
    list_parser.add_argument("--snapshot", default=None, help="Registry JSON input path")
    list_parser.add_argument("--json", action="store_true", help="Print raw JSON")
    list_parser.set_defaults(func=cmd_model_registry_list)

    # indexer
    indexer_parser = subparsers.add_parser("indexer", help="Local multimodal file index and review queue")
    indexer_sub = indexer_parser.add_subparsers(dest="indexer_command", required=True)

    scan_parser = indexer_sub.add_parser("scan", help="Dry-run scan; never moves files")
    scan_parser.add_argument("--source", required=True, help="Source directory to scan")
    scan_parser.add_argument("--target", required=True, help="Proposed destination root")
    scan_parser.set_defaults(func=cmd_indexer_scan)

    queue_parser = indexer_sub.add_parser("queue", help="List indexed files and review status")
    queue_parser.add_argument("--status", action="append", choices=["PENDING", "APPROVED", "REJECTED", "DUPLICATE", "SUPERSEDED", "PARTIAL", "APPLIED", "ERROR"])
    queue_parser.set_defaults(func=cmd_indexer_queue)

    for command_name, handler, verb in (("approve", cmd_indexer_approve, "Approve"), ("reject", cmd_indexer_reject, "Reject")):
        command = indexer_sub.add_parser(command_name, help=f"{verb} pending queue records")
        command.add_argument("--ids", nargs="+", type=int, default=[])
        command.add_argument("--all", action="store_true", help=f"{verb} all pending records")
        command.set_defaults(func=handler)

    apply_parser = indexer_sub.add_parser("apply", help="Apply approved records with explicit confirmation")
    apply_parser.add_argument("--ids", nargs="+", type=int, default=[])
    apply_parser.add_argument("--source", default=None, help="Expected scan source root")
    apply_parser.add_argument("--target", default=None, help="Expected scan target root")
    apply_parser.add_argument("--confirm", action="store_true", help="Confirm file copy/verify/remove operations")
    apply_parser.set_defaults(func=cmd_indexer_apply)

    # safe-use
    safe_parser = subparsers.add_parser("safe-use", help="Safe browser and Windows UI automation")
    safe_sub = safe_parser.add_subparsers(dest="safe_command", required=True)

    def add_safe_policy_flags(command: argparse.ArgumentParser) -> None:
        command.add_argument("--target", choices=["browser", "windows"], default="browser")
        command.add_argument("--domain", action="append", default=[], help="Allowlisted browser domain; repeatable")
        command.add_argument("--app", action="append", default=[], help="Allowlisted Windows app name; repeatable")
        command.add_argument("--allow-sensitive-fields", action="store_true")
        command.add_argument("--headed", action="store_true", help="Show browser UI instead of headless mode")

    observe_parser = safe_sub.add_parser("observe", help="Observe without mutating")
    add_safe_policy_flags(observe_parser)
    observe_parser.add_argument("--url", default=None)
    observe_parser.add_argument("--selector", default="body")
    observe_parser.add_argument("--max-chars", type=int, default=12000)
    observe_parser.add_argument("--screenshot", action="store_true")
    observe_parser.add_argument("--app-name", default=None)
    observe_parser.add_argument("--max-depth", type=int, default=3)
    observe_parser.set_defaults(func=cmd_safe_use_observe)

    propose_parser = safe_sub.add_parser("propose", help="Validate an action without executing")
    add_safe_policy_flags(propose_parser)
    propose_parser.add_argument("--intent", required=True, help="Action intent JSON")
    propose_parser.set_defaults(func=cmd_safe_use_propose)

    execute_parser = safe_sub.add_parser("execute", help="Execute one explicitly approved action")
    add_safe_policy_flags(execute_parser)
    execute_parser.add_argument("--intent", required=True, help="Action intent JSON")
    execute_parser.add_argument("--approve", action="store_true", help="Explicitly approve this one action")
    execute_parser.set_defaults(func=cmd_safe_use_execute)

    mcp_parser = safe_sub.add_parser("mcp-config", help="Generate isolated Playwright MCP config")
    mcp_parser.add_argument("--output", default=None)
    mcp_parser.add_argument("--domain", action="append", default=[], help="Allowlisted domain; repeatable")
    mcp_parser.add_argument("--app", action="append", default=[], help="Allowlisted Windows app; repeatable")
    mcp_parser.add_argument("--headed", action="store_true")
    mcp_parser.add_argument("--persistent", action="store_true", help="Do not use an isolated browser profile")
    mcp_parser.set_defaults(func=cmd_safe_use_mcp_config)

    # agent
    agent_parser = subparsers.add_parser("agent", help="Run an autonomous multi-model browser/computer task")
    agent_parser.add_argument("--task", required=True, help="Natural-language task")
    agent_parser.add_argument("--target", choices=["browser", "windows"], default="browser")
    agent_parser.add_argument("--url", default=None, help="Start URL for browser tasks")
    agent_parser.add_argument("--app-name", default=None, help="Windows application name for windows tasks")
    agent_parser.add_argument("--domain", action="append", default=[], help="Allowlisted browser domain; repeatable")
    agent_parser.add_argument("--allow-app", action="append", default=[], help="Allowlisted Windows app; repeatable")
    agent_parser.add_argument("--allow-sensitive-fields", action="store_true")
    agent_parser.add_argument("--models", action="append", default=[], help="Provider::model ref; repeatable (default: 4 free vision models from snapshot)")
    agent_parser.add_argument("--snapshot", default=None, help="Registry snapshot for auto model selection")
    agent_parser.add_argument("--ollama-url", default="http://localhost:11434")
    agent_parser.add_argument("--headed", action="store_true", help="Show browser UI instead of headless mode")
    agent_parser.add_argument("--max-steps", type=int, default=12, help="Maximum agent steps")
    agent_parser.add_argument("--aggregator", default=None, help="Provider::model ref to merge proposals (MoA); defaults to majority vote")
    agent_parser.set_defaults(func=cmd_agent_run)

    # music-video
    music_parser = subparsers.add_parser("music-video", help="Music video research & planning")
    music_sub = music_parser.add_subparsers(dest="music_command", required=True)

    research_parser = music_sub.add_parser("research", help="Research generators and trends")
    research_parser.add_argument("--generators", action="store_true", help="List free video generators")
    research_parser.add_argument("--trends", action="store_true", help="Fetch YouTube trend data")
    research_parser.add_argument("--vram", type=int, default=8, help="Available VRAM in GB")
    research_parser.add_argument("--max-results", type=int, default=10, help="Max trend results")
    research_parser.set_defaults(func=cmd_music_video_research)

    bible_parser = music_sub.add_parser("style-bible-template", help="Create a JSON character/style bible template")
    bible_parser.add_argument("--output", required=True, help="Output JSON path")
    bible_parser.set_defaults(func=cmd_music_video_style_bible_template)

    plan_parser = music_sub.add_parser("plan", help="Create song plans")
    plan_parser.add_argument(
        "--song",
        action="append",
        required=True,
        help='JSON object with keys: name, audio, genre, mood, duration. Example: --song \'{"name":"Track","audio":"track.mp3"}\'',
    )
    plan_parser.add_argument("--assets-root", default=None, help="Root path for reusable assets")
    plan_parser.add_argument("--staging-root", default=None, help="Flat gdrive staging dir to classify (clips/characters/styles)")
    plan_parser.add_argument("--character-ref", default=None, help="Path to character reference image")
    plan_parser.add_argument("--style-bible", default=None, help="Optional JSON character/style bible")
    plan_parser.add_argument(
        "--generation-mode",
        default="full",
        choices=["full", "clip_only", "assembly_only"],
        help="Pipeline generation mode",
    )
    plan_parser.set_defaults(func=cmd_music_video_plan)

    master_parser = music_sub.add_parser("master-plan", help="Create and save master plan")
    master_parser.add_argument(
        "--song",
        action="append",
        required=True,
        help='JSON object with keys: name, audio, genre, mood, duration. Example: --song \'{"name":"Track","audio":"track.mp3"}\'',
    )
    master_parser.add_argument("--assets-root", default=None, help="Root path for reusable assets")
    master_parser.add_argument("--staging-root", default=None, help="Flat gdrive staging dir to classify (clips/characters/styles)")
    master_parser.add_argument("--character-ref", default=None, help="Path to character reference image")
    master_parser.add_argument("--style-bible", default=None, help="Optional JSON character/style bible")
    master_parser.add_argument(
        "--generation-mode",
        default="full",
        choices=["full", "clip_only", "assembly_only"],
        help="Pipeline generation mode",
    )
    master_parser.add_argument("--output", default=None, help="Output JSON path")
    master_parser.set_defaults(func=cmd_music_video_master_plan)

    execute_parser = music_sub.add_parser("execute", help="Execute a saved plan via ComfyUI")
    execute_parser.add_argument("--plan", required=True, help="Path to master plan JSON")
    execute_parser.add_argument("--song-index", type=int, default=0, help="Song index to execute")
    execute_parser.add_argument(
        "--generation-mode",
        default="",
        choices=["", "full", "clip_only", "assembly_only"],
        help="Override generation mode (default: use plan value)",
    )
    execute_parser.add_argument("--platforms", nargs="*", help="Target platforms")
    execute_parser.set_defaults(func=cmd_music_video_execute)

    assemble_parser = music_sub.add_parser("assemble", help="Beat-snap assemble a saved plan's clips with ffmpeg")
    assemble_parser.add_argument("--plan", required=True, help="Path to master plan JSON")
    assemble_parser.add_argument("--song-index", type=int, default=0, help="Song index to assemble")
    assemble_parser.add_argument("--output", required=True, help="Output mp4 path")
    assemble_parser.add_argument("--audio", default=None, help="Override the audio track")
    assemble_parser.add_argument("--no-beat-snap", action="store_true", help="Keep scene boundaries as planned (no snap)")
    assemble_parser.set_defaults(func=cmd_music_video_assemble)

    # youtube
    youtube_parser = subparsers.add_parser("youtube", help="Publish music videos to YouTube (OAuth2)")
    youtube_sub = youtube_parser.add_subparsers(dest="youtube_command", required=True)

    yt_metadata_parser = youtube_sub.add_parser("metadata", help="Preview metadata generated from a song plan (no network)")
    yt_metadata_parser.add_argument("--plan", required=True, help="Path to master plan JSON")
    yt_metadata_parser.add_argument("--song-index", type=int, default=0, help="Song index")
    yt_metadata_parser.set_defaults(func=cmd_youtube_metadata)

    yt_upload_parser = youtube_sub.add_parser("upload", help="Upload a finished video using metadata from a song plan")
    yt_upload_parser.add_argument("--plan", required=True, help="Path to master plan JSON")
    yt_upload_parser.add_argument("--song-index", type=int, default=0, help="Song index")
    yt_upload_parser.add_argument("--video", default=None, help="Video file (default: next to the plan as .mp4)")
    yt_upload_parser.add_argument("--thumbnail", default=None, help="Thumbnail image path")
    yt_upload_parser.add_argument("--privacy", choices=["private", "public", "unlisted"], default=None)
    yt_upload_parser.add_argument("--category", default=None, help="YouTube category id (default: 10 Music)")
    yt_upload_parser.add_argument("--playlist", action="append", default=[], help="Playlist id; repeatable")
    yt_upload_parser.add_argument("--create-playlist", default=None, help="Create a playlist and file the video into it")
    yt_upload_parser.set_defaults(func=cmd_youtube_upload)

    yt_file_parser = youtube_sub.add_parser("upload-file", help="Upload any video file directly")
    yt_file_parser.add_argument("--video", required=True, help="Video file path")
    yt_file_parser.add_argument("--title", default=None, help="Title (default: video filename)")
    yt_file_parser.add_argument("--description", default="", help="Description")
    yt_file_parser.add_argument("--tags", default=None, help="Comma-separated tags")
    yt_file_parser.add_argument("--thumbnail", default=None, help="Thumbnail image path")
    yt_file_parser.add_argument("--privacy", choices=["private", "public", "unlisted"], default=None)
    yt_file_parser.add_argument("--category", default=None, help="YouTube category id")
    yt_file_parser.add_argument("--playlist", action="append", default=[], help="Playlist id; repeatable")
    yt_file_parser.set_defaults(func=cmd_youtube_upload_file)

    yt_info_parser = youtube_sub.add_parser("channel-info", help="Show the authenticated channel's statistics")
    yt_info_parser.set_defaults(func=cmd_youtube_channel_info)

    yt_analytics_parser = youtube_sub.add_parser("analytics", help="Fetch public channel stats + top videos via the Data API key")
    yt_analytics_parser.add_argument("--channel-id", required=True, help="YouTube channel id (e.g. UC...)")
    yt_analytics_parser.add_argument("--max-results", type=int, default=10, help="Number of top videos")
    yt_analytics_parser.set_defaults(func=cmd_youtube_analytics)

    yt_playlist_parser = youtube_sub.add_parser("create-playlist", help="Create a YouTube playlist")
    yt_playlist_parser.add_argument("--title", required=True, help="Playlist title")
    yt_playlist_parser.add_argument("--description", default="", help="Playlist description")
    yt_playlist_parser.add_argument("--privacy", choices=["private", "public", "unlisted"], default=None)
    yt_playlist_parser.set_defaults(func=cmd_youtube_create_playlist)

    # gdrive
    gdrive_parser = subparsers.add_parser("gdrive", help="Google Drive reference-media uploader (content-dedupe + pending/done lists)")
    gdrive_sub = gdrive_parser.add_subparsers(dest="gdrive_command", required=True)

    gdrive_collect_parser = gdrive_sub.add_parser("collect", help="Scan sources, filter, dedupe by content into pending")
    gdrive_collect_parser.add_argument("--source", action="append", required=True, help="Source directory; repeatable")
    gdrive_collect_parser.add_argument("--state", default=None, help="Upload state JSON path")
    gdrive_collect_parser.set_defaults(func=cmd_gdrive_collect)

    gdrive_status_parser = gdrive_sub.add_parser("status", help="Show pending/done counts")
    gdrive_status_parser.add_argument("--state", default=None, help="Upload state JSON path")
    gdrive_status_parser.set_defaults(func=cmd_gdrive_status)

    gdrive_upload_parser = gdrive_sub.add_parser("upload", help="Upload pending files in paced batches")
    gdrive_upload_parser.add_argument("--state", default=None, help="Upload state JSON path")
    gdrive_upload_parser.add_argument("--batch-size", type=int, default=20, help="Files per Playwright batch")
    gdrive_upload_parser.add_argument("--delay", type=float, default=45.0, help="Seconds between batches (slow uploads)")
    gdrive_upload_parser.add_argument("--headed", action="store_true", help="Show Chrome UI instead of headless")
    gdrive_upload_parser.add_argument("--max-batches", type=int, default=None, help="Stop after N batches")
    gdrive_upload_parser.add_argument(
        "--user-data-dir", default=None, help="Chrome profile dir (e.g. your signed-in main profile)"
    )
    gdrive_upload_parser.add_argument(
        "--cdp-url", default=None, help="Attach to a running Chrome via CDP (e.g. http://127.0.0.1:9222)"
    )
    gdrive_upload_parser.add_argument(
        "--backend", choices=["browser", "drive_api", "rclone"], default=None, help="Upload transport (default: config gdrive_backend)"
    )
    gdrive_upload_parser.add_argument(
        "--rclone-remote", default=None, help="rclone remote for the rclone backend, e.g. 'gdrive:' (default: config gdrive_rclone_remote)"
    )
    gdrive_upload_parser.add_argument(
        "--rclone-path", default=None, help="Folder inside the rclone remote (default: config gdrive_rclone_path)"
    )
    gdrive_upload_parser.set_defaults(func=cmd_gdrive_upload)

    # repurpose
    repurpose_parser = subparsers.add_parser("repurpose", help="Create vertical clips from existing videos")
    repurpose_parser.add_argument("--input", required=True, help="Path to source video")
    repurpose_parser.add_argument("--platform", default="tiktok", help="Target platform")
    repurpose_parser.add_argument("--platforms", default="tiktok", help="Comma-separated platforms for --multi")
    repurpose_parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds")
    repurpose_parser.add_argument("--duration", type=float, default=0.0, help="Clip duration in seconds (0 = full)")
    repurpose_parser.add_argument("--caption", default=None, help="Caption to burn into the clip")
    repurpose_parser.add_argument("--multi", action="store_true", help="Generate multi-platform clips")
    repurpose_parser.add_argument("--clip-duration", type=float, default=15.0, help="Segment duration for --multi")
    repurpose_parser.set_defaults(func=cmd_repurpose)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
