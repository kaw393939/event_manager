import jwt
from datetime import datetime, timedelta

def create_access_token(*, data: dict, expires_delta: timedelta = None) -> str:
    # Use a local import to avoid circular dependencies.
    from app.dependencies import get_settings
    settings = get_settings()

    to_encode = data.copy()
    # Convert the role value properly:
    if 'role' in to_encode:
        role = to_encode['role']
        # If role is an enum (has a value attribute), use its value.
        if hasattr(role, "value"):
            to_encode['role'] = role.value.upper()
        else:
            to_encode['role'] = str(role).upper()

    # Set token expiration
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})

    # Use the correct secret key and algorithm from settings.
    token = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token

def decode_token(token: str) -> dict:
    from app.dependencies import get_settings
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
