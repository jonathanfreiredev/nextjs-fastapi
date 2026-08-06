from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .users_schemas import CreateUserDto
from .users_models import User
from ..auth import auth_service

async def get_user(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, schema: CreateUserDto):
    user_exists = await get_user(db, email=schema.email)

    if user_exists:
        raise HTTPException(status_code=404, detail="User already exists")

    hashed_password = auth_service.get_password_hash(schema.password)

    user = User(
        hashed_password=hashed_password,
        email=schema.email,
        full_name=schema.full_name
    )
    
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user