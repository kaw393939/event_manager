import pytest
from app.schemas.pagination_schema import Pagination, EnhancedPagination

@pytest.fixture
def sample_pagination_data():
    return {
        "page": 1,
        "per_page": 10,
        "total_items": 50,
        "total_pages": 5
    }

@pytest.fixture
def sample_pagination_links():
    return [
        {"rel": "next", "href": "http://example.com/api?page=2"},
        {"rel": "prev", "href": "http://example.com/api?page=1"},
    ]

def test_pagination_model(sample_pagination_data):
    pagination = Pagination(**sample_pagination_data)
    assert pagination.page == sample_pagination_data["page"]
    assert pagination.per_page == sample_pagination_data["per_page"]
    assert pagination.total_items == sample_pagination_data["total_items"]
    assert pagination.total_pages == sample_pagination_data["total_pages"]

def test_enhanced_pagination_model(sample_pagination_data, sample_pagination_links):
    enhanced_pagination = EnhancedPagination(**sample_pagination_data)
    for link_data in sample_pagination_links:
        enhanced_pagination.add_link(**link_data)
    assert enhanced_pagination.page == sample_pagination_data["page"]
    assert enhanced_pagination.per_page == sample_pagination_data["per_page"]
    assert enhanced_pagination.total_items == sample_pagination_data["total_items"]
    assert enhanced_pagination.total_pages == sample_pagination_data["total_pages"]
    assert len(enhanced_pagination.links) == len(sample_pagination_links)

    # Additional checks for links
    for index, link in enumerate(enhanced_pagination.links):
        assert link.rel == sample_pagination_links[index]["rel"]
        assert str(link.href) == sample_pagination_links[index]["href"]
