from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import re

from app.utils.nickname_gen import generate_nickname

class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

def validate_url(url: Optional[str]) -> Optional[str]:
    """Validate URL format if provided."""
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url

# Common field definitions
class UserFields:
    """Centralized field definitions to avoid repetition."""
    email = lambda required=True: Field(
        ... if required else None,
        example="john.doe@example.com"
    )
    
    nickname = lambda: Field(
        None,
        min_length=3,
        pattern=r'^[\w-]+$',
        example=generate_nickname()
    )
    
    first_name = lambda: Field(None, example="John")
    last_name = lambda: Field(None, example="Doe")
    bio = lambda: Field(
        None,
        example="Experienced software developer specializing in web applications."
    )
    
    profile_picture_url = lambda: Field(
        None,
        example="https://example.com/profiles/john.jpg"
    )
    
    linkedin_profile_url = lambda: Field(
        None,
        example="https://linkedin.com/in/johndoe"
    )
    
    github_profile_url = lambda: Field(
        None,
        example="https://github.com/johndoe"
    )
    
    password = lambda required=True: Field(
        ... if required else None,
        example="Secure*1234"
    )
    
    id = lambda: Field(..., example=uuid.uuid4())
    
    role = lambda: Field(
        default=UserRole.AUTHENTICATED,
        example="AUTHENTICATED"
    )
    
    is_professional = lambda: Field(default=False, example=True)


class BaseUserModel(BaseModel):
    """Base model with common configurations."""
    class Config:
        from_attributes = True


class UserBase(BaseUserModel):
    """Base user model with common fields."""
    email: EmailStr = UserFields.email()
    nickname: Optional[str] = UserFields.nickname()
    first_name: Optional[str] = UserFields.first_name()
    last_name: Optional[str] = UserFields.last_name()
    bio: Optional[str] = UserFields.bio()
    profile_picture_url: Optional[str] = UserFields.profile_picture_url()
    linkedin_profile_url: Optional[str] = UserFields.linkedin_profile_url()
    github_profile_url: Optional[str] = UserFields.github_profile_url()

    # Apply URL validation to all URL fields
    _validate_urls = validator(
        'profile_picture_url', 
        'linkedin_profile_url', 
        'github_profile_url', 
        pre=True, 
        allow_reuse=True
    )(validate_url)


class UserCreate(UserBase):
    """Model for user creation."""
    password: str = UserFields.password()


class UserUpdate(BaseUserModel):
    """Model for user updates with all fields optional."""
    email: Optional[EmailStr] = UserFields.email(required=False)
    nickname: Optional[str] = UserFields.nickname()
    first_name: Optional[str] = UserFields.first_name()
    last_name: Optional[str] = UserFields.last_name()
    bio: Optional[str] = UserFields.bio()
    profile_picture_url: Optional[str] = UserFields.profile_picture_url()
    linkedin_profile_url: Optional[str] = UserFields.linkedin_profile_url()
    github_profile_url: Optional[str] = UserFields.github_profile_url()
    
    # Apply URL validation to all URL fields
    _validate_urls = validator(
        'profile_picture_url', 
        'linkedin_profile_url', 
        'github_profile_url', 
        pre=True, 
        allow_reuse=True
    )(validate_url)

    @root_validator(pre=True)
    def check_at_least_one_value(cls, values):
        """Ensure at least one field is provided for update."""
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values


class UserResponse(UserBase):
    """Model for user responses with additional fields."""
    id: uuid.UUID = UserFields.id()
    role: UserRole = UserFields.role()
    is_professional: Optional[bool] = UserFields.is_professional()


class LoginRequest(BaseModel):
    """Model for login requests."""
    email: str = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure*1234")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str = Field(..., example="Not Found")
    details: Optional[str] = Field(None, example="The requested resource was not found.")


class UserListResponse(BaseModel):
    """Model for paginated user list responses."""
    items: List[UserResponse] = Field(
        ...,
        example=[
            {
                "id": uuid.uuid4(),
                "nickname": generate_nickname(),
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "bio": "Experienced developer",
                "role": "AUTHENTICATED",
                "profile_picture_url": "https://example.com/profiles/john.jpg",
                "linkedin_profile_url": "https://linkedin.com/in/johndoe",
                "github_profile_url": "https://github.com/johndoe",
                "is_professional": True
            }
        ]
    )
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)