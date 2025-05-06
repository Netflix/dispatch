"""Models for individual contact resources in the Dispatch application."""

from datetime import datetime
from pydantic import field_validator, Field
from urllib.parse import urlparse

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table, UniqueConstraint
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
    TimeStampMixin,
)

# Association tables for many to many relationships
assoc_individual_filters = Table(
    "assoc_individual_filters",
    Base.metadata,
    Column("individual_contact_id", Integer, ForeignKey("individual_contact.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("individual_contact_id", "search_filter_id"),
)


class IndividualContact(Base, ContactMixin, ProjectMixin, TimeStampMixin):
    """SQLAlchemy model for individual contact resources."""
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
    """Base Pydantic model for individual contact resources."""
    mobile_phone: str | None = Field(None, nullable=True)
    office_phone: str | None = Field(None, nullable=True)
    title: str | None = Field(None, nullable=True)
    weblink: str | None = Field(None, nullable=True)
    external_id: str | None = Field(None, nullable=True)

    @field_validator("weblink")
    @classmethod
    def weblink_validator(cls, v: str | None) -> str | None:
        """Validates the weblink field to be None, empty string, or a valid URL (internal or external)."""
        if v is None or v == "":
            return v
        result = urlparse(v)
        if all([result.scheme, result.netloc]):
            return v
        raise ValueError("weblink must be empty or a valid URL")


class IndividualContactCreate(IndividualContactBase):
    """Pydantic model for creating an individual contact resource."""
    filters: list[SearchFilterRead] | None = None
    project: ProjectRead


class IndividualContactUpdate(IndividualContactBase):
    """Pydantic model for updating an individual contact resource."""
    filters: list[SearchFilterRead] | None = None
    project: ProjectRead | None = None


class IndividualContactRead(IndividualContactBase):
    """Pydantic model for reading an individual contact resource."""
    id: PrimaryKey
    filters: list[SearchFilterRead] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IndividualContactReadMinimal(IndividualContactBase):
    """Pydantic model for reading a minimal individual contact resource."""
    id: PrimaryKey
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IndividualContactPagination(Pagination):
    """Pydantic model for paginated individual contact results."""
    total: int
    items: list[IndividualContactRead] = []
