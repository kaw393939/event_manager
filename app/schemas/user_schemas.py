from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import List, Optional
from app.schemas.link_schema import Link
from app.schemas.pagination_schema import EnhancedPagination
import re
import uuid

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr = Field(...)
    full_name: Optional[str] = Field(None, max_length=100, pattern="^[a-zA-Z\s'-]+$")
    bio: Optional[str] = Field(None, max_length=500)
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profile_pictures/john_doe_updated.jpg")

    @validator('profile_picture_url', pre=True, always=True)
    def validate_profile_picture_url(cls, v):
        if v and not re.search(r"\.(jpg|jpeg|png)$", v):
            raise ValueError("Profile picture URL must point to a valid image file (JPEG, PNG).")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8 or not re.search(r"[A-Z]", v) or not re.search(r"[a-z]", v) or not re.search(r"\d", v) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None)
    full_name: Optional[str] = Field(None, max_length=100, pattern="^[a-zA-Z\s'-]+$")
    bio: Optional[str] = Field(None, max_length=500)
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profile_pictures/john_doe_updated.jpg")

    @validator('profile_picture_url', pre=True, always=True)
    def validate_profile_picture_url(cls, v):
        if v and not re.search(r"\.(jpg|jpeg|png)$", v):
            raise ValueError("Profile picture URL must point to a valid image file (JPEG, PNG).")
        return v

class UserResponse(UserBase):
    id: uuid.UUID = Field(...)
    last_login_at: Optional[datetime] = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    links: List[Link] = Field(default_factory=list)

class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(...)
    pagination: EnhancedPagination = Field(...)

class LoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class ErrorResponse(BaseModel):
    error: str = Field(...)
    details: Optional[str] = Field(None)
