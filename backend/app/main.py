from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from .users.router import users_router
from .auth.router import auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)


