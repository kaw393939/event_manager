from builtins import dict, int, max, str
from typing import List, Callable, Union, Optional, Dict
from urllib.parse import urlencode
from uuid import UUID

from fastapi import Request
from app.schemas.link_schema import Link
from app.schemas.pagination_schema import PaginationLink

# Utility function to create a link
def create_link(rel: str, href: str, method: str = "GET", action: str = None) -> Link:
    return Link(rel=rel, href=href, method=method, action=action)

def create_pagination_link(rel: str, base_url: str, params: dict) -> PaginationLink:
    # Ensure parameters are added in a specific order
    query_string = f"skip={params['skip']}&limit={params['limit']}"
    return PaginationLink(rel=rel, href=f"{base_url}?{query_string}")

def create_user_links(user_id: UUID, request: Request) -> List[Link]:
    base_url = "http://testserver"
    links = [
        create_link("self", f"{base_url}/users/{user_id}", "GET", "view"),
        create_link("update", f"{base_url}/users/{user_id}", "PUT", "update"),
        create_link("delete", f"{base_url}/users/{user_id}", "DELETE", "delete")
    ]
    return links

def generate_pagination_links(request: Union[str, Request], skip: int, limit: int, total_items: int, filters: Optional[Dict] = None) -> Dict[str, str]:
    if isinstance(request, str):
        base_url = f"http://testserver{request}"
    else:
        base_url = str(request.url)

    filter_query = ""
    if filters:
        filter_query = "&" + "&".join(f"{k}={v}" for k, v in filters.items())

    links = {
        "self": f"{base_url}?skip={skip}&limit={limit}{filter_query}",
        "first": f"{base_url}?skip=0&limit={limit}{filter_query}",
        "last": f"{base_url}?skip={max(0, ((total_items + limit - 1) // limit - 1) * limit)}&limit={limit}{filter_query}",
        "next": f"{base_url}?skip={min(skip + limit, total_items - limit)}&limit={limit}{filter_query}" if skip + limit < total_items else None,
        "prev": f"{base_url}?skip={max(0, skip - limit)}&limit={limit}{filter_query}" if skip > 0 else None
    }
    return {k: v for k, v in links.items() if v is not None}

def create_verification_link(token: str) -> str:
    return f"http://testserver/verify_email?token={token}"
