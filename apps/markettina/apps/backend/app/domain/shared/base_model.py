"""
MARKETTINA v2.0 - Base Model
Standard fields for all entities following DDD patterns.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin for soft delete support."""

    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()


class VersionMixin:
    """Mixin for optimistic locking."""

    version = Column(Integer, nullable=False, default=1)


class MultiTenantMixin:
    """Mixin for multi-tenancy support via account_id."""

    @declared_attr
    def account_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )


class BaseEntity(TimestampMixin, SoftDeleteMixin, VersionMixin):
    """
    Base entity with standard fields:
    - id: UUID primary key
    - created_at, updated_at: timestamps
    - deleted_at: soft delete
    - version: optimistic locking
    """

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
            server_default=text("gen_random_uuid()")
        )


class MultiTenantEntity(BaseEntity, MultiTenantMixin):
    """
    Base entity for multi-tenant resources.
    Includes account_id for tenant isolation.
    """
