from __future__ import annotations
import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, User
from app.models.service_models import Service


class UserRole(Base):
    """
    Associates a user with a role within a specific service.
    Ensures that each user-service pair is unique.
    """
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint('user_id', 'service_id', name='uix_user_service'),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Unique identifier for the user role association"
    )
    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Role of the user within the service"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="Foreign key referencing the user"
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id"),
        nullable=False,
        comment="Foreign key referencing the service"
    )

    user: Mapped[User] = relationship("User", back_populates="roles")
    service: Mapped[Service] = relationship("Service", back_populates="user_roles")
