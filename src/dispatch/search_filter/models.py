from datetime import datetime

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
    id: PrimaryKey | None
    name: str
    email: str


class TeamRead(DispatchBase):
    id: PrimaryKey | None
    name: str


class ServiceRead(DispatchBase):
    id: PrimaryKey | None
    name: str


class NotificationRead(DispatchBase):
    id: PrimaryKey | None
    name: str


class SearchFilterBase(DispatchBase):
    description: str | None = Field(None, nullable=True)
    enabled: bool | None
    expression: list[dict]
    name: NameStr
    subject: SearchFilterSubject = SearchFilterSubject.incident


class SearchFilterCreate(SearchFilterBase):
    project: ProjectRead


class SearchFilterUpdate(SearchFilterBase):
    id: PrimaryKey = None


class SearchFilterRead(SearchFilterBase):
    id: PrimaryKey
    created_at: datetime | None = None
    updated_at: datetime | None = None
    project: ProjectRead | None
    creator: UserRead | None
    individuals: list[IndividualContactRead | None] = []
    notifications: list[NotificationRead | None] = []
    services: list[ServiceRead | None] = []
    teams: list[TeamRead | None] = []


class SearchFilterPagination(Pagination):
    items: list[SearchFilterRead]
