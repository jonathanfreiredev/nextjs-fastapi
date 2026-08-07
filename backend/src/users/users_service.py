from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .users_schemas import CreateUserDto, UpdateUserDto, UpdateUserPasswordDto
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

async def update_user(db: AsyncSession, email: str, schema: UpdateUserDto):
    user = await get_user(db, email)

    user_with_new_email = await get_user(db, schema.email)

    print(user.email, schema.email)

    if user_with_new_email and user_with_new_email.email != email:
        raise HTTPException(status_code=404, detail="User with this email already exists")

    if schema.email:
        user.email = schema.email
    if schema.full_name:
        user.full_name = schema.full_name

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def update_user_password(db: AsyncSession, email: str, schema: UpdateUserPasswordDto):
    user = await get_user(db, email)

    if not auth_service.verify_password(schema.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    hashed_password = auth_service.get_password_hash(schema.new_password)
    user.hashed_password = hashed_password

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user