from __future__ import annotations
import uuid
from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.schemas import UserRole


class Service(Base):
    """
    Represents a service within the system.
    """
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Unique identifier for the service"
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Name of the service"
    )

    user_roles: Mapped[List[UserRole]] = relationship(
        "UserRole",
        back_populates="service",
        cascade="all, delete-orphan",
        comment="User roles associated with the service"
    )