from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.db import get_async_db_session
from ..dependencies import get_current_active_user
from .users_schemas import UserDto, CreateUserDto
from . import users_service


users_router = APIRouter()

@users_router.post("/users")
async def create_user_post(
    data: CreateUserDto,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> UserDto:
    return await users_service.create_user(db, data)


@users_router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
) -> UserDto:
    return current_user


@users_router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]