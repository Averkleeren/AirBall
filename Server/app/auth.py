from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
_MAX_BCRYPT_LEN = 72


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:_MAX_BCRYPT_LEN], hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:_MAX_BCRYPT_LEN])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return {"email": email} if email else None
    except JWTError:
        return None


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract bearer token from an Authorization header value."""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None
