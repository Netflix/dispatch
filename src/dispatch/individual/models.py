from datetime import datetime
from typing import List, Optional, Union
from pydantic import Field, AnyHttpUrl, validator

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.project.models import ProjectRead
from dispatch.search_filter.models import SearchFilterRead
from dispatch.models import (
    ContactBase,
    ContactMixin,
    ProjectMixin,
    PrimaryKey,
    Pagination,
)

# Association tables for many to many relationships
assoc_individual_filters = Table(
    "assoc_individual_contact_filters",
    Base.metadata,
    Column(
        "individual_contact_id", Integer, ForeignKey("individual_contact.id", ondelete="CASCADE")
    ),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("individual_contact_id", "search_filter_id"),
)


class IndividualContact(Base, ContactMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("email", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mobile_phone = Column(String)
    office_phone = Column(String)
    title = Column(String)
    weblink = Column(String)
    external_id = Column(String)

    events = relationship("Event", backref="individual")
    service_feedback = relationship("ServiceFeedback", backref="individual")

    filters = relationship(
        "SearchFilter", secondary=assoc_individual_filters, backref="individuals"
    )
    team_contact_id = Column(Integer, ForeignKey("team_contact.id"))
    team_contact = relationship("TeamContact", backref="individuals")

    search_vector = Column(
        TSVectorType(
            "name",
            "title",
            "email",
            "company",
            "notes",
            weights={"name": "A", "email": "B", "title": "C", "company": "D"},
        )
    )


class IndividualContactBase(ContactBase):
    weblink: Union[AnyHttpUrl, None, str] = Field(None, nullable=True)
    mobile_phone: Optional[str] = Field(None, nullable=True)
    office_phone: Optional[str] = Field(None, nullable=True)
    title: Optional[str] = Field(None, nullable=True)
    external_id: Optional[str] = Field(None, nullable=True)

    @validator("weblink")
    def weblink_validator(cls, v):
        if v is None or isinstance(v, AnyHttpUrl) or v == "":
            return v
        raise ValueError("weblink is not an empty string or a valid weblink")


class IndividualContactCreate(IndividualContactBase):
    filters: Optional[List[SearchFilterRead]]
    project: ProjectRead


class IndividualContactUpdate(IndividualContactBase):
    filters: Optional[List[SearchFilterRead]]


class IndividualContactRead(IndividualContactBase):
    id: Optional[PrimaryKey]
    filters: Optional[List[SearchFilterRead]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IndividualContactReadMinimal(IndividualContactBase):
    id: Optional[PrimaryKey]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IndividualContactPagination(Pagination):
    items: List[IndividualContactRead] = []
