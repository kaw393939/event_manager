from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from faker import Faker

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


# ---------- Helper Functions ----------
def generate_user_data(**overrides):
    return {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
        **overrides
    }

async def create_user(db_session, **overrides):
    user = User(**generate_user_data(**overrides))
    db_session.add(user)
    await db_session.commit()
    return user

def create_token(sub: str, role: str):
    return create_access_token(data={"sub": sub, "role": role})


# ---------- Fixtures ----------
@pytest.fixture
def email_service():
    return EmailService(template_manager=TemplateManager())

@pytest.fixture(scope="function")
async def async_client(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        yield client
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
        yield session
        await session.close()


# ---------- User Fixtures ----------
@pytest.fixture
async def user(db_session):
    return await create_user(db_session)

@pytest.fixture
async def locked_user(db_session):
    return await create_user(db_session, is_locked=True, failed_login_attempts=settings.max_login_attempts)

@pytest.fixture
async def verified_user(db_session):
    return await create_user(db_session, email_verified=True)

@pytest.fixture
async def unverified_user(db_session):
    return await create_user(db_session, email_verified=False)

@pytest.fixture
async def users_with_same_role_50_users(db_session):
    return [await create_user(db_session) for _ in range(50)]

@pytest.fixture
async def admin_user(db_session):
    return await create_user(db_session, nickname="admin_user", email="admin@example.com", role=UserRole.ADMIN)

@pytest.fixture
async def manager_user(db_session):
    return await create_user(db_session, nickname="manager_john", email="manager_user@example.com", role=UserRole.MANAGER)


# ---------- Token Fixtures ----------
@pytest.fixture
def user_token():
    return create_token("john_doe_123", UserRole.AUTHENTICATED.value)

@pytest.fixture
def admin_token():
    return create_token("john_doe_Admin", UserRole.ADMIN.value)

@pytest.fixture
def manager_token():
    return create_token("john_doe_manager", UserRole.MANAGER.value)


# ---------- Test Data Fixtures ----------
@pytest.fixture
def user_base_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe@example.com",
        "nickname": "manager_john",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "username": "john_doe_123",
        "email": "john.doe.example.com",  # Invalid email
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
        "first_name": "John",
        "full_name": "John H. Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "last_login_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe.test@example.com",
        "password": "SecurePassword123!"
    }
