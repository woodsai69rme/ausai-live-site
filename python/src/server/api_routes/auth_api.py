from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import os
import secrets
import logging
from supabase import create_client, Client

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy-initialize Supabase client
_supabase_client: Client | None = None


def _get_supabase() -> Client | None:
    """Lazy initializer for Supabase client."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set — auth disabled")
        return None

    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        return _supabase_client
    except Exception as e:
        logger.warning(f"Supabase client initialization failed: {e} — auth disabled")
        return None

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class APIKeyResponse(BaseModel):
    api_key: str

@router.post("/register", response_model=APIKeyResponse)
async def register(user: UserRegister):
    supabase = _get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": user.email,
            "password": user.password,
            "email_confirm": True
        })

        user_id = auth_response.user.id

        # Generate API key
        api_key = secrets.token_hex(32)

        # Store API key in our custom table
        supabase.table("api_keys").insert({
            "user_id": user_id,
            "key": api_key
        }).execute()

        return {"api_key": api_key}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=APIKeyResponse)
async def login(user: UserLogin):
    supabase = _get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        user_id = auth_response.user.id

        # Retrieve existing API key or generate new one
        result = supabase.table("api_keys").select("key").eq("user_id", user_id).execute()

        if result.data and len(result.data) > 0:
            api_key = result.data[0]["key"]
        else:
            # Generate new API key if none exists
            api_key = secrets.token_hex(32)
            supabase.table("api_keys").insert({
                "user_id": user_id,
                "key": api_key
            }).execute()

        return {"api_key": api_key}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )