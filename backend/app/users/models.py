from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import BaseModel, utcnow


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(default=None)
    full_name: Mapped[str | None] = mapped_column(default=None)
    disabled: Mapped[bool | None] = mapped_column(default=None)
    hashed_password: Mapped[str]

    # A callable default: evaluated per insert, not once at import time.
    tokens_valid_after: Mapped[datetime] = mapped_column(default=utcnow)
