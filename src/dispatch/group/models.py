from typing import Optional

from pydantic import validator, Field
from pydantic.networks import EmailStr

from sqlalchemy import Column, Integer, String, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import TACTICAL_GROUP_DESCRIPTION
from dispatch.models import NameStr, PrimaryKey
from dispatch.models import ResourceBase, ResourceMixin


class Group(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))


# Pydantic models...
class GroupBase(ResourceBase):
    name: NameStr
    email: EmailStr


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    id: PrimaryKey = None


class GroupRead(GroupBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return TACTICAL_GROUP_DESCRIPTION
