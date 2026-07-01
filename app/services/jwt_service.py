# app/services/jwt_service.py
from builtins import dict, str
import jwt
from datetime import datetime, timedelta
from settings.config import settings

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT access token with optional expiration time.

    Args:
        data (dict): The data to encode into the token.
        expires_delta (timedelta, optional): Custom expiration time. Defaults to None.

    Returns:
        str: Encoded JWT token.
    """
    # Prepare data for encoding
    to_encode = data.copy()
    if 'role' in to_encode:  # Ensure the role is in uppercase
        to_encode['role'] = to_encode['role'].upper()

    # Set expiration time
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})

    # Encode and return the JWT
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str):
    """
    Decodes a JWT token.

    Args:
        token (str): The encoded JWT token.

    Returns:
        dict or None: Decoded token data if valid, otherwise None.
    """
    try:
        # Decode the JWT token
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        # Return None if decoding fails
        return None
