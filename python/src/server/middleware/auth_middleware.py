from fastapi import Request, HTTPException, status
from supabase import create_client, Client
import os
import logging
import threading

logger = logging.getLogger(__name__)

_PLACEHOLDER_SUPABASE_URLS = (
    "example.supabase.co",
    "test.supabase.co",
    "your-project.supabase.co",
)
_PLACEHOLDER_SUPABASE_KEYS = (
    "example-key",
    "test-key-fake-for-bare-windows",
    "your-service-key-here",
)


def _is_placeholder_supabase(url: str | None, key: str | None) -> bool:
    if not url or not key:
        return True
    url_lower = url.lower()
    if any(fragment in url_lower for fragment in _PLACEHOLDER_SUPABASE_URLS):
        return True
    return key.strip() in _PLACEHOLDER_SUPABASE_KEYS


# Lazy-initialize Supabase client — avoids crash on import when credentials are missing/invalid.
# A lock prevents duplicate-client races on concurrent first-request load.
_supabase_lock = threading.Lock()
_supabase_client: Client | None = None


def _get_supabase() -> Client | None:
    """Lazy initializer for Supabase client (thread-safe)."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    with _supabase_lock:
        if _supabase_client is not None:
            return _supabase_client

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if _is_placeholder_supabase(supabase_url, supabase_key):
            logger.warning("Placeholder Supabase credentials — auth DB validation disabled")
            return None

        if not supabase_url or not supabase_key:
            logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set — auth disabled")
            return None

        try:
            _supabase_client = create_client(supabase_url, supabase_key)
            return _supabase_client
        except Exception as e:
            logger.warning(f"Supabase client initialization failed: {e} — auth disabled")
            return None


async def authenticate_api_key(request: Request):
    """
    Middleware to authenticate requests using API key.
    Expects API key in the 'X-API-Key' header.
    Skips validation if Supabase is unavailable.
    """
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )

    local_dev_key = os.getenv("ARCHON_VOICE_API_KEY", "local-voice-assistant")
    if os.getenv("ARCHON_ENV", "development") == "development" and api_key == local_dev_key:
        return

    supabase = _get_supabase()
    if supabase is None:
        # Supabase unavailable — skip DB validation but require header presence
        logger.warning("Auth middleware: Supabase unavailable, skipping DB validation")
        return

    # Verify the API key exists in our database
    try:
        result = supabase.table("api_keys").select("user_id").eq("key", api_key).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )