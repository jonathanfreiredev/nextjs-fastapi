from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import refresh
from app.auth.constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from app.auth.keys import KID, private_key, public_key
from app.auth.schemas import Token
from app.auth.security import get_password_hash, verify_password
from app.db.models import utcnow
from app.users import service as users_service
from app.users.models import User
from app.users.schemas import CreateUserDto, LoginUserDto

# OAUTH2.0
DUMMY_HASH = get_password_hash("dummypassword")

bearer_scheme = HTTPBearer()

# FUNCTIONS


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = utcnow()
    expire = now + (expires_delta or timedelta(minutes=30))

    to_encode.update({"exp": expire, "iat": now})

    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM, headers={"kid": KID})


async def create_token_pair(db: AsyncSession, user: User) -> Token:
    access_token = create_access_token(
        data={"sub": user.email, "name": user.full_name},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = await refresh.issue(db, user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def signup(db: AsyncSession, data: CreateUserDto):
    user = await users_service.create_user(db, data)

    return await create_token_pair(db, user)


async def login(db: AsyncSession, data: LoginUserDto):
    user = await authenticate_user(db, data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await create_token_pair(db, user)


async def authenticate_user(db: AsyncSession, data: LoginUserDto):
    user = await users_service.get_user(db, email=data.email)
    password = data.password
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def refresh_tokens(db: AsyncSession, raw_token: str):
    user = await refresh.consume(db, raw_token)

    return await create_token_pair(db, user)


async def logout(db: AsyncSession, raw_token: str):
    await refresh.revoke(db, raw_token)

    return {"message": "Logged out"}


async def verify_token(db: AsyncSession, token: str):
    try:
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await users_service.get_user(db, email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_iat = datetime.fromtimestamp(payload["iat"], tz=UTC)

        if token_iat < user.tokens_valid_after:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


async def logout_all_sessions(db: AsyncSession, email: str):
    user = await users_service.get_user(db, email)

    user.tokens_valid_after = utcnow()
    await db.commit()

    await refresh.revoke_all_for_user(db, user.id)

    return {"message": "All sessions closed on all devices"}
