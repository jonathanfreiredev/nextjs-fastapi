from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db_session
from app.dependencies import get_current_active_user
from app.users import service as users_service
from app.users.schemas import UpdateUserDto, UpdateUserPasswordDto, UserDto

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me/")
async def read_users_me(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
) -> UserDto:
    return current_user


@users_router.put("/me/")
async def update_user_profile(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
    user_update: UpdateUserDto,
) -> UserDto:
    return await users_service.update_user(db=db, email=current_user.email, schema=user_update)


@users_router.put("/me/password/")
async def update_user_password(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
    password_update: UpdateUserPasswordDto,
) -> UserDto:
    updated_user = await users_service.update_user_password(
        db=db, email=current_user.email, schema=password_update
    )

    return updated_user
