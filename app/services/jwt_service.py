# app/services/jwt_service.py
from datetime import datetime, timedelta
from typing import Optional
import jwt  # make sure you're using PyJWT
from settings.config import settings


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if 'role' in to_encode:
        to_encode['role'] = str(to_encode['role']).upper()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
