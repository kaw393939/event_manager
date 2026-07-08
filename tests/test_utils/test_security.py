import pytest
from app.utils.security import hash_password, verify_password, generate_verification_token

def test_password_validation():
    password = "TestPass123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass123!", hashed)

def test_hash_password_with_different_rounds():
    password = "TestPass123!"
    hashed1 = hash_password(password, rounds=4)
    hashed2 = hash_password(password, rounds=12)
    assert hashed1 != hashed2
    assert verify_password(password, hashed1)
    assert verify_password(password, hashed2)

def test_hash_password_invalid_input():
    with pytest.raises(ValueError):
        hash_password("")

def test_verify_password_invalid_hash():
    with pytest.raises(ValueError):
        verify_password("password", "invalid_hash")

def test_generate_verification_token():
    token1 = generate_verification_token()
    token2 = generate_verification_token()
    assert len(token1) > 16  # URL-safe token is longer than original bytes
    assert token1 != token2  # Tokens should be unique