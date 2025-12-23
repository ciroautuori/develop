"""
MARKETTINA v2.0 - Shared Domain Components
"""

from .base_model import (
    BaseEntity,
    MultiTenantEntity,
    MultiTenantMixin,
    SoftDeleteMixin,
    TimestampMixin,
    VersionMixin,
)

__all__ = [
    "BaseEntity",
    "MultiTenantEntity",
    "MultiTenantMixin",
    "SoftDeleteMixin",
    "TimestampMixin",
    "VersionMixin",
]
