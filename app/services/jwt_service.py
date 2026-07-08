from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status

class JWTService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        from app.dependencies import get_settings
        settings = get_settings()
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        # Add role if not present
        if "role" not in to_encode:
            to_encode["role"] = "AUTHENTICATED"
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        from app.dependencies import get_settings
        settings = get_settings()
        
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def decode_token(token: str) -> dict:
        """Alias for verify_token to maintain backwards compatibility"""
        return JWTService.verify_token(token)
