"""Models for document resources in the Dispatch application."""

from datetime import datetime
from collections import defaultdict

from pydantic import field_validator, ValidationInfo
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.messaging.strings import DOCUMENT_DESCRIPTIONS
from dispatch.models import EvergreenBase, NameStr, PrimaryKey
from dispatch.models import ResourceBase, ProjectMixin, ResourceMixin, EvergreenMixin, Pagination
from dispatch.project.models import ProjectRead
from dispatch.search_filter.models import SearchFilterRead
from dispatch.tag.models import TagRead

# Association tables for many to many relationships
assoc_document_filters = Table(
    "assoc_document_filters",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "search_filter_id"),
)

assoc_document_tags = Table(
    "assoc_document_tags",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "tag_id"),
)


class Document(ProjectMixin, ResourceMixin, EvergreenMixin, Base):
    """SQLAlchemy model for document resources."""

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    report_id = Column(Integer, ForeignKey("report.id", ondelete="CASCADE"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE", use_alter=True))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE", use_alter=True))

    filters = relationship("SearchFilter", secondary=assoc_document_filters, backref="documents")

    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))
    tags = relationship(
        "Tag",
        secondary=assoc_document_tags,
        lazy="subquery",
        backref="documents",
    )


# Pydantic models...
class DocumentBase(ResourceBase, EvergreenBase):
    """Base Pydantic model for document resources."""

    description: str | None = None
    name: NameStr
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentCreate(DocumentBase):
    """Pydantic model for creating a document resource."""

    filters: list[SearchFilterRead] | None = []
    project: ProjectRead
    tags: list[TagRead] | None = []


class DocumentUpdate(DocumentBase):
    """Pydantic model for updating a document resource."""

    filters: list[SearchFilterRead] | None = None
    tags: list[TagRead] | None = []

    @field_validator("tags")
    @classmethod
    def find_exclusive(cls, v):
        """Ensures only one exclusive tag per tag type is applied."""
        if v:
            exclusive_tags = defaultdict(list)
            for tag in v:
                if tag.tag_type.exclusive:
                    exclusive_tags[tag.tag_type.id].append(tag)

            for tag_types in exclusive_tags.values():
                if len(tag_types) > 1:
                    raise ValueError(
                        f"Found multiple exclusive tags. Please ensure that only one tag of a given type is applied. Tags: {','.join([t.name for t in v])}"  # noqa: E501
                    )
        return v


class DocumentRead(DocumentBase):
    """Pydantic model for reading a document resource."""

    id: PrimaryKey
    filters: list[SearchFilterRead] | None = []
    project: ProjectRead | None
    tags: list[TagRead] | None = []

    @field_validator("description", mode="before")
    @classmethod
    def set_description(cls, v, info: ValidationInfo):
        """Sets the description for the document resource."""
        if not v:
            resource_type = info.data.get("resource_type")
            return DOCUMENT_DESCRIPTIONS.get(resource_type, "No Description")
        return v


class DocumentPagination(Pagination):
    """Pydantic model for paginated document results."""

    items: list[DocumentRead] = []
