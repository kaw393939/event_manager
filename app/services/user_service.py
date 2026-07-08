import re
from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
import secrets
from typing import Optional, Dict, List
from pydantic import ValidationError
from sqlalchemy import func, null, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_email_service, get_settings
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from uuid import UUID
from app.services.email_service import EmailService
from app.models.user_model import UserRole
import logging
from fastapi import HTTPException

# Load application settings and configure logger
settings = get_settings()
logger = logging.getLogger(__name__)

def validate_password(password: str):
    """
    Validate the format of the password. 
    Password must be at least 8 characters long and include 
    an uppercase letter, a lowercase letter, a number, and a special character.

    :param password: The password to validate.
    :raises HTTPException: If the password does not meet the criteria.
    """
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        raise HTTPException(
            status_code=400, 
            detail='Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.'
        )
    
def validate_nickname(nickname: str):
    """
    Validate the format of the nickname. 
    Nickname must contain only alphanumeric characters, underscores, and hyphens.

    :param nickname: The nickname to validate.
    :raises HTTPException: If the nickname contains invalid characters.
    """
    if not re.match(r'^[\w-]+$', nickname):
        raise HTTPException(
            status_code=400,
            detail="Nickname must contain only alphanumeric characters, underscores, and hyphens."
        )

class UserService:

    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        """
        Execute a database query and handle any errors.

        :param session: The AsyncSession instance for database access.
        :param query: The SQLAlchemy query to execute.
        :return: The result of the query, or None if an error occurs.
        """
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        """
        Fetch a user from the database based on the provided filters.

        :param session: The AsyncSession instance for database access.
        :param filters: Filters to apply to the query.
        :return: The user object if found, otherwise None.
        """
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Fetch a user by their ID.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to fetch.
        :return: The user object if found, otherwise None.
        """
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        """
        Fetch a user by their nickname.

        :param session: The AsyncSession instance for database access.
        :param nickname: The nickname of the user to fetch.
        :return: The user object if found, otherwise None.
        """
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        """
        Fetch a user by their email address.

        :param session: The AsyncSession instance for database access.
        :param email: The email of the user to fetch.
        :return: The user object if found, otherwise None.
        """
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        """
        Create a new user in the database.

        :param session: The AsyncSession instance for database access.
        :param user_data: A dictionary containing the user data.
        :param email_service: An instance of EmailService to send verification emails.
        :return: The created user object if successful, otherwise None.
        :raises HTTPException: If validation fails or if a user with the same email or nickname already exists.
        """
        try:
            # Validate and clean user data
            validated_data = UserCreate(**user_data).model_dump()
            existing_user_by_email = await cls.get_by_email(session, validated_data['email'])
            if existing_user_by_email:
                logger.error("User with given email already exists.")
                raise HTTPException(status_code=400, detail="User with given email already exists.")
        
            existing_user_by_nickname = await cls.get_by_nickname(session, validated_data['nickname'])
            if existing_user_by_nickname:
                logger.error("User with given nickname already exists.")
                raise HTTPException(status_code=400, detail="User with given nickname already exists.")

            # Validate password and nickname
            validate_nickname(validated_data['nickname'])
            validate_password(validated_data['password'])

            # Hash password and create user
            validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            new_user = User(**validated_data)
            new_user.verification_token = generate_verification_token()
        
            session.add(new_user)
            await session.commit()
            await email_service.send_verification_email(new_user)
        
            return new_user
        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            raise HTTPException(status_code=422, detail="Validation error: " + str(e))

    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        """
        Update an existing user's information.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to update.
        :param update_data: A dictionary containing the fields to update.
        :return: The updated user object if successful, otherwise None.
        :raises HTTPException: If validation fails or if a user with the same email or nickname already exists.
        """
        try:
            # Validate and clean update data
            validated_data = UserUpdate(**update_data).dict(exclude_unset=True)

            if 'email' in validated_data:
                existing_user = await cls.get_by_email(session, validated_data['email'])
                if existing_user and existing_user.id != user_id:
                    logger.error("User with given email already exists.")
                    raise HTTPException(status_code=422, detail="User with given email already exists.")

            if 'nickname' in validated_data:
                validate_nickname(validated_data['nickname'])
                existing_user = await cls.get_by_nickname(session, validated_data['nickname'])
                if existing_user and existing_user.id != user_id:
                    logger.error("User with given nickname already exists.")
                    raise HTTPException(status_code=422, detail="User with given nickname already exists.")

            if 'password' in validated_data:
                password = validated_data.pop('password')
                validate_password(password)  # Validate the password
                validated_data['hashed_password'] = hash_password(password)
            
            # Fetch and update the user
            existing_user = await cls.get_by_id(session, user_id)
            if not existing_user:
                logger.error(f"User with ID {user_id} not found.")
                return None
            
            query = (
                update(User)
                .where(User.id == user_id)
                .values(**validated_data)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()

            updated_user = await cls.get_by_id(session, user_id)
            return updated_user
        except ValidationError as e:
            logger.error(f"Validation error during user update: {e}")
            raise HTTPException(status_code=422, detail="Validation error: " + str(e))

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        """
        Delete a user from the database.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to delete.
        :return: True if the user was deleted, otherwise False.
        """
        user = await cls.get_by_id(session, user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found.")
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        """
        List users from the database with pagination.

        :param session: The AsyncSession instance for database access.
        :param skip: The number of users to skip.
        :param limit: The maximum number of users to return.
        :return: A list of user objects.
        """
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str], get_email_service) -> Optional[User]:
        """
        Register a new user. This is a wrapper for the create method.

        :param session: The AsyncSession instance for database access.
        :param user_data: A dictionary containing the user data.
        :param get_email_service: A function to get an instance of EmailService.
        :return: The created user object if successful, otherwise None.
        """
        return await cls.create(session, user_data, get_email_service)

    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user based on email and password.

        :param session: The AsyncSession instance for database access.
        :param email: The email of the user trying to log in.
        :param password: The password provided by the user.
        :return: The user object if authentication is successful, otherwise None.
        """
        user = await cls.get_by_email(session, email)
        if user:
            if user.email_verified is False:
                logger.warning(f"User {email} has not verified their email.")
                return None
            if user.is_locked:
                logger.warning(f"User {email} is locked due to too many failed login attempts.")
                return None
            if verify_password(password, user.hashed_password):
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                logger.info(f"User {email} logged in successfully.")
                return user
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.is_locked = True
                session.add(user)
                await session.commit()
                logger.warning(f"User {email} failed to log in. Failed attempts: {user.failed_login_attempts}.")
        else:
            logger.warning(f"User {email} not found.")
        return None

    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
        """
        Check if a user's account is locked.

        :param session: The AsyncSession instance for database access.
        :param email: The email of the user to check.
        :return: True if the account is locked, otherwise False.
        """
        user = await cls.get_by_email(session, email)
        return user.is_locked if user else False

    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        """
        Reset a user's password.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user whose password is to be reset.
        :param new_password: The new password for the user.
        :return: True if the password was reset successfully, otherwise False.
        """
        hashed_password = hash_password(new_password)
        user = await cls.get_by_id(session, user_id)
        if user:
            user.hashed_password = hashed_password
            user.failed_login_attempts = 0  # Resetting failed login attempts
            user.is_locked = False  # Unlocking the user account, if locked
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        """
        Verify a user's email address using a verification token.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to verify.
        :param token: The verification token provided by the user.
        :return: True if the email was verified successfully, otherwise False.
        """
        user = await cls.get_by_id(session, user_id)
        if user and user.verification_token == token:
            user.email_verified = True
            user.verification_token = None  # Clear the token once used
            user.role = UserRole.AUTHENTICATED
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        """
        Count the number of users in the database.

        :param session: The AsyncSession instance for database access.
        :return: The count of users.
        """
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        count = result.scalar()
        return count
    
    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        """
        Unlock a user's account.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to unlock.
        :return: True if the account was unlocked successfully, otherwise False.
        """
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0  # Optionally reset failed login attempts
            session.add(user)
            await session.commit()
            return True
        return False
