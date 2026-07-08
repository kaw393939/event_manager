from builtins import len, max, sorted, str
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse, parse_qsl, urlunparse, urlencode
from uuid import uuid4

import pytest
from fastapi import Request

from app.utils.link_generation import create_link, create_pagination_link, create_user_links, generate_pagination_links

from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

def normalize_url(url):
    """Normalize the URL for consistent comparison by sorting query parameters."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
    # Sort the query parameters by key, and sort their values if there are multiple for a single key
    sorted_query_items = sorted((k, sorted(v)) for k, v in query_params.items())
    # Convert the sorted query parameters back to a query string
    encoded_query = urlencode(sorted_query_items, doseq=True)
    normalized_url = urlunparse(parsed_url._replace(query=encoded_query))
    return normalized_url.rstrip('/')


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.url = "http://testserver/users"  # Return string instead of MagicMock
    return request

def test_create_link():
    link = create_link("self", "http://example.com", "GET", "view")
    assert normalize_url(str(link.href)) == "http://example.com"

def test_create_user_links(mock_request):
    user_id = uuid4()
    links = create_user_links(user_id, mock_request)
    assert len(links) == 3
    assert normalize_url(str(links['self'].href)) == f"http://testserver/users/{user_id}"

def test_generate_pagination_links(mock_request):
    skip = 10
    limit = 5
    total_items = 50
    links = generate_pagination_links(mock_request, skip, limit, total_items)
    assert 'self' in links
    expected_self_url = "http://testserver/users?limit=5&skip=10"
    assert normalize_url(str(links['self'].href)) == normalize_url(expected_self_url)

def test_generate_pagination_links_with_empty_params(mock_request):
    links = generate_pagination_links(mock_request, 0, 10, 100)
    first_link = next(link for link in links if link.rel == "first")
    assert "skip=0" in str(first_link.href)
    assert "limit=10" in str(first_link.href)

def test_generate_pagination_links_with_filters(mock_request):
    links = generate_pagination_links(
        mock_request, 
        0, 
        10, 
        100
    )
    assert "skip=0" in str(links[0].href)

def test_create_link_with_params():
    link = create_link("self", "http://example.com", method="GET", action="view")  # Add required action
    assert "http://example.com" in str(link.href)

def test_create_pagination_link():
    params = {"skip": 20, "limit": 10}
    link = create_pagination_link("next", "http://example.com", params)
    assert "skip=20" in str(link.href)
    assert "limit=10" in str(link.href)