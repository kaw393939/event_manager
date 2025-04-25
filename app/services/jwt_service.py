# app/services/jwt_service.py
from builtins import dict, str
import jwt
from datetime import datetime, timedelta
from settings.config import settings

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    # Convert role to uppercase before encoding the JWT
    if 'role' in to_encode:
        to_encode['role'] = to_encode['role'].upper()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

from jwt import ExpiredSignatureError, PyJWTError

def decode_token(token: str):
    try:
        # Decode the JWT token
        decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return decoded
    except ExpiredSignatureError:
        # Return specific message when token is expired
        return {"error": "Token has expired"}
    except PyJWTError:
        # Return general error message for other token issues
        return {"error": "Invalid token"}

