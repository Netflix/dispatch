from datetime import datetime
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
    weblink: AnyHttpUrl | str | None = Field(None, nullable=True)
    mobile_phone: str | None = Field(None, nullable=True)
    office_phone: str | None = Field(None, nullable=True)
    title: str | None = Field(None, nullable=True)
    external_id: str | None = Field(None, nullable=True)

    @validator("weblink")
    def weblink_validator(cls, v):
        if v is None or isinstance(v, AnyHttpUrl) or v == "":
            return v
        raise ValueError("weblink is not an empty string or a valid weblink")


class IndividualContactCreate(IndividualContactBase):
    filters: list[SearchFilterRead] = []
    project: ProjectRead


class IndividualContactUpdate(IndividualContactBase):
    filters: list[SearchFilterRead] = []


class IndividualContactRead(IndividualContactBase):
    id: PrimaryKey | None
    filters: list[SearchFilterRead] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IndividualContactReadMinimal(IndividualContactBase):
    id: PrimaryKey | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IndividualContactPagination(Pagination):
    items: list[IndividualContactRead] = []
