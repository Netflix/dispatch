from pydantic.networks import EmailStr
from dispatch.models import PrimaryKey
from sqlalchemy import Column, Integer, String, ForeignKey

from dispatch.database.core import Base
from dispatch.models import ResourceBase, ResourceMixin


class Group(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))


# Pydantic models...
class GroupBase(ResourceBase):
    name: str
    email: EmailStr


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    id: PrimaryKey


class GroupRead(GroupBase):
    id: PrimaryKey


class GroupNested(GroupBase):
    id: PrimaryKey
