"""add fastapi-users fields and drop refresh tokens

Revision ID: 38f47880319b
Revises: f595128119f7
Create Date: 2026-10-08 18:40:26.860882

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "38f47880319b"
down_revision: str | Sequence[str] | None = "f595128119f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "users",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # Existing accounts keep working: active unless they were disabled, and
    # already verified so the migration does not lock anyone out.
    op.execute("UPDATE users SET is_active = NOT COALESCE(disabled, false)")
    op.execute("UPDATE users SET is_verified = true")

    op.alter_column("users", "email", existing_type=sa.VARCHAR(), nullable=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.drop_column("users", "disabled")
    op.drop_column("users", "tokens_valid_after")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "tokens_valid_after",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column("users", sa.Column("disabled", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.alter_column("users", "email", existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_active")
    op.create_table(
        "refresh_tokens",
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("token_hash", sa.VARCHAR(length=64), autoincrement=False, nullable=False),
        sa.Column(
            "expires_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False
        ),
        sa.Column(
            "revoked_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True
        ),
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_refresh_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_refresh_tokens_token_hash")),
    )
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)
