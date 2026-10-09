from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(default=None)
    hashed_password: Mapped[str]

    # Expected by FastAPI Users' user protocol.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
