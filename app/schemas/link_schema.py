from pydantic import BaseModel, Field, AnyUrl, ConfigDict, field_validator

class Link(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rel: str
    href: str  # Allow any URL format
    method: str = "GET"
    action: str | None = None

class PaginationLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rel: str
    href: str  # Allow relative URLs
