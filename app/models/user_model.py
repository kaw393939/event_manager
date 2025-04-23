from builtins import bool, int, str
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import (
    String, Integer, DateTime, Boolean, func, Enum as SQLAlchemyEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class UserRole(Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[uuid.UUID] = mapped_column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nickname: Mapped[str] = mapped_column("nickname", String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column("email", String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column("first_name", String(100), nullable=True)
    last_name: Mapped[str] = mapped_column("last_name", String(100), nullable=True)
    bio: Mapped[str] = mapped_column("bio", String(500), nullable=True)
    profile_picture_url: Mapped[str] = mapped_column("profile_picture_url", String(255), nullable=True)
    linkedin_profile_url: Mapped[str] = mapped_column("linkedin_profile_url", String(255), nullable=True)
    github_profile_url: Mapped[str] = mapped_column("github_profile_url", String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        "role", SQLAlchemyEnum(UserRole, name='UserRole', create_constraint=False),
        default=UserRole.ANONYMOUS, nullable=False
    )
    is_professional: Mapped[bool] = mapped_column("is_professional", Boolean, default=False)
    professional_status_updated_at: Mapped[datetime] = mapped_column("professional_status_updated_at", DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime] = mapped_column("last_login_at", DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column("failed_login_attempts", Integer, default=0)
    is_locked: Mapped[bool] = mapped_column("is_locked", Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    verification_token: Mapped[str] = mapped_column("verification_token", String, nullable=True)
    email_verified: Mapped[bool] = mapped_column("email_verified", Boolean, default=False, nullable=False)
    hashed_password: Mapped[str] = mapped_column("hashed_password", String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.nickname}, Role: {self.role.name}>"

    def lock_account(self):
        self.is_locked = True

    def unlock_account(self):
        self.is_locked = False

    def verify_email(self):
        self.email_verified = True

    def has_role(self, role_name: UserRole) -> bool:
        return self.role == role_name

    def update_professional_status(self, status: bool):
        self.is_professional = status
        self.professional_status_updated_at = func.now()
