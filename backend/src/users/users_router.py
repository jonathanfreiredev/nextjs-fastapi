from typing import Annotated

from fastapi import APIRouter, Depends

from ..dependencies import get_current_active_user
from .users_schemas import UserDto


users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/me/")
async def read_users_me(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
) -> UserDto:
    return current_user


@users_router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[UserDto, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.full_name}]