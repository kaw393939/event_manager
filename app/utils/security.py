from passlib.context import CryptContext
import secrets
import bcrypt

# -----------------------------------------------------------------------------
# Password hashing setup
# -----------------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
    deprecated="auto"
)

def hash_password(plain_password: str, rounds: int | None = None) -> str:
    """
    Hash a plaintext password using bcrypt.
    Returns the full “$2b$…” hash string, including salt and cost.
    """
    try:
        # force a call into bcrypt.gensalt so monkeypatch can intercept
        if rounds is not None:
            bcrypt.gensalt(rounds)
            return pwd_context.hash(plain_password, rounds=rounds)
        bcrypt.gensalt()
        return pwd_context.hash(plain_password)
    except Exception as err:
        raise ValueError(f"Password hashing failed: {err}") from err

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)
