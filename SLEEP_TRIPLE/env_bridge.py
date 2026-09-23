#!/usr/bin/env python3
"""Bridge workspace .env values into SLEEP_TRIPLE lane config JSON files."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent

ENV_SEARCH_PATHS = (
    WORKSPACE / ".env",
    WORKSPACE / "python" / ".env",
)

# JSON config key -> environment variable name
CONFIG_ENV_MAP: dict[str, dict[str, str]] = {
    "opt_a_config.json": {
        "gumroad_api_key": "GUMROAD_API_KEY",
    },
    "opt_b_config.json": {
        "youtube_oauth_credentials_path": "YOUTUBE_OAUTH_CREDENTIALS_PATH",
    },
    "opt_c_config.json": {
        "cryptocompare_api_key": "CRYPTOCOMPARE_API_KEY",
        "binance_api_key": "BINANCE_API_KEY",
        "binance_api_secret": "BINANCE_API_SECRET",
    },
    "opt_e_config.json": {
        "shopify_store_url": "SHOPIFY_STORE_URL",
        "shopify_admin_api_token": "SHOPIFY_ADMIN_TOKEN",
        "printful_api_key": "PRINTFUL_API_KEY",
    },
    "sleep_config.json": {
        "printful_api_key": "PRINTFUL_API_KEY",
    },
}

_PLACEHOLDER_RE = re.compile(
    r"^(?:replace(?:_with)?|todo|tbd|none|null|<[^>]+>|\{[^}]+\})$",
    re.IGNORECASE,
)


def load_dotenv() -> dict[str, str]:
    """Parse .env files (no python-dotenv dependency). Later paths do not override earlier."""
    values: dict[str, str] = {}
    for path in ENV_SEARCH_PATHS:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            if key and key not in values:
                values[key] = val.strip().strip("\"'")
    for key, val in os.environ.items():
        if val:
            values[key] = val
    return values


def is_placeholder(value: Any) -> bool:
    """True when value is empty or a known unset sentinel."""
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    if not stripped:
        return True
    upper = stripped.upper()
    if upper.startswith("REPLACE"):
        return True
    if upper in ("NONE", "NULL", "TODO", "TBD"):
        return True
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    if stripped.startswith("{") and stripped.endswith("}"):
        return True
    for suffix in ("_HERE", "_TOKEN", "_KEY"):
        if upper.endswith(suffix):
            return True
    return bool(_PLACEHOLDER_RE.match(stripped))


def _path_credential_ok(path_value: str, *, min_bytes: int = 50) -> bool:
    """True when env points at a real on-disk credential file (not just a path string)."""
    if not path_value or is_placeholder(path_value):
        return False
    p = Path(path_value).expanduser()
    try:
        return p.is_file() and p.stat().st_size > min_bytes
    except OSError:
        return False


def overlay_env(cfg: dict, config_name: str, env: dict[str, str] | None = None) -> dict:
    """Return a copy of cfg with non-placeholder env values applied."""
    env = env if env is not None else load_dotenv()
    mapping = CONFIG_ENV_MAP.get(config_name, {})
    out = dict(cfg)
    for json_key, env_key in mapping.items():
        env_val = env.get(env_key, "").strip()
        if env_val and not is_placeholder(env_val):
            out[json_key] = env_val
    return out


def load_config(config_path: Path | str, *, apply_env: bool = True) -> dict:
    """Load a lane config JSON file with optional .env overlay."""
    path = Path(config_path)
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if apply_env:
        cfg = overlay_env(cfg, path.name)
    return cfg


def credential_report() -> dict[str, Any]:
    """Summarize which revenue credentials are set (values never returned)."""
    env = load_dotenv()
    lanes = {
        "gumroad": {
            "env": "GUMROAD_API_KEY",
            "configured": bool(env.get("GUMROAD_API_KEY")) and not is_placeholder(env["GUMROAD_API_KEY"]),
            "signup": "https://app.gumroad.com/settings/advanced#application",
        },
        "youtube_oauth": {
            "env": "YOUTUBE_OAUTH_CREDENTIALS_PATH",
            # Path string alone is not enough — token file must exist on disk
            "configured": _path_credential_ok(env.get("YOUTUBE_OAUTH_CREDENTIALS_PATH", "")),
            "signup": "https://console.cloud.google.com/apis/credentials",
        },
        "discord_webhook": {
            "env": "DISCORD_WEBHOOK_URL",
            "configured": bool(env.get("DISCORD_WEBHOOK_URL")),
            "signup": "https://support.discord.com/hc/en-us/articles/228383668",
        },
        "stripe": {
            "env": "STRIPE_SECRET_KEY",
            "configured": bool(env.get("STRIPE_SECRET_KEY")),
            "signup": "https://dashboard.stripe.com/apikeys",
        },
        "shopify": {
            "env": "SHOPIFY_ADMIN_TOKEN",
            "configured": bool(env.get("SHOPIFY_ADMIN_TOKEN")) and not is_placeholder(env.get("SHOPIFY_ADMIN_TOKEN", "")),
            "signup": "https://admin.shopify.com/store",
        },
        "printful": {
            "env": "PRINTFUL_API_KEY",
            "configured": bool(env.get("PRINTFUL_API_KEY")) and not is_placeholder(env.get("PRINTFUL_API_KEY", "")),
            "signup": "https://www.printful.com/dashboard/settings#api",
        },
        "cryptocompare": {
            "env": "CRYPTOCOMPARE_API_KEY",
            "configured": bool(env.get("CRYPTOCOMPARE_API_KEY")),
            "signup": "https://www.cryptocompare.com/cryptopian/api-keys",
        },
        "binance": {
            "env": "BINANCE_API_KEY",
            "configured": bool(env.get("BINANCE_API_KEY"))
            and bool(env.get("BINANCE_API_SECRET"))
            and not is_placeholder(env.get("BINANCE_API_KEY", ""))
            and not is_placeholder(env.get("BINANCE_API_SECRET", "")),
            "signup": "https://www.binance.com/en/my/settings/api-management",
        },
        "openrouter": {
            "env": "OPENROUTER_API_KEY",
            "configured": bool(env.get("OPENROUTER_API_KEY")),
            "signup": "https://openrouter.ai/keys",
        },
    }
    configured = [k for k, v in lanes.items() if v["configured"]]
    missing = [k for k, v in lanes.items() if not v["configured"]]
    return {
        "env_files_checked": [str(p) for p in ENV_SEARCH_PATHS if p.is_file()],
        "configured": configured,
        "missing": missing,
        "lanes": lanes,
    }