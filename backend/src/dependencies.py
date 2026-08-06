from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_async_db_session

from .auth.auth_constants import ALGORITHM, SECRET_KEY
from .auth.auth_service import bearer_scheme
from .users.users_schemas import UserDto
from .users import users_service

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)], 
    db: Annotated[AsyncSession, Depends(get_async_db_session)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception
    
    user = await users_service.get_user(db, email=email)
    if user is None:
        raise credentials_exception

    token_iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

    if token_iat < user.tokens_valid_after:
        raise credentials_exception
    
    return UserDto.model_validate(user)

async def get_current_active_user(
    current_user: Annotated[UserDto, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user