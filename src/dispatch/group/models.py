"""Models for group resources in the Dispatch application."""
from pydantic import field_validator, EmailStr
from pydantic.networks import EmailStr

from sqlalchemy import Column, Integer, String, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import TACTICAL_GROUP_DESCRIPTION
from dispatch.models import NameStr, PrimaryKey
from dispatch.models import ResourceBase, ResourceMixin


class Group(Base, ResourceMixin):
    """SQLAlchemy model for group resources."""
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))


# Pydantic models...
class GroupBase(ResourceBase):
    """Base Pydantic model for group resources."""
    name: NameStr
    email: EmailStr


class GroupCreate(GroupBase):
    """Pydantic model for creating a group resource."""
    pass


class GroupUpdate(GroupBase):
    """Pydantic model for updating a group resource."""
    id: PrimaryKey | None = None


class GroupRead(GroupBase):
    """Pydantic model for reading a group resource."""
    id: PrimaryKey
    description: str | None = None

    @field_validator("description", mode="before")
    @classmethod
    def set_description(cls, v):
        """Sets the description for the group resource."""
        return TACTICAL_GROUP_DESCRIPTION
