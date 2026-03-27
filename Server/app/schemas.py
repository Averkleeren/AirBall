from pydantic import BaseModel, EmailStr
from typing import Any, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    email_redirect_to: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr
    redirect_to: Optional[str] = None

class ResendVerificationRequest(BaseModel):
    email: EmailStr
    email_redirect_to: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    email_confirmed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    raw_user_meta_data: dict[str, Any] = {}

    class Config:
        from_attributes = True

class AuthMessage(BaseModel):
    message: str

class SignupResponse(AuthMessage):
    user: UserResponse
    email_verification_required: bool = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: Optional[int] = None
    expires_at: Optional[int] = None
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
