"""Models for storage functionality in the Dispatch application."""

from pydantic import field_validator

from sqlalchemy import Column, Integer, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import STORAGE_DESCRIPTION
from dispatch.models import ResourceBase, ResourceMixin


class Storage(Base, ResourceMixin):
    """SQLAlchemy model for storage resources."""

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))


# Pydantic models...
class StorageBase(ResourceBase):
    """Base Pydantic model for storage resources."""


class StorageCreate(StorageBase):
    """Pydantic model for creating a storage resource."""


class StorageUpdate(StorageBase):
    """Pydantic model for updating a storage resource."""


class StorageRead(StorageBase):
    """Pydantic model for reading a storage resource."""

    description: str | None = None

    @field_validator("description", mode="before")
    @classmethod
    def set_description(cls, _v: str):
        """Sets the description."""
        return STORAGE_DESCRIPTION
