"""Wild Turkey — Application Configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://wildturkey:wildturkey@localhost:5432/wildturkey"
    DATABASE_SYNC_URL: str = "postgresql://wildturkey:wildturkey@localhost:5432/wildturkey"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    
    VAULT_KEY: str = ""
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3737"]
    
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY: Optional[str] = None
    
    TASK_QUEUE_DEFAULT_TIMEOUT: int = 300
    TASK_QUEUE_MAX_RETRIES: int = 3
    
    MONITOR_DEFAULT_INTERVAL: int = 60
    MONITOR_GITHUB_TOKEN: Optional[str] = None
    
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000
    
    ENABLE_TERMINAL_API: bool = False
    ENABLE_MCP_CODE_EXEC: bool = False
    
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()

if settings.ENVIRONMENT == "production":
    if not settings.VAULT_KEY:
        raise RuntimeError("VAULT_KEY must be set in production environment")
    if settings.JWT_SECRET_KEY == "change-me-in-production-use-a-real-secret":
        raise RuntimeError("JWT_SECRET_KEY must be changed from its default in production environment")
