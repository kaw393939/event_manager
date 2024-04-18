# test_link_generation.py

import pytest
from app.main import app
from app.schemas.link_schema import Link
from app.schemas.pagination_schema import PaginationLink
from app.utils.link_generation import create_user_links, generate_pagination_links
from uuid import UUID

class MockRequest:
    def __init__(self, base_url):
        self.base_url = base_url

    def url_for(self, endpoint, **kwargs):
        return f"{self.base_url}/{endpoint}"

    @property
    def url(self):
        return self.base_url

@pytest.fixture
def app_instance():
    return app()

@pytest.fixture
def mock_request():
    return MockRequest("https://example.com")

def test_create_user_links(mock_request):
    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    links = create_user_links(user_id, mock_request)
    assert len(links) == 3

    for link in links:
        assert isinstance(link, Link)
        assert link.action in ["view", "update", "delete"]

'''
To be fixed
def test_generate_pagination_links(mock_request):
    skip = 0
    limit = 5
    total_items = 25
    links = generate_pagination_links(mock_request, skip, limit, total_items)
    assert len(links) == 5

    for link in links:
        assert isinstance(link, PaginationLink)

    assert any(link.rel == "self" for link in links)
    assert any(link.rel == "first" for link in links)
    assert any(link.rel == "last" for link in links)
    assert any(link.rel == "next" for link in links)
    assert any(link.rel == "prev" for link in links)
    '''
