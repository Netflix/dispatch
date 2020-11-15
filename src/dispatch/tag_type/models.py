from typing import List, Optional

from sqlalchemy import Column, Integer, String

from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


class TagType(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class TagTypeBase(DispatchBase):
    name: str
    description: Optional[str]


class TagTypeCreate(TagTypeBase):
    pass


class TagTypeUpdate(TagTypeBase):
    id: int


class TagTypeRead(TagTypeBase):
    id: int


class TagTypePagination(DispatchBase):
    items: List[TagTypeRead]
    total: int
