from fastapi import APIRouter

from app.auth.backend import auth_backend, fastapi_users
from app.auth.schemas import UserCreate, UserRead

auth_router = APIRouter(prefix="/auth", tags=["auth"])

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
auth_router.include_router(fastapi_users.get_verify_router(UserRead))
auth_router.include_router(fastapi_users.get_reset_password_router())
