import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext

from app import models, schemas

logger = logging.getLogger("auth_service.crud.user")

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    """
    Repository class for User CRUD operations.
    Encapsulates all database interactions related to the User model.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[models.User]:
        """
        Retrieves a user by their username.

        :param username: The username of the user to retrieve.
        :return: User object if found, else None.
        """
        logger.debug(f"Fetching user by username: {username}")
        return self.db.query(models.User).filter(models.User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """
        Retrieves a user by their email.

        :param email: The email of the user to retrieve.
        :return: User object if found, else None.
        """
        logger.debug(f"Fetching user by email: {email}")
        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """
        Retrieves a list of users with pagination.

        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of User objects.
        """
        logger.debug(f"Fetching users with skip={skip} and limit={limit}")
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create_user(self, user: schemas.UserCreate) -> models.User:
        """
        Creates a new user with hashed password.

        :param user: UserCreate schema containing user details.
        :return: The created User object.
        """
        logger.debug(f"Creating user: {user.username}")
        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"User {db_user.username} successfully created.")
        return db_user

    def delete_user(self, username: str) -> Optional[models.User]:
        """
        Deletes a user by their username.

        :param username: The username of the user to delete.
        :return: The deleted User object if found and deleted, else None.
        """
        logger.debug(f"Deleting user: {username}")
        user = self.get_user_by_username(username)
        if user:
            self.db.delete(user)
            self.db.commit()
            logger.info(f"User {username} successfully deleted.")
        else:
            logger.warning(f"Attempted to delete non-existent user: {username}")
        return user

    def add_user_role(self, user: models.User, role: schemas.UserRoleCreate) -> models.UserRole:
        """
        Adds a role to a user for a specific service.

        :param user: The User object to which the role will be added.
        :param role: UserRoleCreate schema containing role details.
        :return: The created UserRole object.
        """
        logger.debug(f"Adding role '{role.role}' to user '{user.username}' for service ID {role.service_id}")
        user_role = models.UserRole(
            role=role.role,
            service_id=role.service_id,
            user_id=user.id
        )
        self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user_role)
        logger.info(f"Role '{user_role.role}' added to user '{user.username}' for service ID {role.service_id}.")
        return user_role

    def authenticate_user(self, username: str, password: str) -> Optional[models.User]:
        """
        Authenticates a user by verifying their username and password.

        :param username: The username or email of the user.
        :param password: The plaintext password to verify.
        :return: The User object if authentication is successful, else None.
        """
        logger.debug(f"Authenticating user: {username}")
        user = self.get_user_by_username(username)
        if not user:
            logger.debug(f"User '{username}' not found. Attempting to fetch by email.")
            user = self.get_user_by_email(username)  # Allows login via email
        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found.")
            return None
        if not pwd_context.verify(password, user.hashed_password):
            logger.warning(f"Authentication failed: Incorrect password for user '{username}'.")
            return None
        logger.info(f"User '{username}' successfully authenticated.")
        return user
