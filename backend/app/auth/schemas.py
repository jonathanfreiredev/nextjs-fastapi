import uuid

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    full_name: str | None = None


class UserCreate(schemas.BaseUserCreate):
    full_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    full_name: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
