from datetime import datetime

from pydantic import BaseModel, ConfigDict

class UserDto(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    tokens_valid_after: datetime

    model_config = ConfigDict(from_attributes=True)

class CreateUserDto(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str