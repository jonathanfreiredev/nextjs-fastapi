from fastapi import FastAPI
from .users.users_router import users_router
from .auth.auth_router import auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)


