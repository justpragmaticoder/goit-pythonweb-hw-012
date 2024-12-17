from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.db.db import get_db
from src.conf.config import config
from src.services.users import UserService
from src.db.models import User, Role


class Hash:
    """
    A utility class for hashing and verifying passwords using bcrypt.
    """

    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a hashed password.

        Args:
            plain_password (str): The plain-text password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self._pwd_context.verify(plain_password, hashed_password)

    def get_pwd_hash(self, password: str) -> str:
        """
        Hash a plain-text password.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: The hashed password.
        """
        return self._pwd_context.hash(password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Get hashed password

        Args:
            password (str): Plain password

        Returns:
            str: Hashed password
        """
        return self._pwd_context.hash(password)


# OAuth2 configuration for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create a new JWT access token.

    Args:
        data (dict): The data to encode into the token.
        expires_delta (Optional[int]): Optional expiration time in seconds. Defaults to the value from configuration.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        timedelta(seconds=expires_delta)
        if expires_delta
        else timedelta(seconds=config.JWT_EXPIRATION_SECONDS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGO)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the currently authenticated user from the access token.

    Args:
        token (str): The JWT token provided via OAuth2 scheme.
        db (AsyncSession): The database session.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user cannot be authenticated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGO])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if not user:
        raise credentials_exception
    return user


def create_email_token(data: dict) -> str:
    """
    Create a new JWT token for email verification.

    Args:
        data (dict): The data to encode into the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=config.MAIL_TOKEN_EXP_DAYS)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGO)


async def get_email_from_token(token: str) -> str:
    """
    Decode an email address from an email verification token.

    Args:
        token (str): The JWT token containing the email address.

    Returns:
        str: The decoded email address.

    Raises:
        HTTPException: If the token is invalid or the email address cannot be decoded.
    """
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGO])
        email = payload.get("sub")
        if not email:
            raise ValueError("Email not found in token payload")
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email verification token",
        )
    
async def get_password_from_token(token: str) -> str:
    """
    Get password from token

    Args:
        token (str): JWT token

    Returns:
        str: Password

    Raises:
        HTTPException: Wrong token
    """
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        password = payload["password"]
        return password
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong token",
        )
    

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current admin user

    Args:
        current_user (User, optional): Current user. Defaults to Depends(get_current_user).

    Returns:
        User: Admin user object
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user