from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import TokenClaims, get_token_claims
from app.db.session import get_async_db_session
from app.users.models import User
from app.users.service import get_or_create_user


async def get_current_user(
    claims: Annotated[TokenClaims, Depends(get_token_claims)],
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> User:
    """Resolve the bearer token to a local profile, provisioning it if needed."""
    return await get_or_create_user(session, claims)
