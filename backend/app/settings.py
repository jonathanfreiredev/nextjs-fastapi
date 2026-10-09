from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    env: str = "development"
    database_url: str
    # Symmetric secret FastAPI Users uses to sign the email-verification and
    # password-reset tokens.
    auth_secret: str
    # Base URL of the frontend, used to build the links sent by email.
    frontend_url: str = "http://localhost:3000"
    # PEM contents of the RSA private key used to sign JWTs. When unset, the key
    # is read from keys/private.pem (see app/auth/keys.py).
    jwt_private_key: str | None = None

    @property
    def debug(self) -> bool:
        return self.env == "development"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
