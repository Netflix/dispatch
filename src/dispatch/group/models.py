from sqlalchemy import Column, Integer, String

from dispatch.database import Base
from dispatch.models import DispatchBase, ResourceMixin


class Group(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)


# Pydantic models...
class GroupBase(DispatchBase):
    pass


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    id: int


class GroupRead(GroupBase):
    id: int


class GroupNested(GroupBase):
    id: int
