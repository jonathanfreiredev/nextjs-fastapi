from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.auth.schemas import RefreshTokenRequest, Token
from app.db.session import get_async_db_session
from app.dependencies import get_current_active_user
from app.users.schemas import CreateUserDto, LoginUserDto, UserDto

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


@auth_router.post("/refresh")
async def refresh(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> Token:
    return await auth_service.refresh_tokens(db, data.refresh_token)


@auth_router.post("/logout")
async def logout(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
):
    return await auth_service.logout(db, data.refresh_token)


@auth_router.post("/logout-all")
async def logout_all_sessions(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
):
    return await auth_service.logout_all_sessions(db, email=current_user.email)
