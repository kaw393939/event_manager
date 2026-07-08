from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator, constr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import re

from app.utils.nickname_gen import generate_nickname

# Enum to define possible user roles
class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

# Validator function for URL format
def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url

# Base model class for user data
class UserBase(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")  # User's email address
    nickname: Optional[str] = Field(None, min_length=3, max_length=20, pattern=r'^[\w-]+$', example='john_doe_456')  # Optional nickname
    first_name: Optional[str] = Field(None, example="John")  # Optional first name
    last_name: Optional[str] = Field(None, example="Doe")  # Optional last name
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")  # Optional bio
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")  # Optional profile picture URL
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")  # Optional LinkedIn profile URL
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")  # Optional GitHub profile URL
    role: Optional[UserRole] = Field(UserRole.AUTHENTICATED, example="AUTHENTICATED")  # User's role

    # Validator to check URL format for profile picture and social media URLs
    _validate_urls = validator('profile_picture_url', 'linkedin_profile_url', 'github_profile_url', pre=True, allow_reuse=True)(validate_url)
 
    class Config:
        from_attributes = True  # Allows Pydantic models to be created from attributes of other objects

# Model class for creating a new user
class UserCreate(UserBase):
    email: EmailStr = Field(..., example="john.doe@example.com")  # User's email address
    password: str = Field(..., min_length=8, example="Secure*1234")  # User's password with minimum length and complexity requirements
    nickname: Optional[str] = Field(None, min_length=3, max_length=20, pattern=r'^[\w-]+$', example="john_doe_456")  # Optional nickname

    # Validator for password complexity
    @validator('password')
    def password_complexity(cls, value):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise ValueError('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.')
        return value

    # Validator for nickname format
    @validator('nickname')
    def nickname_characters(cls, value):
        if not re.match(r'^[\w-]+$', value):
            raise ValueError("Nickname must contain only alphanumeric characters, underscores, and hyphens.")
        return value

# Model class for updating existing user data
class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")  # Optional email address
    nickname: Optional[str] = Field(None, min_length=3, max_length=20, pattern=r'^[\w-]+$', example="john_doe_456")  # Optional nickname
    first_name: Optional[str] = Field(None, example="John")  # Optional first name
    last_name: Optional[str] = Field(None, example="Doe")  # Optional last name
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")  # Optional bio
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")  # Optional profile picture URL
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")  # Optional LinkedIn profile URL
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")  # Optional GitHub profile URL
    password: Optional[constr(min_length=8)] = None  # Optional password with minimum length requirement
    role: Optional[UserRole] = Field(UserRole.AUTHENTICATED, example="AUTHENTICATED")  # Optional role

    # Validator for nickname format
    @validator('nickname')
    def nickname_characters(cls, value):
        if value and not re.match(r'^[\w-]+$', value):
            raise ValueError("Nickname must contain only alphanumeric characters, underscores, and hyphens.")
        return value
    
    # Validator for password complexity
    @validator('password')
    def password_complexity(cls, value):
        if value and not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise ValueError('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.')
        return value

    # Validator to ensure at least one field is provided for update
    @root_validator(pre=True)
    def check_at_least_one_value(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

# Model class for user response data
class UserResponse(UserBase):
    id: uuid.UUID = Field(..., example=uuid.uuid4())  # Unique identifier for the user
    role: UserRole = Field(default=UserRole.AUTHENTICATED, example="AUTHENTICATED")  # User's role
    email: EmailStr = Field(..., example="john.doe@example.com")  # User's email address
    nickname: Optional[str] = Field(None, min_length=3, pattern=r'^[\w-]+$', example='john_doe_456')  # Optional nickname
    is_professional: Optional[bool] = Field(default=False, example=True)  # Indicates if the user is a professional

# Model class for login request
class LoginRequest(BaseModel):
    email: str = Field(..., example="john.doe@example.com")  # User's email address
    password: str = Field(..., example="Secure*1234")  # User's password

# Model class for error response
class ErrorResponse(BaseModel):
    error: str = Field(..., example="Not Found")  # Error message
    details: Optional[str] = Field(None, example="The requested resource was not found.")  # Optional additional details about the error

# Model class for user list response
class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(..., example=[{
        "id": uuid.uuid4(), "nickname": 'john_doe_456', "email": "john.doe@example.com",
        "first_name": "John", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "last_name": "Doe", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "profile_picture_url": "https://example.com/profiles/john.jpg", 
        "linkedin_profile_url": "https://linkedin.com/in/johndoe", 
        "github_profile_url": "https://github.com/johndoe"
    }])  # List of user response objects
    total: int = Field(..., example=100)  # Total number of users
    page: int = Field(..., example=1)  # Current page number
    size: int = Field(..., example=10)  # Number of users per page
