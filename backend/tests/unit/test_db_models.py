from app.db.models import utcnow
from app.users.models import User


def test_utcnow_is_truncated_to_whole_seconds():
    # JWT `iat`/`exp` have second precision, so we keep timestamps on the same grid.
    assert utcnow().microsecond == 0


def test_tokens_valid_after_default_is_a_callable():
    # A scalar default would freeze every row to the app's import time.
    default = User.__table__.c.tokens_valid_after.default
    assert default.is_callable
