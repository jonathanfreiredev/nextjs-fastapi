from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from ..users.users_schemas import CreateUserDto, LoginUserDto
from ..users import users_service
from .auth_constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from .auth_schemas import Token

# OAUTH2.0
password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

bearer_scheme = HTTPBearer()

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

async def signup(db: AsyncSession, data: CreateUserDto):
    user = await users_service.create_user(db, data)

    return await get_token(email=user.email)

async def login(db: AsyncSession, data: LoginUserDto):
    is_authenticated = await authenticate_user(db, email=data.email, password=data.password)
    
    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await get_token(email=data.email)

async def authenticate_user(db: AsyncSession, data: LoginUserDto):
    user = await users_service.get_user(db, email=data.email)
    password = data.password
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return True

async def get_token(email: str):    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

async def logout_all_sessions(db: AsyncSession, email: str):
    user = await users_service.get_user(db, email)

    user.tokens_valid_after = datetime.now(timezone.utc)
    
    await db.commit()

    return {"message": "All sessions closed on all devices"}