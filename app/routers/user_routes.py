"""
FastAPI application for user management with RESTful API principles, OAuth2 security,
and asynchronous database operations via SQLAlchemy. Implements HATEOAS for
enhanced API discoverability.
"""

from builtins import dict, int, len, str
from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, get_email_service, require_role
from app.schemas.pagination_schema import EnhancedPagination
from app.schemas.token_schema import TokenResponse
from app.schemas.user_schemas import LoginRequest, UserBase, UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.services.jwt_service import create_access_token
from app.utils.link_generation import create_user_links, generate_pagination_links
from app.dependencies import get_settings
from app.services.email_service import EmailService
from app.schemas.user_schemas import validate_url  # Import the validator class

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
settings = get_settings()

# --- Helper functions ---

async def get_user_or_404(db: AsyncSession, user_id: UUID):
    """Get a user by ID or raise a 404 exception if not found."""
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def create_user_response(user, request: Request = None):
    """Create a consistent UserResponse object from a user model."""
    response_data = {
        "id": user.id,
        "nickname": user.nickname,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "profile_picture_url": user.profile_picture_url,
        "github_profile_url": user.github_profile_url,
        "linkedin_profile_url": user.linkedin_profile_url,
        "role": user.role,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
    
    if request:
        response_data["links"] = create_user_links(user.id, request)
        
    return UserResponse.model_construct(**response_data)

# --- Admin/Manager User Management Endpoints ---

@router.get("/users/{user_id}", response_model=UserResponse, name="get_user", 
           tags=["User Management Requires (Admin or Manager Roles)"])
async def get_user(
    user_id: UUID, 
    request: Request, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme), 
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    """Fetch a user by their UUID."""
    user = await get_user_or_404(db, user_id)
    return create_user_response(user, request)

@router.put("/users/{user_id}", response_model=UserResponse, name="update_user", 
           tags=["User Management Requires (Admin or Manager Roles)"])
async def update_user(
    user_id: UUID, 
    user_update: UserUpdate, 
    request: Request, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme), 
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    """Update user information."""
    user_data = user_update.model_dump(exclude_unset=True)
    updated_user = await UserService.update(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return create_user_response(updated_user, request)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_user", 
              tags=["User Management Requires (Admin or Manager Roles)"])
async def delete_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme), 
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    """Delete a user by their ID."""
    success = await UserService.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, 
            tags=["User Management Requires (Admin or Manager Roles)"], name="create_user")
async def create_user(
    user: UserCreate, 
    request: Request, 
    db: AsyncSession = Depends(get_db), 
    email_service: EmailService = Depends(get_email_service), 
    token: str = Depends(oauth2_scheme), 
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    """Create a new user (admin/manager only)."""
    existing_user = await UserService.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    created_user = await UserService.create(db, user.model_dump(), email_service)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
    
    return create_user_response(created_user, request)

@router.get("/users/", response_model=UserListResponse, 
           tags=["User Management Requires (Admin or Manager Roles)"])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    """List users with pagination."""
    total_users = await UserService.count(db)
    users = await UserService.list_users(db, skip, limit)

    user_responses = [UserResponse.model_validate(user) for user in users]
    pagination_links = generate_pagination_links(request, skip, limit, total_users)
    
    return UserListResponse(
        items=user_responses,
        total=total_users,
        page=skip // limit + 1,
        size=len(user_responses),
        links=pagination_links
    )

# --- Public Authentication Endpoints ---

@router.post("/register/", response_model=UserResponse, tags=["Login and Registration"])
async def register(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_db), 
    email_service: EmailService = Depends(get_email_service)
):
    """Register a new user account."""
    user = await UserService.register_user(session, user_data.model_dump(), email_service)
    if not user:
        raise HTTPException(status_code=400, detail="Email already exists")
    return user

@router.post("/login/", response_model=TokenResponse, tags=["Login and Registration"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_db)
):
    """Authenticate a user and generate an access token."""
    if await UserService.is_account_locked(session, form_data.username):
        raise HTTPException(
            status_code=400, 
            detail="Account locked due to too many failed login attempts."
        )

    user = await UserService.login_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
        
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "role": str(user.role.name)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email/{user_id}/{token}", status_code=status.HTTP_200_OK, 
           name="verify_email", tags=["Login and Registration"])
async def verify_email(
    user_id: UUID, 
    token: str, 
    db: AsyncSession = Depends(get_db), 
    email_service: EmailService = Depends(get_email_service)
):
    """Verify a user's email with the provided token."""
    if await UserService.verify_email_with_token(db, user_id, token):
        return {"message": "Email verified successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Invalid or expired verification token"
    )

@router.post("/check-password-strength/", response_model=dict, tags=["User Management"])
async def check_password_strength(password_data: dict):
    """Check password strength without creating a user."""
    try:
        password = password_data.get("password", "")
        validate_url.validate_password(password)
        return {"message": "Password meets strength requirements"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))