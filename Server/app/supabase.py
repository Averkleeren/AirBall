import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _build_client(key: str) -> Any:
    return create_client(_get_required_env("SUPABASE_URL"), key)


@lru_cache
def get_supabase_client() -> Any:
    return _build_client(_get_required_env("SUPABASE_ANON_KEY"))


@lru_cache
def get_supabase_admin_client() -> Any | None:
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not service_role_key:
        return None
    return _build_client(service_role_key)


def get_auth_redirect_url(override: str | None = None) -> str | None:
    if override:
        return override
    return os.getenv("SUPABASE_EMAIL_REDIRECT_TO") or os.getenv("FRONTEND_URL")