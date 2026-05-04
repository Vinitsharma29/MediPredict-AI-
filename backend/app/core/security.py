import base64
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Support verifying older bcrypt hashes while generating new PBKDF2 hashes.
# (bcrypt has a 72-byte password limit; PBKDF2 does not.)
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
ALGO = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(subject: dict[str, Any], expires_minutes: int = 60 * 24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGO)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGO])


def _fernet_from_key(key: str) -> Fernet:
    raw = key.encode("utf-8")
    if len(raw) < 32:
        raw = raw.ljust(32, b"0")
    raw = raw[:32]
    fkey = base64.urlsafe_b64encode(raw)
    return Fernet(fkey)


_fernet = _fernet_from_key(settings.field_enc_key)


def encrypt_text(value: str | None) -> str | None:
    if value is None:
        return None
    token = _fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet.decrypt(value.encode("utf-8")).decode("utf-8")
