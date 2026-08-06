from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column

from ..db.models import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str]
    email: Mapped[str | None] = mapped_column(default=None)
    full_name: Mapped[str | None] = mapped_column(default=None)
    disabled: Mapped[bool | None] = mapped_column(default=None)
    hashed_password: Mapped[str]

    tokens_valid_after: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))