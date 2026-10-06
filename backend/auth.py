"""
Security helper for the Student Marketplace.
Uses bcrypt for password hashing.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models import get_seller_by_id, get_item_by_id
from utilities import get_required_env

load_dotenv()

SECRET_KEY = get_required_env("SECRET_KEY")
if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY must be at least 32 characters. "
        'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# auto_error=False: we raise our own 401 (with WWW-Authenticate) when the
# header is missing, because the built-in error status differs between
bearer_scheme = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """hash a plaintext password"""
    raw = plain.encode("utf-8")
    if len(raw) > 72:
        # bcrypt only uses the first 72 bytes; refuse instead of silently truncating
        raise ValueError("Password exceeds bcrypt's 72-byte limit.")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12)).decode("utf-8")

def verify_password(plain: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    raw = plain.encode("utf-8")
    if len(raw) > 72:
        return False
    try:
        return bcrypt.checkpw(raw, password_hash.encode("utf-8"))
    except ValueError:
        # malformed hash in the database
        return False

# Compared against when a username doesn't exist, so login takes the same
# time whether or not the account is real (prevents username enumeration).
DUMMY_HASH = hash_password("not-a-real-password")

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------

def create_token(seller_id: int) -> str:
    """Create a signed access token for a seller."""
    now = datetime.now(timezone.utc)

    lifetime = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(seller_id),  # seller id
        "iat": now, # when the token was created
        "exp": now + lifetime, # when the token expires
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    """FastAPI dependency: return the seller identified by the Bearer token."""
    if credentials is None:
        raise _unauthorized("Not authenticated")

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY, algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        seller_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:  # must come before InvalidTokenError (its parent)
        raise _unauthorized("Token has expired") from None
    except (jwt.InvalidTokenError, ValueError):
        raise _unauthorized("Invalid token") from None

    seller = get_seller_by_id(seller_id)

    if seller is None:
        raise _unauthorized("Invalid token")

    return seller

# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------

def require_item_owner(item_id: int, current_seller: dict = Depends(get_current_user)) -> None:
    """
    FastAPI dependency for routes with an {item_id} path parameter.
    401 if the token is missing or invalid (raised by get_current_user),
    404 if the item doesn't exist, 403 if it belongs to another seller.
    """
    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["seller_id"] != current_seller["id"]:
        raise HTTPException(status_code=403, detail="You do not own this item")