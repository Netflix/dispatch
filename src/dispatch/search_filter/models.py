from typing import List, Optional

from pydantic import Field
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy_utils import TSVectorType

from dispatch.auth.models import DispatchUser, UserRead
from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, PrimaryKey, ProjectMixin
from dispatch.project.models import ProjectRead


class SearchFilter(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="search_filters")

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class SearchFilterBase(DispatchBase):
    expression: List[dict]
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)


class SearchFilterCreate(SearchFilterBase):
    project: ProjectRead


class SearchFilterUpdate(SearchFilterBase):
    id: PrimaryKey = None


class SearchFilterRead(SearchFilterBase):
    id: PrimaryKey
    creator: Optional[UserRead]


class SearchFilterPagination(DispatchBase):
    items: List[SearchFilterRead]
    total: int
