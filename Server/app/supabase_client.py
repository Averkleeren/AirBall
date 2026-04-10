import os

from dotenv import load_dotenv
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

load_dotenv()

DEFAULT_FRONTEND_URL = "http://localhost:3000"
DEFAULT_PASSWORD_RESET_PATH = "/auth/reset-password"


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SUPABASE_URL = _get_required_env("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = _get_required_env("SUPABASE_SERVICE_ROLE_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", DEFAULT_FRONTEND_URL)
PASSWORD_RESET_REDIRECT_URL = os.getenv(
    "PASSWORD_RESET_REDIRECT_URL",
    f"{FRONTEND_URL}{DEFAULT_PASSWORD_RESET_PATH}",
)


def get_supabase_client() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )
