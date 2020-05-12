from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean

from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


class Tag(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    uri = Column(String)
    source = Column(String)
    type = Column(String)
    discoverable = Column(Boolean, default=True)
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class TagBase(DispatchBase):
    name: str
    source: Optional[str] = "dispatch"
    type: Optional[str] = "generic"
    uri: Optional[str]
    discoverable: Optional[bool] = True
    description: Optional[str] = "Generic user tag"


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    id: int


class TagRead(TagBase):
    id: int


class TagPagination(DispatchBase):
    items: List[TagRead]
    total: int
