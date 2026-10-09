import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users.manager import BaseUserManager

from app.auth.backend import current_active_user, fastapi_users
from app.auth.schemas import ChangePasswordRequest, UserRead, UserUpdate
from app.auth.users import get_user_manager
from app.users.models import User

users_router = APIRouter(prefix="/users", tags=["users"])

users_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))


@users_router.put("/me/password/", response_model=UserRead)
async def change_password(
    data: ChangePasswordRequest,
    user: Annotated[User, Depends(current_active_user)],
    user_manager: Annotated[BaseUserManager[User, uuid.UUID], Depends(get_user_manager)],
) -> User:
    """Change the current user's password, requiring the old one."""
    verified, _ = user_manager.password_helper.verify_and_update(
        data.old_password, user.hashed_password
    )
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    return await user_manager.update(UserUpdate(password=data.new_password), user, safe=True)
