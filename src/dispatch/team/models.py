from datetime import datetime
from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.project.models import ProjectRead
from dispatch.search_filter.models import SearchFilterRead
from dispatch.models import (
    ContactBase,
    ContactMixin,
    EvergreenBase,
    EvergreenMixin,
    NameStr,
    ProjectMixin,
    PrimaryKey,
    Pagination,
)

assoc_team_contact_incidents = Table(
    "team_contact_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("incident_id", "team_contact_id"),
)

assoc_team_filters = Table(
    "assoc_team_contact_filters",
    Base.metadata,
    Column("team_contact_id", Integer, ForeignKey("team_contact.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("team_contact_id", "search_filter_id"),
)


class TeamContact(Base, ContactMixin, ProjectMixin, EvergreenMixin):
    __table_args__ = (UniqueConstraint("email", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    notes = Column(String)
    incidents = relationship(
        "Incident", secondary=assoc_team_contact_incidents, backref="teams"
    )  # I'm not sure this needs to be set explicitly rather than via a query

    filters = relationship("SearchFilter", secondary=assoc_team_filters, backref="teams")
    search_vector = Column(TSVectorType("name", "notes", weights={"name": "A", "notes": "B"}))


class TeamContactBase(ContactBase, EvergreenBase):
    name: NameStr
    notes: Optional[str] = Field(None, nullable=True)


class TeamContactCreate(TeamContactBase):
    filters: Optional[List[SearchFilterRead]] = []
    project: ProjectRead


class TeamContactUpdate(TeamContactBase):
    filters: Optional[List[SearchFilterRead]] = []


class TeamContactRead(TeamContactBase):
    id: PrimaryKey
    filters: Optional[List[SearchFilterRead]] = []
    created_at: datetime
    updated_at: datetime


class TeamPagination(Pagination):
    items: List[TeamContactRead] = []
