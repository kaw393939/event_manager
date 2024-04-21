import pytest
from pydantic import ValidationError, HttpUrl
from app.schemas.link_schema import Link

# Fixture for creating a Link instance with predefined attributes
@pytest.fixture
def example_link():
    return Link(
        rel="self",
        href="https://api.example.com/qr/123",
        action="GET",
        type="application/json"
    )

# Test for correct initialization
def test_link_initialization(example_link):
    assert example_link.rel == "self"
    assert example_link.href == HttpUrl("https://api.example.com/qr/123")
    assert example_link.action == "GET"
    assert example_link.type == "application/json"

# Test default type field
def test_link_default_type():
    link = Link(
        rel="next",
        href="https://api.example.com/qr/124",
        action="POST"
    )
    assert link.type == "application/json"  # Check default value

# Test validation of fields
def test_link_field_validation():
    # Valid case
    try:
        Link(rel="update", href="https://api.example.com/qr/125", action="PUT")
    except ValidationError as e:
        pytest.fail(f"Unexpected ValidationError: {e}")
    
    # Invalid URL
    with pytest.raises(ValidationError):
        Link(rel="delete", href="not_a_valid_url", action="DELETE")

# Test example matches model capabilities
def test_link_example_matches_model(example_link):
    # Create an example dictionary where 'href' is expected to be a string
    example = {
        "rel": "self",
        "href": "https://api.example.com/qr/123",  # Expected as a string
        "action": "GET",
        "type": "application/json"
    }
    # Convert the `example_link` to a dictionary and update the 'href' to be a string
    example_link_dict = example_link.dict()
    example_link_dict['href'] = str(example_link.href)  # Convert HttpUrl to string

    assert example_link_dict == example
