import base64
import hashlib
import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth.constants import ALGORITHM
from app.settings import BASE_DIR, settings

logger = logging.getLogger(__name__)

PRIVATE_KEY_FILE = BASE_DIR / "keys" / "private.pem"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _load_private_key() -> rsa.RSAPrivateKey:
    if settings.jwt_private_key:
        return serialization.load_pem_private_key(settings.jwt_private_key.encode(), password=None)

    if PRIVATE_KEY_FILE.exists():
        return serialization.load_pem_private_key(PRIVATE_KEY_FILE.read_bytes(), password=None)

    if settings.debug:
        logger.warning(
            "No JWT private key configured; generating an ephemeral one. Tokens "
            "will be invalidated on restart. Run scripts/generate_keys.py or set "
            "JWT_PRIVATE_KEY for stable keys."
        )
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    raise RuntimeError(
        "No JWT private key configured. Set JWT_PRIVATE_KEY or provide keys/private.pem."
    )


def _public_jwk(public_key: rsa.RSAPublicKey) -> dict:
    numbers = public_key.public_numbers()
    n = _b64url(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big"))
    e = _b64url(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big"))
    kid = _b64url(hashlib.sha256(f"{n}.{e}".encode()).digest())[:16]

    return {"kty": "RSA", "use": "sig", "alg": ALGORITHM, "kid": kid, "n": n, "e": e}


private_key = _load_private_key()
public_key = private_key.public_key()

# PEM serializations, as expected by FastAPI Users' JWTStrategy.
PRIVATE_KEY_PEM = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
PUBLIC_KEY_PEM = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

JWKS = {"keys": [_public_jwk(public_key)]}
KID = JWKS["keys"][0]["kid"]
