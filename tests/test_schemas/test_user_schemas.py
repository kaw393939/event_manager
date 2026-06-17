from builtins import str
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

# Tests for UserBase
def test_user_base_valid():
    user_base_data = {"email": "john.doe@example.com", "nickname": "testuser"}
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid():
    user_create_data = {"email": "john.doe@example.com", "nickname": "testuser", "password": "Secure*1234"}
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid():
    user_update_data = {"email": "updated.email@example.com", "first_name": "UpdatedName"}
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid():
    user_response_data = {
        "id": "6f27bfc9-24e5-4b3e-8b90-df930e72cc04",
        "email": "john.doe@example.com",
        "nickname": "testuser",
        "role": "AUTHENTICATED"
    }
    user = UserResponse(**user_response_data)
    assert str(user.id) == user_response_data["id"]
    assert user.email == user_response_data["email"]

# Tests for LoginRequest
def test_login_request_valid():
    login_request_data = {"email": "john.doe@example.com", "password": "Secure*1234"}
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]
    