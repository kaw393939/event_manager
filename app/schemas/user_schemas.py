from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, HttpUrl, Field, constr, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID
import re


from app.utils.nickname_gen import generate_nickname

class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url


class UserBase(BaseModel):
    username: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[constr(min_length=3, pattern=r"^[A-Za-z0-9_-]+$")] = Field(
        None, example="jdoe_42"
    )
    first_name: str = Field(..., example="John")
    last_name:  str = Field(..., example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer.")
    profile_picture_url: Optional[str] = Field(
        None, example="https://example.com/profiles/john.jpg"
    )
    linkedin_profile_url: Optional[str] = Field(
        None, example="https://linkedin.com/in/johndoe"
    )
    github_profile_url: Optional[str] = Field(
        None, example="https://github.com/johndoe"
    )

    # ensure any provided URLs are valid
    _validate_urls = validator(
        "profile_picture_url", "linkedin_profile_url", "github_profile_url",
        pre=True, allow_reuse=True
    )(validate_url)

    model_config = {
        "from_attributes": True,   # allow ORM objects → schema
    }

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="Secure*Pass123")


class UserUpdate(BaseModel):
    username: Optional[EmailStr] = Field(None, example="new.email@example.com")
    nickname: Optional[constr(min_length=3, pattern=r"^[A-Za-z0-9_-]+$")] = Field(
        None, example="jdoe_43"
    )
    first_name: Optional[str]             = None
    last_name:  Optional[str]             = None
    bio:        Optional[str]             = None
    profile_picture_url: Optional[str]    = None
    linkedin_profile_url: Optional[str]   = None
    github_profile_url: Optional[str]     = None

    @root_validator(pre=True)
    def require_one(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

    model_config = {
        "from_attributes": True,
    }

class UserResponse(UserBase):
    id:               UUID
    role:             UserRole
    is_professional:  bool
    created_at:       datetime
    last_login_at:    datetime

    model_config = {
        "from_attributes": True,
    }

class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(
        ...,
        example=[{
            "id":                "123e4567-e89b-12d3-a456-426614174000",
            "username":          "john.doe@example.com",
            "nickname":          "jdoe_42",
            "first_name":        "John",
            "last_name":         "Doe",
            "bio":               "Experienced developer",
            "profile_picture_url":"https://example.com/profiles/john.jpg",
            "linkedin_profile_url":"https://linkedin.com/in/johndoe",
            "github_profile_url":"https://github.com/johndoe",
            "role":              "AUTHENTICATED",
            "is_professional":   False,
            "created_at":        "2025-04-21T01:34:30.268953",
            "last_login_at":     "2025-04-21T01:34:30.268951"
        }]
    )
    total: int = Field(..., example=100)
    page:  int = Field(..., example=1)
    size:  int = Field(..., example=10)


class LoginRequest(BaseModel):
    username: EmailStr = Field(..., example="john.doe@example.com")
    password: str      = Field(..., min_length=8, example="Secure*Pass123")