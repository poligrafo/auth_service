import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app import crud, schemas, models

logger = logging.getLogger("auth_service.services.user_service")


class UserService:
    """
    Service class for handling user-related business logic.
    Utilizes the UserRepository for data access operations.
    """
    def __init__(self, db: Session):
        self.user_repo = crud.UserRepository(db)

    def authenticate_user(self, username_or_email: str, password: str) -> Optional[models.User]:
        """
        Authenticates a user by verifying their credentials.

        :param username_or_email: The username or email of the user.
        :param password: The plaintext password of the user.
        :return: The authenticated User object if successful, else None.
        """
        logger.debug(f"Service authentication for user: {username_or_email}")
        return self.user_repo.authenticate_user(username_or_email, password)

    def create_user(self, user_create: schemas.UserCreate) -> models.User:
        """
        Creates a new user.

        :param user_create: UserCreate schema containing user details.
        :return: The created User object.
        """
        logger.debug(f"Service creating user: {user_create.username}")
        return self.user_repo.create_user(user_create)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """
        Retrieves a list of users with pagination.

        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of User objects.
        """
        logger.debug(f"Service fetching users with skip={skip} and limit={limit}")
        return self.user_repo.get_users(skip=skip, limit=limit)

    def delete_user(self, username: str) -> Optional[models.User]:
        """
        Deletes a user by their username.

        :param username: The username of the user to delete.
        :return: The deleted User object if successful, else None.
        """
        logger.debug(f"Service deleting user: {username}")
        return self.user_repo.delete_user(username)

    def add_user_role(self, username: str, role_create: schemas.UserRoleCreate) -> Optional[models.UserRole]:
        """
        Adds a role to a user for a specific service.

        :param username: The username of the user.
        :param role_create: UserRoleCreate schema containing role details.
        :return: The created UserRole object if successful, else None.
        """
        logger.debug(f"Service adding role '{role_create.role}' to user '{username}'")
        user = self.user_repo.get_user_by_username(username)
        if not user:
            logger.warning(f"User '{username}' not found while adding role.")
            return None
        return self.user_repo.add_user_role(user, role_create)

    def get_user_by_username(self, username: str) -> Optional[models.User]:
        """
        Retrieves a user by their username.

        :param username: The username of the user to retrieve.
        :return: User object if found, else None.
        """
        logger.debug(f"Service fetching user by username: {username}")
        return self.user_repo.get_user_by_username(username)
