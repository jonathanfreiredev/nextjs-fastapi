import uuid

import jwt
import pytest

from app.auth.backend import get_jwt_strategy
from app.auth.constants import ALGORITHM
from app.auth.keys import KID, public_key
from app.users.models import User

pytestmark = pytest.mark.anyio


async def test_jwt_strategy_signs_rs256_tokens_with_the_user_id_as_subject():
    user = User(id=uuid.uuid4(), email="jane@example.com", hashed_password="x")

    token = await get_jwt_strategy().write_token(user)

    header = jwt.get_unverified_header(token)
    assert header["alg"] == "RS256"
    assert header["kid"] == KID

    payload = jwt.decode(token, public_key, algorithms=[ALGORITHM], audience="fastapi-users:auth")
    assert payload["sub"] == str(user.id)
    assert payload["aud"] == ["fastapi-users:auth"]
