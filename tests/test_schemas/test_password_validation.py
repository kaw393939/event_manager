import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserCreate

def test_password_too_short():
    with pytest.raises(ValidationError) as e:
        UserCreate(email="test@example.com", password="Short1!")
    assert "at least 8 characters" in str(e.value)

def test_password_no_uppercase():
    with pytest.raises(ValidationError) as e:
        UserCreate(email="test@example.com", password="lowercase1!")
    assert "uppercase letter" in str(e.value)

def test_password_no_lowercase():
    with pytest.raises(ValidationError) as e:
        UserCreate(email="test@example.com", password="UPPERCASE1!")
    assert "lowercase letter" in str(e.value)

def test_password_no_number():
    with pytest.raises(ValidationError) as e:
        UserCreate(email="test@example.com", password="NoNumber!")
    assert "contain a number" in str(e.value)

def test_password_no_special():
    with pytest.raises(ValidationError) as e:
        UserCreate(email="test@example.com", password="NoSpecial123")
    assert "special character" in str(e.value)

def test_valid_password():
    user = UserCreate(email="test@example.com", password="ValidP@ss123")
    assert user.password == "ValidP@ss123"