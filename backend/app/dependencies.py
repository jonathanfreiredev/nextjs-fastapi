from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import bearer_scheme, verify_token
from app.db.session import get_async_db_session
from app.users.schemas import UserDto


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
):
    token = credentials.credentials
    user = await verify_token(db, token)

    return UserDto.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserDto, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
