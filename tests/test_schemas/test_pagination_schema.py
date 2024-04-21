import pytest
from app.schemas.pagination_schema import EnhancedPagination, PaginationLink

# Fixtures for creating instances of Pagination
@pytest.fixture
def base_pagination():
    return EnhancedPagination(page=1, per_page=10, total_items=100, total_pages=10)

@pytest.fixture
def link():
    return PaginationLink(rel="next", href="http://example.com/page/2")

# Test adding links to Pagination
def test_add_link(base_pagination, link):
    base_pagination.add_link(rel=link.rel, href=str(link.href))  # Convert URL to string when adding
    assert len(base_pagination.links) == 1
    assert base_pagination.links[0].rel == "next"
    assert str(base_pagination.links[0].href) == "http://example.com/page/2"  # Convert URL to string for comparison

# Test to ensure the link is correctly added and properties are as expected
def test_add_link_properties(base_pagination):
    base_pagination.add_link("prev", "http://example.com/page/0")
    assert base_pagination.links[-1].rel == "prev"
    assert str(base_pagination.links[-1].href) == "http://example.com/page/0"  # Convert URL to string for comparison
    assert base_pagination.links[-1].method == "GET"  # Check for default method