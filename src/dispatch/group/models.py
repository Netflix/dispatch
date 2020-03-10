from sqlalchemy import Column, Integer, String

from dispatch.database import Base
from dispatch.models import DispatchBase, ResourceMixin


class Group(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)


# Pydantic models...
class GroupBase(DispatchBase):
    name: str
    email: str
    resource_id: str
    resource_type: str
    weblink: str


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    id: int


class GroupRead(GroupBase):
    id: int


class GroupNested(GroupBase):
    id: int
