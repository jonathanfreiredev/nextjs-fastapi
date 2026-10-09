import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.auth.constants import ACCESS_TOKEN_LIFETIME_SECONDS, ALGORITHM
from app.auth.keys import KID, PRIVATE_KEY_PEM, PUBLIC_KEY_PEM
from app.auth.users import get_user_manager
from app.users.models import User


class KidJWTStrategy(JWTStrategy[User, uuid.UUID]):
    """A JWTStrategy that stamps a `kid` header on the access token.

    The frontend resolves keys from the JWKS by `kid`, so publishing it lets the
    frontend refetch the key set automatically when the signing key rotates.
    """

    async def write_token(self, user: User) -> str:
        data: dict = {"sub": str(user.id), "aud": self.token_audience}
        if self.lifetime_seconds:
            data["exp"] = datetime.now(UTC) + timedelta(seconds=self.lifetime_seconds)

        return jwt.encode(data, self.encode_key, algorithm=self.algorithm, headers={"kid": KID})


bearer_transport = BearerTransport(tokenUrl="/auth/jwt/login")


def get_jwt_strategy() -> KidJWTStrategy:
    return KidJWTStrategy(
        secret=PRIVATE_KEY_PEM,
        public_key=PUBLIC_KEY_PEM,
        algorithm=ALGORITHM,
        lifetime_seconds=ACCESS_TOKEN_LIFETIME_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)
