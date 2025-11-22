from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# -------------------------------
# Security Configuration
# -------------------------------

# NOTE: In production, never hardcode this.
# Store it in environment variables (.env file).
SECRET_KEY = "super_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# -------------------------------
# Password Hashing (Using Argon2)
# -------------------------------

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using Argon2.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies whether a plain password matches the stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------
# JWT Token Generation
# -------------------------------

def create_access_token(data: dict) -> str:
    """
    Creates a signed JWT token with expiration.
    `data` should contain user identifiers (example: {"sub": user_id})
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
