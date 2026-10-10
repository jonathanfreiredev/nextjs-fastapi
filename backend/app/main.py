from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.health.router import health_router
from app.logging_config import configure_logging
from app.middleware.request_id import RequestIdMiddleware
from app.users.router import users_router

# Structured logging for the whole process (app + uvicorn).
configure_logging()

app = FastAPI()

# Unauthenticated probes for orchestrators and uptime monitors.
app.include_router(health_router)
app.include_router(users_router)

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

# Added last so it is the outermost middleware: the request id is bound (and the
# access log emitted) around everything, including CORS.
app.add_middleware(RequestIdMiddleware)
