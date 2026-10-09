from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import TokenClaims
from app.users.models import User


async def get_or_create_user(session: AsyncSession, claims: TokenClaims) -> User:
    """Return the profile for the authenticated subject, creating it on first use.

    Supabase owns signup, so the local profile is provisioned just-in-time: the
    first authenticated request creates it and the mirrored email is kept in
    sync on later requests.
    """
    user = await session.scalar(select(User).where(User.supabase_user_id == claims.subject))

    if user is None:
        user = User(
            supabase_user_id=claims.subject,
            email=claims.email,
            full_name=claims.metadata.get("full_name"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    if claims.email and user.email != claims.email:
        user.email = claims.email
        await session.commit()
        await session.refresh(user)

    return user
