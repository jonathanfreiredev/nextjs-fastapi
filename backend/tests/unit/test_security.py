from app.auth.security import get_password_hash, verify_password


def test_hash_is_not_the_plain_password():
    assert get_password_hash("supersecret") != "supersecret"


def test_hashes_are_salted():
    # Two hashes of the same password must differ, otherwise the salt is not working.
    assert get_password_hash("supersecret") != get_password_hash("supersecret")


def test_verify_accepts_the_correct_password():
    hashed = get_password_hash("supersecret")

    assert verify_password("supersecret", hashed) is True


def test_verify_rejects_a_wrong_password():
    hashed = get_password_hash("supersecret")

    assert verify_password("wrongpassword", hashed) is False
