from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.schema import UniqueConstraint

from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, ProjectMixin, PrimaryKey

from dispatch.auth.models import DispatchUser

from dispatch.project.models import ProjectRead


class SearchFilter(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="search_filters")
    type = Column(String)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class SearchFilterBase(DispatchBase):
    expression: List[dict]
    name: NameStr
    type: Optional[str]
    description: Optional[str] = Field(None, nullable=True)


class SearchFilterCreate(SearchFilterBase):
    project: ProjectRead


class SearchFilterUpdate(SearchFilterBase):
    id: PrimaryKey = None


class SearchFilterRead(SearchFilterBase):
    id: PrimaryKey


class SearchFilterPagination(DispatchBase):
    items: List[SearchFilterRead]
    total: int
