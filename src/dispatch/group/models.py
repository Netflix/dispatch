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
    email: str


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    id: int


class GroupRead(GroupBase):
    id: int


class GroupNested(GroupBase):
    id: int
