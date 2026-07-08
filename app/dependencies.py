import logging
from builtins import Exception, dict, str
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Database
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService
from app.services.jwt_service import decode_token
from settings.config import Settings, settings
from jwt import PyJWTError

# Configure logging to capture information at the INFO level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_settings() -> Settings:
    """Return application settings."""
    return settings

def get_email_service() -> EmailService:
    """Create and return an instance of EmailService with a TemplateManager."""
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

async def get_db() -> AsyncSession:
    """Dependency that provides a database session for each request.
    
    This function creates an async database session and yields it.
    If an exception occurs during session handling, an HTTP 500 error is raised.
    """
    async_session_factory = Database.get_session_factory()
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# OAuth2 scheme to retrieve the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Retrieve the current user based on the provided token.
    
    This function decodes the token, retrieves user details from the database,
    and raises HTTP 401 if the token is invalid or the user cannot be found.
    """
    from app.services.user_service import UserService
    
    # Exception to be raised if credentials are invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        logger.info("Decoding token...")
        payload = decode_token(token)  # Use decode_token from jwt_service
        if payload is None:
            logger.error("Failed to decode token")
            raise credentials_exception
        
        email: str = payload.get("sub")
        logger.info(f"Token decoded successfully, email extracted: {email}")
        if email is None:
            logger.error("Email extracted from token is None")
            raise credentials_exception
        
        logger.info("Fetching user from database...")
        user = await UserService.get_by_email(db, email)
        if user is None:
            logger.error(f"No user found with email: {email}")
            raise credentials_exception
        
        logger.info(f"User found: {user.email}, role: {user.role}")
        return {"email": user.email, "role": user.role.name}
    
    except PyJWTError as e:
        logger.error(f"JWTError occurred: {e}")
        raise credentials_exception

def require_role(roles: list):
    """Decorator to ensure the current user has one of the required roles.
    
    This function returns a role checker that verifies if the user's role
    is included in the specified list of roles. If not, it raises an HTTP 403 error.
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        logger.info(f"Checking if user role {current_user['role']} is in {roles}")
        if current_user["role"] not in roles:
            logger.error(f"User role {current_user['role']} not permitted")
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    
    return role_checker
