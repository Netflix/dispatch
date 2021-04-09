from typing import List, Optional

from sqlalchemy import Column, Integer, String

from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin
from dispatch.project.models import ProjectRead


class TagType(Base, TimeStampMixin, ProjectMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class TagTypeBase(DispatchBase):
    name: str
    description: Optional[str]


class TagTypeCreate(TagTypeBase):
    project: ProjectRead


class TagTypeUpdate(TagTypeBase):
    id: int


class TagTypeRead(TagTypeBase):
    id: int


class TagTypePagination(DispatchBase):
    items: List[TagTypeRead]
    total: int
