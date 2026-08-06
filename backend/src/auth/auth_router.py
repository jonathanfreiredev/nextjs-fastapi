from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_active_user
from .auth_schemas import Token
from ..db.db import get_async_db_session
from ..users.users_schemas import UserDto
from . import auth_service

auth_router = APIRouter()

@auth_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> Token:
    return await auth_service.get_token(db, username=form_data.username, password=form_data.password)

@auth_router.post("/logout-all")
async def logout_all_sessions(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
):  
    return await auth_service.logout_all_sessions(db, username=current_user.username)