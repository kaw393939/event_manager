import pytest
from pydantic import ValidationError
from app.schemas.token_schemas import Token, TokenData, RefreshTokenRequest

# Test Token model
def test_token_model():
    access_token = "jhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    token = Token(access_token=access_token)
    assert token.access_token == access_token
    assert token.token_type == "bearer"  # Default value check

    # Validate JSON schema
    assert token.schema()["properties"]["access_token"]["type"] == "string"
    assert token.schema()["properties"]["token_type"]["type"] == "string"

# Test TokenData model
# Test TokenData model
def test_token_data_model():
    token_data = TokenData()

    # Validate JSON schema
    assert token_data.schema() is not None

# Test RefreshTokenRequest model
def test_refresh_token_request_model():
    refresh_token = "jhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    refresh_request = RefreshTokenRequest(refresh_token=refresh_token)
    assert refresh_request.refresh_token == refresh_token

    # Validate JSON schema
    assert refresh_request.schema()["properties"]["refresh_token"]["type"] == "string"