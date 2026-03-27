from typing import Any

from fastapi import APIRouter, Header, HTTPException, status

from ..schemas import (
    AuthMessage,
    PasswordResetRequest,
    ResendVerificationRequest,
    SignupResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from ..supabase import get_auth_redirect_url, get_supabase_client

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

def _to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if isinstance(value, dict):
        return value
    return dict(value)


def _serialize_user(user: Any) -> dict[str, Any]:
    payload = _to_dict(user)
    metadata = payload.get("user_metadata") or payload.get("raw_user_meta_data") or {}
    return {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "username": metadata.get("username") or metadata.get("full_name") or payload.get("username"),
        "email_confirmed_at": payload.get("email_confirmed_at"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "raw_user_meta_data": metadata,
    }


def _raise_auth_error(exc: Exception, fallback_status: int = status.HTTP_400_BAD_REQUEST) -> None:
    message = getattr(exc, "message", None) or str(exc)
    error_status = getattr(exc, "status", None) or getattr(exc, "status_code", None) or fallback_status
    normalized_message = message.lower()

    if "invalid login credentials" in normalized_message:
        error_status = status.HTTP_401_UNAUTHORIZED
    elif "email not confirmed" in normalized_message:
        error_status = status.HTTP_403_FORBIDDEN
    elif "user already registered" in normalized_message:
        error_status = status.HTTP_400_BAD_REQUEST

    raise HTTPException(status_code=error_status, detail=message)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate):
    supabase = get_supabase_client()

    credentials = {
        "email": user_data.email,
        "password": user_data.password,
        "options": {
            "data": {
                "username": user_data.username,
                "full_name": user_data.username,
            }
        },
    }

    redirect_to = get_auth_redirect_url(user_data.email_redirect_to)
    if redirect_to:
        credentials["options"]["email_redirect_to"] = redirect_to

    try:
        response = supabase.auth.sign_up(credentials)
        user = getattr(response, "user", None)
        session = getattr(response, "session", None)
    except Exception as exc:
        _raise_auth_error(exc)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Supabase did not return a user for signup",
        )

    return {
        "message": "Signup successful. Check your email to verify your account.",
        "user": _serialize_user(user),
        "email_verification_required": session is None,
    }

@router.post("/login", response_model=Token)
def login(user_data: UserLogin):
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": user_data.email,
                "password": user_data.password,
            }
        )
    except Exception as exc:
        _raise_auth_error(exc, fallback_status=status.HTTP_401_UNAUTHORIZED)

    session = getattr(response, "session", None)
    user = getattr(response, "user", None)

    if session is None or user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "token_type": "bearer",
        "expires_in": getattr(session, "expires_in", None),
        "expires_at": getattr(session, "expires_at", None),
        "user": _serialize_user(user),
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(authorization: str | None = Header(default=None, alias="Authorization")):
    supabase = get_supabase_client()
    token = _extract_bearer_token(authorization)

    try:
        response = supabase.auth.get_user(token)
    except Exception as exc:
        _raise_auth_error(exc, fallback_status=status.HTTP_401_UNAUTHORIZED)

    user = getattr(response, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return _serialize_user(user)


@router.post("/forgot-password", response_model=AuthMessage)
def forgot_password(payload: PasswordResetRequest):
    supabase = get_supabase_client()
    redirect_to = get_auth_redirect_url(payload.redirect_to)

    try:
        if redirect_to:
            supabase.auth.reset_password_for_email(payload.email, {"redirect_to": redirect_to})
        else:
            supabase.auth.reset_password_for_email(payload.email)
    except Exception as exc:
        _raise_auth_error(exc)

    return {"message": "Password reset email sent if the account exists."}


@router.post("/resend-verification", response_model=AuthMessage)
def resend_verification(payload: ResendVerificationRequest):
    supabase = get_supabase_client()
    request_payload: dict[str, Any] = {
        "type": "signup",
        "email": payload.email,
    }

    redirect_to = get_auth_redirect_url(payload.email_redirect_to)
    if redirect_to:
        request_payload["options"] = {"email_redirect_to": redirect_to}

    try:
        supabase.auth.resend(request_payload)
    except Exception as exc:
        _raise_auth_error(exc)

    return {"message": "Verification email resent if the signup request exists."}
