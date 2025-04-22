"""
This Python file is part of a FastAPI application, demonstrating user management functionalities including creating, reading,
updating, and deleting (CRUD) user information. It uses OAuth2 with Password Flow for security, ensuring that only authenticated
users can perform certain operations. Additionally, the file showcases the integration of FastAPI with SQLAlchemy for asynchronous
database operations, enhancing performance by non-blocking database calls.

The implementation emphasizes RESTful API principles, with endpoints for each CRUD operation and the use of HTTP status codes
and exceptions to communicate the outcome of operations. It introduces the concept of HATEOAS (Hypermedia as the Engine of
Application State) by including navigational links in API responses, allowing clients to discover other related operations dynamically.

OAuth2PasswordBearer is employed to extract the token from the Authorization header and verify the user's identity, providing a layer
of security to the operations that manipulate user data.

Key Highlights:
- Use of FastAPI's Dependency Injection system to manage database sessions and user authentication.
- Demonstrates how to perform CRUD operations in an asynchronous manner using SQLAlchemy with FastAPI.
- Implements HATEOAS by generating dynamic links for user-related actions, enhancing API discoverability.
- Utilizes OAuth2PasswordBearer for securing API endpoints, requiring valid access tokens for operations.
"""

from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, get_email_service, require_role
from app.schemas.user_schemas import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.schemas.token_schema import TokenResponse
from app.services.user_service import UserService
from app.services.jwt_service import create_access_token
from app.utils.link_generation import create_user_links, generate_pagination_links
from app.dependencies import get_settings
from app.services.email_service import EmailService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
settings = get_settings()

@router.get(
    "/users/{user_id}", response_model=UserResponse,
    name="get_user", tags=["User Management Requires (Admin or Manager Roles)"]
)
async def get_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)

@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    name="update_user",
    tags=["User Management Requires (Admin or Manager Roles)"],
)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    request: Request,
    db: AsyncSession               = Depends(get_db),
    token: str                     = Depends(oauth2_scheme),
    current_user: dict             = Depends(require_role(["ADMIN", "MANAGER"]))
):
    # 1) Grab only the fields they actually set
    data = user_update.model_dump(exclude_unset=True)

    # 2) Map public "username" → ORM "email"
    update_dict = user_update.model_dump(exclude_unset=True)
    updated_user = await UserService.update(db, user_id, update_dict)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_construct(
        id=                  updated_user.id,
        username=            updated_user.email,
        nickname=            updated_user.nickname,
        first_name=          updated_user.first_name,
        last_name=           updated_user.last_name,
        bio=                 updated_user.bio,
        profile_picture_url= updated_user.profile_picture_url,
        linkedin_profile_url=updated_user.linkedin_profile_url,
        github_profile_url=  updated_user.github_profile_url,
        role=                updated_user.role,
        is_professional=     updated_user.is_professional,
        created_at=          updated_user.created_at,
        last_login_at=       updated_user.last_login_at,
    )

    # 3) Convert any HttpUrl fields to str
    for fld in ("profile_picture_url","linkedin_profile_url","github_profile_url"):
        if fld in data and data[fld] is not None:
            data[fld] = str(data[fld])

    # 4) Perform the update
    updated = await UserService.update(db, user_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    # 5) Return a Pydantic response, exposing `username` again
    return UserResponse.model_construct(
        id=                  updated.id,
        username=            updated.email,
        nickname=            updated.nickname,
        first_name=          updated.first_name,
        last_name=           updated.last_name,
        bio=                 updated.bio,
        profile_picture_url= updated.profile_picture_url,
        linkedin_profile_url=updated.linkedin_profile_url,
        github_profile_url=  updated.github_profile_url,
        role=                updated.role,
        is_professional=     updated.is_professional,
        created_at=          updated.created_at,
        last_login_at=       updated.last_login_at,
    )

@router.delete(
    "/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
    name="delete_user", tags=["User Management Requires (Admin or Manager Roles)"]
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    success = await UserService.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post(
    "/users/", response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_user", tags=["User Management Requires (Admin or Manager Roles)"]
)
async def create_user(
    user_create: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    existing = await UserService.get_by_email(db, user_create.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    created = await UserService.create(db, user_create.model_dump(), email_service)
    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
    return UserResponse.model_validate(created)

@router.get(
    "/users/", response_model=UserListResponse,
    tags=["User Management Requires (Admin or Manager Roles)"]
)
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    total = await UserService.count(db)
    users = await UserService.list_users(db, skip, limit)
    items = [UserResponse.model_validate(u) for u in users]
    links = generate_pagination_links(request, skip, limit, total)
    return UserListResponse(items=items, total=total, page=skip//limit+1, size=len(items), links=links)

@router.post(
    "/register/", response_model=UserResponse,
    tags=["Login and Registration"]
)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
):
    user = await UserService.register_user(db, user_create.model_dump(by_alias=True), email_service)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    return UserResponse.model_validate(user)

@router.post(
    "/login/", response_model=TokenResponse,
    tags=["Login and Registration"], include_in_schema=False
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    if await UserService.is_account_locked(db, form_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account locked")
    user = await UserService.login_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    # use email for subject since User model stores email
    token = create_access_token(data={"sub": user.email, "role": str(user.role.name)}, expires_delta=expires)
    return {"access_token": token, "token_type": "bearer"}

@router.get(
    "/verify-email/{user_id}/{token}", status_code=status.HTTP_200_OK,
    name="verify_email", tags=["Login and Registration"]
)
async def verify_email(user_id: UUID, token: str, db: AsyncSession = Depends(get_db), email_service: EmailService = Depends(get_email_service)):
    if await UserService.verify_email_with_token(db, user_id, token):
        return {"message": "Email verified successfully"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")