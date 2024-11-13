import logging
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.settings import settings
from app.schemas import TokenData
from app.services import UserService

logger = logging.getLogger("auth_service.core.security")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    :param data: Dictionary containing the data to encode in the token.
    :param expires_delta: Optional timedelta for token expiration.
    :return: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta
                                           else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created JWT token for data: {data}")
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[Any]:
    """
    Retrieves the current user based on the JWT token.

    :param token: JWT token.
    :param db: Database session.
    :return: User object if token is valid and user exists.
    :raises HTTPException: If token is invalid or user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Failed to verify credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            logger.error("The JWT token does not contain a user")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"Error decoding the JWT token: {e}")
        raise credentials_exception

    user_service = UserService(db)
    user = user_service.get_user_by_username(token_data.username)
    if user is None:
        logger.error(f"User {token_data.username} not found")
        raise credentials_exception
    return user


def get_current_admin_user(
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Ensures that the current user has administrative privileges.

    :param current_user: The current authenticated user.
    :return: The current user if they have admin rights.
    :raises HTTPException: If the user lacks admin rights.
    """
    # Check if the user has an 'admin' role in any service
    admin_role = any(role.role == "admin" for role in current_user.roles)
    if not admin_role:
        logger.warning(f"The user {current_user.username} does not have administrative rights")
        raise HTTPException(status_code=403, detail="Not enough rights")
    return current_user
