"""API dependencies."""
import time
import uuid
from collections import defaultdict
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


# ── rate limiting ────────────────────────────────────────────────────────────
# ponytail: in-process sliding window, no Redis. Correct for a single uvicorn
# worker; behind a load balancer each worker gets its own budget, so swap in a
# shared store if this ever runs replicated.
_RATE_LIMIT = 10
_RATE_WINDOW_S = 60
_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(request: Request) -> None:
    """Cap unauthenticated auth attempts per client IP."""
    # ponytail: raw peer address, no X-Forwarded-For handling. Behind a load
    # balancer that doesn't forward the real client IP, every request
    # collapses onto one key. Add a vetted X-Forwarded-For read (trusting
    # only a known proxy hop) if this ever sits behind one.
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()

    # Evict clients whose whole window has already expired, so the dict stays
    # bounded to currently-active clients instead of every IP ever seen.
    for key in [k for k, hits in _hits.items() if not any(now - t < _RATE_WINDOW_S for t in hits)]:
        del _hits[key]

    recent = [t for t in _hits[client] if now - t < _RATE_WINDOW_S]
    if len(recent) >= _RATE_LIMIT:
        _hits[client] = recent
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again in a minute.",
            headers={"Retry-After": str(_RATE_WINDOW_S)},
        )

    recent.append(now)
    _hits[client] = recent
