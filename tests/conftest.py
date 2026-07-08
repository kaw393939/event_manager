"""
File: conftest.py

Overview:
This file sets up fixtures for testing a FastAPI application using pytest.
It includes database fixtures, user-related fixtures, and mocks for external services.
"""

# Standard library imports
from datetime import datetime
from uuid import uuid4

# Third-party imports
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from faker import Faker

# Application-specific imports
from app.main import app
from app.database import Base, Database
from app.models.user_model import User, UserRole
from app.dependencies import get_db, get_settings
from app.utils.security import hash_password
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService
from app.services.jwt_service import create_access_token

# Initialize Faker for generating test data
fake = Faker()

# Load application settings
settings = get_settings()
TEST_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(TEST_DATABASE_URL, echo=settings.debug)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)


# Fixtures

@pytest.fixture
def email_service():
    """Mock email service."""
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)


@pytest.fixture(scope="function")
async def async_client(db_session):
    """Provides an asynchronous HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Initializes the database schema."""
    try:
        Database.initialize(settings.database_url)
    except Exception as e:
        pytest.fail(f"Failed to initialize the database: {str(e)}")


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Sets up and tears down the database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(setup_database):
    """Provides a database session for each test."""
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()

# User Fixtures

@pytest.fixture(scope="function")
async def locked_user(db_session):
    """Creates a locked user."""
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": True,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def user(db_session):
    """Creates a regular user."""
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def verified_user(db_session):
    """Creates a verified user."""
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def unverified_user(db_session):
    """Creates an unverified user."""
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    """Creates 50 users with the same role."""
    users = []
    for _ in range(50):
        user_data = {
            "nickname": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "hashed_password": hash_password(fake.password()),
            "role": UserRole.AUTHENTICATED,
            "email_verified": False,
            "is_locked": False,
        }
        user = User(**user_data)
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    return users


@pytest.fixture(scope="function")
async def admin_user(db_session):
    """Creates an admin user."""
    user = User(
        nickname="admin_user",
        email="admin@example.com",
        first_name="John",
        last_name="Doe",
        hashed_password=hash_password("securepassword"),
        role=UserRole.ADMIN,
        is_locked=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def manager_user(db_session):
    """Creates a manager user."""
    user = User(
        nickname="manager_user",
        email="manager@example.com",
        first_name="Jane",
        last_name="Doe",
        hashed_password=hash_password("securepassword"),
        role=UserRole.MANAGER,
        is_locked=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


# Test Data Fixtures

@pytest.fixture
def user_base_data():
    """Provides base data for a user."""
    return {
        "nickname": "testuser",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe",
    }


@pytest.fixture
def user_create_data(user_base_data):
    """Provides data for creating a user."""
    return {**user_base_data, "password": "SecurePassword123!"}


@pytest.fixture
def user_update_data():
    """Provides data for updating a user."""
    return {
        "email": "john.doe.new@example.com",
        "nickname": "updated_nickname",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Updated bio",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe",
    }


@pytest.fixture
def user_response_data():
    """Provides data for a user response."""
    return {
        "id": uuid4(),  # Fixed to provide a UUID object
        "nickname": "testuser",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Experienced developer",
        "role": UserRole.AUTHENTICATED,
        "profile_picture_url": "https://example.com/profiles/john.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe",
        "created_at": datetime.now(),
        "last_login_at": datetime.now(),
    }


@pytest.fixture
def login_request_data():
    """Provides login request data."""
    return {
        "email": "john.doe@example.com",
        "password": "SecurePassword123!",
    }


# Token Fixtures

@pytest.fixture
async def user_token(verified_user):
    """Generates a token for a verified user."""
    token_data = {"sub": str(verified_user.id), "role": "AUTHENTICATED"}
    return create_access_token(data=token_data)


@pytest.fixture
async def admin_token(admin_user):
    """Generates a token for an admin user."""
    token_data = {"sub": str(admin_user.id), "role": "ADMIN"}
    return create_access_token(data=token_data)


@pytest.fixture
async def manager_token(manager_user):
    """Generates a token for a manager user."""
    token_data = {"sub": str(manager_user.id), "role": "MANAGER"}
    return create_access_token(data=token_data)

@pytest.fixture
def user_base_data_invalid():
    """Provides invalid base data for a user (e.g., invalid email)."""
    return {
        "nickname": "testuser",
        "email": "john.doe.example.com",  # Invalid email format
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe",
    }