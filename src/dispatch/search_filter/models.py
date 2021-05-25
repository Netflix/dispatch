from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.schema import UniqueConstraint

from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin

from dispatch.project.models import ProjectRead


class SearchFilter(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON)
    creator_id = Column(Integer, ForeignKey("dispatch.dispatch_user.id"))
    creator = relationship("DispatchUser", backref="search_filters")
    type = Column(String)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class SearchFilterBase(DispatchBase):
    expression: Optional[List[dict]] = []
    name: Optional[str]
    type: Optional[str]
    description: Optional[str]


class SearchFilterCreate(SearchFilterBase):
    project: ProjectRead


class SearchFilterUpdate(SearchFilterBase):
    id: int


class SearchFilterRead(SearchFilterBase):
    id: int


class SearchFilterPagination(DispatchBase):
    items: List[SearchFilterRead]
    total: int
