from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_active_user
from .auth_schemas import Token
from ..db.db import get_async_db_session
from ..users.users_schemas import CreateUserDto, LoginUserDto, UserDto
from . import auth_service

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/signup")
async def create_user_post(
    data: CreateUserDto,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> Token:
    return await auth_service.signup(db, data)

@auth_router.post("/login")
async def login(
    data: LoginUserDto,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> Token:
    return await auth_service.login(db, data)

@auth_router.post("/update-token")
async def update_token(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> Token:
    return await auth_service.update_token(db, email=current_user.email)

@auth_router.post("/logout-all")
async def logout_all_sessions(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
):  
    return await auth_service.logout_all_sessions(db, email=current_user.email)