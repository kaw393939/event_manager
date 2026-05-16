# Standard library imports
from builtins import range
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

# Third-party imports
import pytest
from fastapi.testclient import TestClient
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

fake = Faker()

settings = get_settings()
TEST_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(TEST_DATABASE_URL, echo=settings.debug)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)


@pytest.fixture
def email_service():
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)


@pytest.fixture(scope="function")
async def async_client(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    try:
        Database.initialize(settings.database_url)
    except Exception as e:
        pytest.fail(f"Failed to initialize the database: {str(e)}")


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()


# DRY helper function to create users
async def create_user(
    db_session,
    *,
    nickname=None,
    first_name=None,
    last_name=None,
    email=None,
    password="MySuperPassword$1234",
    role=UserRole.AUTHENTICATED,
    email_verified=False,
    is_locked=False,
    failed_login_attempts=0
):
    user_data = {
        "nickname": nickname or fake.user_name(),
        "first_name": first_name or fake.first_name(),
        "last_name": last_name or fake.last_name(),
        "email": email or fake.email(),
        "hashed_password": hash_password(password),
        "role": role,
        "email_verified": email_verified,
        "is_locked": is_locked,
        "failed_login_attempts": failed_login_attempts
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


# DRY fixtures using create_user
@pytest.fixture(scope="function")
async def user(db_session):
    return await create_user(db_session)


@pytest.fixture(scope="function")
async def verified_user(db_session):
    return await create_user(db_session, email_verified=True)


@pytest.fixture(scope="function")
async def unverified_user(db_session):
    return await create_user(db_session, email_verified=False)


@pytest.fixture(scope="function")
async def locked_user(db_session):
    return await create_user(
        db_session,
        is_locked=True,
        failed_login_attempts=settings.max_login_attempts
    )


@pytest.fixture(scope="function")
async def admin_user(db_session):
    return await create_user(
        db_session,
        nickname="admin_user",
        email="admin@example.com",
        first_name="John",
        last_name="Doe",
        password="securepassword",
        role=UserRole.ADMIN
    )


@pytest.fixture(scope="function")
async def manager_user(db_session):
    return await create_user(
        db_session,
        nickname="manager_john",
        email="manager_user@example.com",
        first_name="John",
        last_name="Doe",
        password="securepassword",
        role=UserRole.MANAGER
    )


@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    return [await create_user(db_session) for _ in range(50)]


# Base user data
@pytest.fixture
def user_base_data():
    return {
        "email": "john.doe@example.com",
        "nickname": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe"
    }


@pytest.fixture
def user_base_data_invalid():
    return {
        "username": "john_doe_123",
        "email": "john.doe.example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }


@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}


@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "nickname": "johnny123",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johnny",
        "github_profile_url": "https://github.com/johnny"
    }


@pytest.fixture
def user_response_data():
    return {
        "id": uuid4(),
        "email": "test@example.com",
        "nickname": "jane_doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "bio": "QA engineer",
        "profile_picture_url": "https://example.com/profile.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/janedoe",
        "github_profile_url": "https://github.com/janedoe",
        "role": "AUTHENTICATED",
        "is_professional": True,
        "last_login_at": datetime.utcnow()
    }


@pytest.fixture
def login_request_data():
    return {
        "email": "john.doe@example.com",
        "password": "SecurePassword123!"
    }
