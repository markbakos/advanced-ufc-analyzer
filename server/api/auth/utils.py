from passlib.context import CryptContext
from datetime import datetime, timedelta
from server.core.config import settings
from typing import Union, Any
from jose import jwt

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    """Hash password using bcrypt"""
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if plain password matches hashed password"""
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: Union[str, Any], expires_delta: int = None) -> str:
    """Create JWT access token"""
    if expires_delta is not None:
        expires_delta = datetime.now(datetime.UTC) + expires_delta
    else:
        expires_delta = datetime.now(datetime.UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(data)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt