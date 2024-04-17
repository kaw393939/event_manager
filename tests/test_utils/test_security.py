# test_security.py

import pytest
from app.utils import security

def test_hash_password():
    password = "test_password"
    hashed_password = security.hash_password(password)
    assert hashed_password != password  # Ensure password is hashed
    assert security.verify_password(password, hashed_password)  # Verify password is correct

def test_verify_password():
    password = "test_password"
    hashed_password = security.hash_password(password)
    assert security.verify_password(password, hashed_password)  # Verify correct password
    assert not security.verify_password("wrong_password", hashed_password)  # Verify incorrect password

def test_verify_password_invalid_hash():
    with pytest.raises(ValueError):
        security.verify_password("test_password", "invalid_hashed_password")

if __name__ == "__main__":
    pytest.main() # pragma: no cover
