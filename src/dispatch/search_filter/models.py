from datetime import datetime
from typing import List, Optional

from pydantic import Field

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy_utils import TSVectorType

from dispatch.auth.models import DispatchUser, UserRead
from dispatch.database.core import Base
from dispatch.enums import DispatchEnum
from dispatch.models import (
    DispatchBase,
    NameStr,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
    Pagination,
)
from dispatch.project.models import ProjectRead


class SearchFilterSubject(DispatchEnum):
    case = "case"
    incident = "incident"


class SearchFilter(Base, ProjectMixin, TimeStampMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="search_filters")
    subject = Column(String, default="incident")
    enabled = Column(Boolean, default=True)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class IndividualContactRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: str
    email: str


class TeamRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: str


class ServiceRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: str


class NotificationRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: str


class SearchFilterBase(DispatchBase):
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    expression: List[dict]
    name: NameStr
    subject: SearchFilterSubject = SearchFilterSubject.incident


class SearchFilterCreate(SearchFilterBase):
    project: ProjectRead


class SearchFilterUpdate(SearchFilterBase):
    id: PrimaryKey = None


class SearchFilterRead(SearchFilterBase):
    id: PrimaryKey
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project: Optional[ProjectRead]
    creator: Optional[UserRead]
    individuals: Optional[List[IndividualContactRead]] = []
    notifications: Optional[List[NotificationRead]] = []
    services: Optional[List[ServiceRead]] = []
    teams: Optional[List[TeamRead]] = []


class SearchFilterPagination(Pagination):
    items: List[SearchFilterRead]
