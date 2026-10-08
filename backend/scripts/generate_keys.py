"""Generate the RSA key pair used to sign JWTs.

Usage:
    uv run python scripts/generate_keys.py

Writes keys/private.pem and keys/public.pem (both gitignored). In production,
put the private key contents in the JWT_PRIVATE_KEY environment variable instead
of shipping the file.
"""

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS_DIR = Path(__file__).resolve().parent.parent / "keys"


def main() -> None:
    KEYS_DIR.mkdir(exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    (KEYS_DIR / "private.pem").write_bytes(private_pem)
    (KEYS_DIR / "public.pem").write_bytes(public_pem)

    print(f"Wrote {KEYS_DIR / 'private.pem'} and {KEYS_DIR / 'public.pem'}")


if __name__ == "__main__":
    main()
