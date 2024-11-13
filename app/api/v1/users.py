import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.core.security import get_current_admin_user
from app.schemas import User, UserCreate, UserRoleCreate
from app.services import UserService

router = APIRouter()
logger = logging.getLogger("auth_service.api.v1.users")


@router.post("/users/", response_model=User)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    logger.info(f"The administrator {current_user.username} creates a user: {user.username}")
    user_service = UserService(db)
    existing_user = user_service.get_user_by_username(user.username)
    if existing_user:
        logger.warning(f"The user {user.username} already exists.")
        raise HTTPException(status_code=400, detail="The user already exists")
    created_user = user_service.create_user(user)
    logger.info(f"The user {created_user.username} was successfully created.")
    return created_user


@router.get("/users/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    logger.info(
        f"The administrator {current_user.username} requests a list of users. Pass: {skip}, Limit: {limit}"
    )
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    logger.info(f"Returned by {len(users)} users.")
    return users


@router.delete("/users/{username}", response_model=User)
def delete_user(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    logger.info(f"The administrator {current_user.username} deletes the user: {username}")
    user_service = UserService(db)
    user = user_service.delete_user(username)
    if not user:
        logger.warning(f"The user {username} was not found to be deleted.")
        raise HTTPException(status_code=404, detail="The user was not found")
    logger.info(f"User {username} has been successfully deleted.")
    return user


@router.post("/users/{username}/roles/", response_model=UserRoleCreate)
def add_user_role(
    username: str,
    role: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    logger.info(f"The administrator {current_user.username} adds a role for the user: {username}")
    user_service = UserService(db)
    added_role = user_service.add_user_role(username, role)
    if not added_role:
        logger.warning(f"Failed to add the role {role.role} to the user {username}.")
        raise HTTPException(status_code=404, detail="The user or service was not found")
    logger.info(
        f"The role {added_role.role} for the service ID {added_role.service_id} has been added to the user {username}."
    )
    return added_role
