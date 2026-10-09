import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.keys import JWKS
from app.auth.router import auth_router
from app.users.router import users_router

# Show application logs (e.g. the development email sender) in the console.
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/.well-known/jwks.json")
async def jwks() -> dict:
    """Public keys the frontend uses to verify access tokens locally."""
    return JWKS


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js in dev
        "https://mi-dominio.com",  # frontend in prod
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
