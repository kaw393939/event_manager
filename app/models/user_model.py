from builtins import bool, int, str
from datetime import datetime
from enum import Enum
import uuid
import re
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, func, Enum as SQLAlchemyEnum
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.database import Base

class UserRole(Enum):
    """Enumeration of user roles within the application.

    This class defines various roles a user can have in the application, which
    are stored as ENUM in the database. These roles help in defining user permissions and access.
    """
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class User(Base):
    """
    Represents a user within the application.

    This class maps to the 'users' table in the database using SQLAlchemy ORM. It contains attributes
    related to the user's identity, status, and metadata, along with methods to manage user accounts.

    Attributes:
        id (UUID): Unique identifier for the user. Automatically generated.
        nickname (str): Unique nickname for the user, required and indexed for quick lookups.
        email (str): Unique email address for the user, required and indexed.
        email_verified (bool): Indicates if the user's email has been verified.
        hashed_password (str): Hashed password for security, required for authentication.
        first_name (str): Optional first name of the user.
        last_name (str): Optional last name of the user.
        bio (str): Optional biographical information about the user.
        profile_picture_url (str): Optional URL to the user's profile picture.
        linkedin_profile_url (str): Optional URL to the user's LinkedIn profile.
        github_profile_url (str): Optional URL to the user's GitHub profile.
        role (UserRole): Role of the user within the application, using an enum for easy role management.
        is_professional (bool): Indicates whether the user is a professional.
        professional_status_updated_at (datetime): Timestamp of the last update to the user's professional status.
        last_login_at (datetime): Timestamp of the user's last login.
        failed_login_attempts (int): Count of failed login attempts.
        is_locked (bool): Indicates if the user's account is locked.
        created_at (datetime): Timestamp when the user record was created.
        updated_at (datetime): Timestamp of the last update to the user record.
    """
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    # Primary Key: Unique identifier for each user
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Nickname: Must be unique, not null, and indexed for efficient querying
    nickname: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)
    
    # Email: Must be unique, not null, and indexed for efficient querying
    email: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    
    # Optional fields: First and last names, biography, and URLs for profile pictures and social media
    first_name: Mapped[str] = Column(String(100), nullable=True)
    last_name: Mapped[str] = Column(String(100), nullable=True)
    bio: Mapped[str] = Column(String(500), nullable=True)
    profile_picture_url: Mapped[str] = Column(String(255), nullable=True)
    linkedin_profile_url: Mapped[str] = Column(String(255), nullable=True)
    github_profile_url: Mapped[str] = Column(String(255), nullable=True)
    
    # Role: Specifies the user's role in the application using an enum type
    role: Mapped[UserRole] = Column(SQLAlchemyEnum(UserRole, name='UserRole', create_constraint=False), default=UserRole.ANONYMOUS, nullable=False)
    
    # Flags and timestamps related to the user's status and account activity
    is_professional: Mapped[bool] = Column(Boolean, default=False)
    professional_status_updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = Column(Integer, default=0)
    is_locked: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Optional fields: Email verification token and verification status
    verification_token = Column(String, nullable=True)
    email_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    
    # Hashed password for authentication purposes
    hashed_password: Mapped[str] = Column(String(255), nullable=False)

    @validates('nickname')
    def validate_nickname(self, key, nickname):
        """
        Validate the nickname to ensure it meets the specified criteria.

        Checks that the nickname contains only alphanumeric characters and underscores,
        and is between 3 and 20 characters long. Raises a ValueError if the validation fails.

        Args:
            key (str): The name of the attribute being validated.
            nickname (str): The value of the nickname to be validated.

        Returns:
            str: The validated nickname.

        Raises:
            ValueError: If the nickname does not meet the criteria.
        """
        if not re.match(r'^[\w-]+$', nickname):
            raise ValueError("Nickname must contain only alphanumeric characters and underscores.")
        if not (3 <= len(nickname) <= 20):
            raise ValueError("Nickname must be between 3 and 20 characters long.")
        return nickname

    def __repr__(self) -> str:
        """
        Provides a readable representation of a user object.

        Returns:
            str: A string representation of the user object, including nickname and role.
        """
        return f"<User {self.nickname}, Role: {self.role.name}>"

    def lock_account(self):
        """
        Locks the user account by setting the 'is_locked' flag to True.
        """
        self.is_locked = True

    def unlock_account(self):
        """
        Unlocks the user account by setting the 'is_locked' flag to False.
        """
        self.is_locked = False

    def verify_email(self):
        """
        Marks the user's email as verified by setting the 'email_verified' flag to True.
        """
        self.email_verified = True

    def has_role(self, role_name: UserRole) -> bool:
        """
        Checks if the user has a specified role.

        Args:
            role_name (UserRole): The role to check.

        Returns:
            bool: True if the user has the specified role, False otherwise.
        """
        return self.role == role_name

    def update_professional_status(self, status: bool):
        """
        Updates the professional status and logs the update time.

        Args:
            status (bool): The new professional status to set.
        """
        self.is_professional = status
        self.professional_status_updated_at = func.now()
