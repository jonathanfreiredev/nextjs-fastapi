import hashlib
import secrets
import uuid
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.constants import REFRESH_TOKEN_EXPIRE_DAYS
from app.auth.models import RefreshToken
from app.db.models import utcnow
from app.users.models import User


def _hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


async def issue(db: AsyncSession, user: User) -> str:
    """Create a refresh token for the user and return its raw value."""
    raw_token = secrets.token_urlsafe(48)

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=_hash(raw_token),
            expires_at=utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    await db.commit()

    return raw_token


async def consume(db: AsyncSession, raw_token: str) -> User:
    """Validate a refresh token, revoke it (rotation) and return its user."""
    stmt = select(RefreshToken).where(RefreshToken.token_hash == _hash(raw_token))
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()

    if token is None or token.revoked_at is not None or token.expires_at <= utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    token.revoked_at = utcnow()

    user = await db.get(User, token.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    await db.commit()

    return user


async def revoke(db: AsyncSession, raw_token: str) -> None:
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.token_hash == _hash(raw_token), RefreshToken.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    await db.execute(stmt)
    await db.commit()


async def revoke_all_for_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    await db.execute(stmt)
    await db.commit()
