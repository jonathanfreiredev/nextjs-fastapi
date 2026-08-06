from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from ..users.users_schemas import UserDto

from ..users import users_service
from .auth_constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from .auth_schemas import Token

# OAUTH2.0
password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FUNCTIONS

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({
        "exp": expire, 
        "iat": datetime.now(timezone.utc)
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_token(db: AsyncSession, username: str, password: str):
    user = await authenticate_user(db, username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await users_service.get_user(db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def logout_all_sessions(db: AsyncSession, username: str):
    user = await users_service.get_user(db, username)

    user.tokens_valid_after = datetime.now(timezone.utc)
    
    await db.commit()

    return {"message": "All sessions closed on all devices"}