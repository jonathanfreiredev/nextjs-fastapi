import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db_session

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["health"])


@health_router.get("/health", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    """Report that the process is running.

    Checks nothing external on purpose: if this fails, the orchestrator should
    restart the container, not merely stop routing traffic to it.
    """
    return {"status": "ok"}


@health_router.get("/health/ready", summary="Readiness probe")
async def readiness(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> dict[str, str]:
    """Report whether the service can serve traffic (the database is reachable)."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        # Probes run frequently, so log at debug to avoid flooding when the
        # database is down. The 503 response is the signal itself.
        logger.debug("Readiness check failed", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "down"}

    return {"status": "ok", "database": "up"}
