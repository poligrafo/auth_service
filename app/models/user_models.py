from __future__ import annotations
import uuid
from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.schemas import UserRole


class User(Base):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Unique identifier for the user"
    )
    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Username of the user"
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Email address of the user"
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Hashed password of the user"
    )

    roles: Mapped[List[UserRole]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        comment="Roles associated with the user"
    )
