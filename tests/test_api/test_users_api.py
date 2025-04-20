# ====================== DATABASE + MODELS + JWT SERVICE + FIXTURES ======================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Boolean
from datetime import datetime, timedelta
from uuid import uuid4, UUID
import jwt

# ------------------ CONFIGURATION ------------------

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ------------------ DATABASE SETUP ------------------

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

# ------------------ USER MODEL ------------------

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    role = Column(String, default="AUTHENTICATED")

# ------------------ JWT SERVICE ------------------

def create_token(user_id: UUID, role: str) -> str:
    to_encode = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# ------------------ MOCK EMAIL SERVICE ------------------

class EmailService:
    async def send_user_email(self, *args, **kwargs):
        pass
    async def send_verification_email(self, *args, **kwargs):
        pass

# ------------------ FAKE SECURITY FUNCTION ------------------

def hash_password(password: str) -> str:
    return f"hashed_{password}"

# ------------------ FASTAPI APP FOR TESTING ------------------

from fastapi import FastAPI
app = FastAPI()

# ------------------ PYTEST FIXTURES ------------------

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def verified_user():
    return User(
        id=str(uuid4()),
        email="verified@example.com",
        password_hash=hash_password("MySuperPassword$1234"),
        is_verified=True,
        is_locked=False,
        role="AUTHENTICATED",
        nickname="verified_user"
    )

@pytest.fixture
def admin_user():
    return User(
        id=str(uuid4()),
        email="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
        is_verified=True,
        is_locked=False,
        role="ADMIN",
        nickname="admin_user"
    )

@pytest.fixture
def manager_user():
    return User(
        id=str(uuid4()),
        email="manager@example.com",
        password_hash=hash_password("ManagerPass123!"),
        is_verified=True,
        is_locked=False,
        role="MANAGER",
        nickname="manager_user"
    )

@pytest.fixture
def locked_user():
    return User(
        id=str(uuid4()),
        email="locked@example.com",
        password_hash=hash_password("MySuperPassword$1234"),
        is_verified=True,
        is_locked=True,
        role="AUTHENTICATED",
        nickname="locked_user"
    )

@pytest.fixture
def unverified_user():
    return User(
        id=str(uuid4()),
        email="unverified@example.com",
        password_hash=hash_password("MySuperPassword$1234"),
        is_verified=False,
        is_locked=False,
        role="AUTHENTICATED",
        nickname="unverified_user"
    )

@pytest.fixture
def user_token(verified_user):
    return create_token(user_id=verified_user.id, role=verified_user.role)

@pytest.fixture
def admin_token(admin_user):
    return create_token(user_id=admin_user.id, role=admin_user.role)

@pytest.fixture
def manager_token(manager_user):
    return create_token(user_id=manager_user.id, role=manager_user.role)

@pytest.fixture
def email_service(mocker):
    mock = mocker.Mock(spec=EmailService)
    mock.send_user_email.return_value = None
    mock.send_verification_email.return_value = None
    return mock

@pytest.fixture
def user_base_data():
    return {
        "nickname": "johndoe123",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "profile_picture_url": "https://example.com/profile.jpg",
        "bio": "I am a software engineer with over 5 years of experience.",
    }

@pytest.fixture
def user_create_data(user_base_data):
    return {
        **user_base_data,
        "password": "SecurePassword123!"
    }

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "profile_picture_url": "https://example.com/profile_updated.jpg",
        "bio": "I specialize in backend development with Python and Node.js.",
    }

@pytest.fixture
def user_response_data():
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "nickname": "tester",
        "created_at": datetime.utcnow(),
        "last_login_at": datetime.utcnow()
    }

@pytest.fixture
def login_request_data():
    return {
        "email": "john.doe@example.com",
        "password": "SecurePassword123!"
    }
